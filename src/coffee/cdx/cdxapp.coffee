define [
  "underscore"
  "jquery"
  "backbone"
  "common/base"
  "common/has_properties"
  "common/plot_context"
  "common/bulk_save"
  "server/serverutils"
  "server/usercontext/usercontext"
  "./pngplotview"
  "./layout/index"
  "./namespace/namespace"
], (_, $, Backbone, Base, HasProperties, PlotContext, BulkSave, ServerUtils, UserContext, PNGPlotView, Layout, Namespace) ->

  Base.Config.ws_conn_string = "ws://#{window.location.host}/bokeh/sub"

  class CDX extends HasProperties
    default_view : Backbone.View
    type : 'CDX'
    defaults :
      namespace : null
      activetable : null
      activepivot : null
      activeplot : null
      plotcontext : null

  class CDXs extends Backbone.Collection
    model : CDX

  class CDXApp extends Backbone.View
    attributes :
      class : 'cdxmain'

    delegateEvents : (events) ->
      super(events)
    initialize : (options) ->
      title = options.title
      @render_layouts()
      @init_bokeh(title)

    init_bokeh : (title) ->
      wswrapper = ServerUtils.utility.make_websocket()
      doc = new UserContext.Doc(title : title)
      load = doc.load(true)
      load.done((data) =>
        cdx = Base.Collections('CDX').first()
        if not cdx
          coll = Base.Collections('CDX')
          cdx = new coll.model(doc : doc.id)
          coll.add(cdx)
          pc = doc.get_obj('plot_context')
          children = _.clone(pc.get('children'))
          children.push(cdx.ref())
          pc.set('children', children)
          cdx.set_obj('plotcontext', pc)
        ns = cdx.get_obj('namespace')
        if not ns
          coll = Base.Collections('Namespace')
          ns = new coll.model(doc : doc.id)
          coll.add(ns)
          cdx.set_obj('namespace', ns)
        plotlist = cdx.get_obj('plotlist')
        if not plotlist
          coll = Base.Collections('PlotList')
          plotlist = new coll.model(doc : doc.id)
          coll.add(plotlist)
          cdx.set_obj('plotlist', plotlist)
        BulkSave([cdx, doc.get_obj('plot_context'), ns, plotlist])
        @cdxmodel = cdx
        @listenTo(@cdxmodel, 'change:activetable', @render_activetable)
        @listenTo(@cdxmodel, 'change:activepivot', @render_activepivot)
        @listenTo(@cdxmodel, 'change:namespace', @render_namespace)
        @listenTo(@cdxmodel, 'change:plotlist', @render_plotlist)
        @listenTo(@cdxmodel, 'change:activeplot', @render_activeplot)
        @render_namespace()
        @render_plotlist()
        @render_activetable()
        @render_activepivot()
        @render_activeplot()
      )

      @wswrapper = wswrapper

    render_namespace: () ->
      activetable = @cdxmodel.get_obj('activetable')
      @nsview = new Namespace.View({
        model: @cdxmodel.get_obj('namespace')
        active: activetable?.get_obj("source").get("varname")
      })
      @$namespace.html(@nsview.$el)
      @listenTo(@nsview, 'view', @make_table)

    conninfo :
      host : 'localhost'
      port : 10020

    make_table : (varname) ->
      coll = Base.Collections("RemoteDataSource")
      remotedata = coll.find((obj) -> obj.get('varname') == varname)
      if not remotedata?
        remotedata = new coll.model({
          host: @conninfo.host
          port: @conninfo.port
          varname: varname
        })
        coll.add(remotedata)

      tables = Base.Collections("DataTable")
      table = new tables.model()
      table.set_obj('source', remotedata)
      tables.add(table)

      pivots = Base.Collections("Pivot")
      pivot = new pivots.model()
      pivot.set_obj('source', remotedata)
      pivots.add(pivot)

      # XXX: doesn't work if set simultaneously
      @cdxmodel.set({'activetable': table.ref()}, {'silent': true})
      @cdxmodel.set({'activepivot': pivot.ref()}, {'silent': true})

      result = BulkSave([@cdxmodel, table, pivot, remotedata])
      result.done(() =>
        @cdxmodel.trigger('change:activetable')
        @cdxmodel.trigger('change:activepivot')
      )

    render_plotlist : () ->
      plotlist = @cdxmodel.get_obj('plotlist')
      @plotlistview = new PNGPlotView(
        model : plotlist
        thumb_x : 150
        thumb_y : 150
      )
      @$plotlistholder.html(@plotlistview.$el)
      @listenTo(@plotlistview, 'showplot', @showplot)

    showplot : (ref) ->
      model = @cdxmodel.resolve_ref(ref)
      @cdxmodel.set_obj('activeplot', model)

    render_activeplot : () ->
      activeplot = @cdxmodel.get_obj('activeplot')
      if activeplot
        width = @$plotholder.width()
        height = @$plotholder.height()
        ratio1 = width / activeplot.get('outer_width')
        ratio2 = height / activeplot.get('outer_height')
        ratio = _.min([ratio1, ratio2])
        newwidth = activeplot.get('outer_width') * ratio * 0.9
        newheight = activeplot.get('outer_height') * ratio * 0.9
        view = new activeplot.default_view(
          model : activeplot
          canvas_height : newwidth
          canvas_width : newheight
          outer_height : newwidth
          outer_width : newheight
        )
        @activeplotview = view
        @$plotholder.html('').append(view.$el)
      else
        @$plotholder.html('')

    render_activetable: () ->
      activetable = @cdxmodel.get_obj('activetable')
      if activetable
        activetableview = new activetable.default_view({model: activetable})
        @$table.html(activetableview.$el)
      else
        @$table.empty()

    render_activepivot: () ->
      activepivot = @cdxmodel.get_obj('activepivot')
      if activepivot
        activepivotview = new activepivot.default_view({model: activepivot})
        @$pivot.html(activepivotview.$el)
      else
        @$pivot.empty()

    show_tab: (event) ->
      event.preventDefault()
      $(event.target).tab('show')

    render_tabs: () ->
      $tabs = $('<ul class="nav nav-tabs"></ul>')
      $table_tab = $('<li><a href="#tab-table">Table</a></li>').addClass('active')
      $pivot_tab = $('<li><a href="#tab-pivot">Pivot</a></li>')
      $table_tab.click(@show_tab)
      $pivot_tab.click(@show_tab)
      $tabs.append([$table_tab, $pivot_tab])
      $tabs_content = $('<div class="tab-content"></div>')
      @$table = $('<div id="tab-table" class="tab-pane"></div>').addClass('active')
      @$pivot = $('<div id="tab-pivot" class="tab-pane"></div>')
      $tabs_content.append([@$table, @$pivot])
      @$tabsholder.html($tabs).append($tabs_content)

    render_layouts: () ->
      @$namespace = $('<div class="namespaceholder hundredpct"></div>')
      @$tabsholder = $('<div class="tabsholder hundredpct"></div>')
      @$plotholder = $('<div class="plotholder hundredpct"></div>')
      @$plotlistholder = $('<div class="plotlistholder hundredpct"></div>')
      @render_tabs()
      @plotbox = new Layout.HBoxView(
        elements : [@$namespace, @$tabsholder, @$plotholder, @$plotlistholder]
        height : '100%',
        width : '100%',
      )
      @plotbox.sizes = [15, 55, 20, 10]
      @plotbox.set_sizes()
      @$ipcell = $('<div id="thecell" class="hundredpct"></div>')
      @$ipoutput = $("<div class='ipoutput'></div>")
      @iplayout = new Layout.HBoxView(
        elements : [@$ipcell, @$ipoutput]
        height : '100%'
        width : '100%'
      )
      @layout = new Layout.VBoxView(
        elements : [@plotbox.$el, @iplayout.$el]
        height : '100%'
        width : '100%'
      )
      @layout.sizes = [80,20]
      @layout.set_sizes()
      @$el.append(@layout.el)

  return {
    Model: CDX
    Collection: new CDXs()
    View: CDXApp
  }
