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
  "./namespace"
  "./workspace"
  "./ipython_terminal"
], (_, $, Backbone, Base, HasProperties, PlotContext, bulk_save, ServerUtils, UserContext, PNGPlotView, Layout, Namespace, Workspace, IPythonTerminal) ->

  Base.Config.ws_conn_string = "ws://#{window.location.host}/bokeh/sub"

  class CDX extends HasProperties
    default_view : Backbone.View
    type : 'CDX'
    defaults :
      namespace : null
      workspaces : []
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
      @kernel = options.kernel
      @render_layouts()
      @init_cdx(title)

    init_cdx: (title) ->
      @wswrapper = ServerUtils.utility.make_websocket()

      doc = new UserContext.Doc(title : title)
      doc.load(true).done (data) =>
        @cdx = Base.Collections('CDX').first()
        if not @cdx
          coll = Base.Collections('CDX')
          @cdx = new coll.model({doc : doc.id})
          coll.add(@cdx)
          pc = doc.get_obj('plot_context')
          children = _.clone(pc.get('children'))
          children.push(@cdx.ref())
          pc.set('children', children)
          @cdx.set_obj('plotcontext', pc)

        ns = @cdx.get_obj('namespace')
        if not ns
          coll = Base.Collections('Namespace')
          ns = new coll.model(doc : doc.id)
          coll.add(ns)
          @cdx.set_obj('namespace', ns)

        plotlist = @cdx.get_obj('plotlist')
        if not plotlist
          coll = Base.Collections('PlotList')
          plotlist = new coll.model(doc : doc.id)
          coll.add(plotlist)
          @cdx.set_obj('plotlist', plotlist)

        bulk_save([@cdx, doc.get_obj('plot_context'), ns, plotlist])

        @listenTo(@cdx, 'change:namespace', @render_namespace)
        @listenTo(@cdx, 'change:active_workspace', @render_workspace)

        @render_namespace()
        @render_workspace()

        @listenTo(@cdx, 'change:plotlist', @render_plotlist)
        @listenTo(@cdx, 'change:activeplot', @render_activeplot)

        @render_plotlist()
        @render_activeplot()

    render_namespace: () ->
      workspace = @cdx.get_obj('active_workspace')
      @namespace_view = new Namespace.View({
        active: workspace?.get("varname")
        model: @cdx.get_obj('namespace')
        el: @$namespace
      })
      @listenTo(@namespace_view, 'activate', @change_workspace)

    render_workspace: () ->
      workspace = @cdx.get_obj('active_workspace')
      if workspace?
        new workspace.default_view({ model: workspace, el: @$workspace })
      else
        @$workspace.html("<div>Nothing to show</div>")

    conninfo :
      host : 'localhost'
      port : 10020

    get_source: (varname) ->
      collection = Base.Collections("RemoteDataSource")
      source = collection.find((obj) -> obj.get('varname') == varname)

      if not source?
        source = new collection.model({
          host: @conninfo.host,
          port: @conninfo.port,
          varname: varname,
        })
        collection.add(source)

      source

    change_workspace: (varname) ->
      active_workspace = @cdx.get_obj('active_workspace')

      if not active_workspace || active_workspace.get('varname') != varname
        workspaces = Base.Collections("Workspace")
        workspace = workspaces.find((obj) -> obj.get('varname') == varname)

        # XXX: use silent=true with conjunction with bulk_save()
        set_active_workspace = (workspace) =>
          # @cdx.set_obj('active_workspace', workspace)
          @cdx.set({'active_workspace': workspace.ref()}, {'silent': true})

        if workspace?
          set_active_workspace(workspace)
          future = @cdx.save()
        else
          source = @get_source(varname)

          tables = Base.Collections("DataTable")
          table = new tables.model()
          table.set_obj('source', source)
          tables.add(table)

          workspace = new workspaces.model()
          workspace.set('varname', varname)
          workspace.set_obj('data_table', table)
          workspaces.add(workspace)

          set_active_workspace(workspace)
          @cdx.set('workspaces', @cdx.get('workspaces').concat([workspace.ref()]), {'silent': true})

          future = bulk_save([@cdx, workspace, table, source])

        future.done () => @cdx.trigger('change:active_workspace')

    render_plotlist : () ->
      plotlist = @cdx.get_obj('plotlist')
      @plotlist_view = new PNGPlotView(
        model: plotlist
        el: @$plotlist
        thumb_x: 150
        thumb_y: 150
      )
      @listenTo(@plotlist_view, 'showplot', @showplot)

    showplot : (ref) ->
      model = @cdx.resolve_ref(ref)
      @cdx.set_obj('activeplot', model)

    render_activeplot : () ->
      activeplot = @cdx.get_obj('activeplot')
      if activeplot
        width = @$plot.width()
        height = @$plot.height()
        ratio1 = width / activeplot.get('outer_width')
        ratio2 = height / activeplot.get('outer_height')
        ratio = _.min([ratio1, ratio2])
        newwidth = activeplot.get('outer_width') * ratio * 0.9
        newheight = activeplot.get('outer_height') * ratio * 0.9
        new activeplot.default_view({
          model : activeplot
          el : @$plot
          canvas_height : newwidth
          canvas_width : newheight
          outer_height : newwidth
          outer_width : newheight
        })
      else
        @$plot.empty()

    render_layouts: () ->
      @$namespace = $('<div class="cdx-namespace-holder hundredpct"></div>')
      @$workspace = $('<div class="cdx-tabs-holder hundredpct"></div>')
      @$plot = $('<div class="cdx-plot-holder hundredpct"></div>')
      @$plotlist = $('<div class="cdx-plotlist-holder hundredpct"></div>')
      @plotbox = new Layout.HBoxView(
        elements : [@$namespace, @$workspace, @$plot, @$plotlist]
        height : '100%',
        width : '100%',
      )
      @plotbox.sizes = [15, 40, 35, 10]
      @plotbox.set_sizes()
      @$terminal = new IPythonTerminal.View(@kernel)
      @iplayout = new Layout.HBoxView(
        elements : [@$terminal.$el]
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
