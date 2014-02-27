define [
  "underscore"
  "jquery"
  "bootstrap"
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
], (_, $, $$1, Backbone, Base, HasProperties, PlotContext, bulk_save, ServerUtils, UserContext, PNGPlotView, Layout, Namespace, Workspace, IPythonTerminal) ->

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
        @listenTo(@cdx, 'change:pivot_tables', @render_tabs)
        @listenTo(@cdx, 'change:active_workspace', @render_tabs)

        @render_namespace()
        @render_tabs()

        @listenTo(@cdx, 'change:plotlist', @render_plotlist)
        @listenTo(@cdx, 'change:activeplot', @render_activeplot)

        @render_plotlist()
        @render_activeplot()

    render_namespace: () ->
      workspace = @cdx.get_obj('active_workspace')
      @nsview = new Namespace.View({
        model: @cdx.get_obj('namespace')
        active: workspace?.get("varname")
      })
      @$namespace.html(@nsview.$el)
      @listenTo(@nsview, 'view', @change_workspace)

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
        future = bulk_save([@cdx, workspace, table, source])

      future.done () => @cdx.trigger('change:active_workspace')

    render_plotlist : () ->
      plotlist = @cdx.get_obj('plotlist')
      @plotlistview = new PNGPlotView(
        model : plotlist
        thumb_x : 150
        thumb_y : 150
      )
      @$plotlistholder.html(@plotlistview.$el)
      @listenTo(@plotlistview, 'showplot', @showplot)

    showplot : (ref) ->
      model = @cdx.resolve_ref(ref)
      @cdx.set_obj('activeplot', model)

    render_activeplot : () ->
      activeplot = @cdx.get_obj('activeplot')
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

    render_data_table: () ->
      workspace = @cdx.get_obj('active_workspace')
      if workspace
        data_table = workspace.get_obj("data_table")
        data_table_view = new data_table.default_view({model: data_table})
        @$table.html(data_table_view.$el)
      else
        @$table.empty()

    render_pivot_table_menu: (id) ->
      items = ["Delete", "Duplicate", "Protect", "Hide", "Edit"]
      menu = $('<ul class="dropdown-menu"></ul>')
      menu_items = _.map items, (item) =>
        link = $('<a tabindex="-1" href="javascript://"></a>').text(item)
        link.click (event) => @del_pivot_table(id)
        menu_item = $('<li></li>')
        menu_item.append(link)
      menu.append(menu_items)
      dropdown = $('<span class="dropdown"></span>')
      button = $('<button class="btn btn-link btn-xs dropdown-toggle" data-toggle="dropdown"></button>')
      button.append($('<span class="caret"></span>'))
      dropdown.append([button.dropdown(), menu])

    show_tab: (event) ->
      event.preventDefault()
      $(event.target).tab('show')

    on_show_table_tab: (event) =>
      @render_data_table()

    on_show_pivot_tab: (event) =>
      id = $(event.target).data("pivot-table")
      collection = Base.Collections("PivotTable")
      pivot_table = collection.find((obj) -> obj.get('id') == id)
      pivot_table_view = new pivot_table.default_view({model: pivot_table})
      $("#tab-pivot-" + id).html(pivot_table_view.$el)

    add_pivot_table: (event) =>
      workspace = @cdx.get_obj('active_workspace')

      collection = Base.Collections("PivotTable")
      pivot_table = new collection.model()
      pivot_table.set_obj('source', workspace.get_obj("data_table").get_obj("source"))
      collection.add(pivot_table)

      pivot_tables = workspace.get('pivot_tables')
      updated_pivot_tables = pivot_tables.concat([pivot_table.ref()])
      workspace.set("pivot_tables", updated_pivot_tables, {silent: true})

      bulk_save([workspace, pivot_table]).done () =>
        @cdx.trigger('change:pivot_tables')

    del_pivot_table: (id) =>
      workspace = @cdx.get_obj('active_workspace')
      pivot_tables = workspace.get('pivot_tables')
      updated_pivot_tables = _.filter(pivot_tables, (obj) -> obj.id != id)
      workspace.set('pivot_tables', updated_pivot_tables)
      workspace.save()

    render_tabs: () ->
      workspace = @cdx.get_obj('active_workspace')

      if not workspace
        @$tabsholder.html("<div>Nothing to show</div>")
      else
        @$tabsholder.empty()

        $tabs = $('<ul class="nav nav-tabs"></ul>')
        $table_link = $('<a href="#tab-table">Data Table</a>')
        $table_link.click(@show_tab)
        $table_link.on('show.bs.tab', @on_show_table_tab)
        $table_tab = $('<li></li>').html($table_link)
        $tabs.append($table_tab)

        $tabs_content = $('<div class="tab-content"></div>')
        @$table = $('<div id="tab-table" class="tab-pane"></div>')
        $tabs_content.append(@$table)

        pivot_tables = workspace.get_obj('pivot_tables')
        _.each pivot_tables, (pivot_table) =>
          id = pivot_table.get("id")

          tab_id = "tab-pivot-" + id
          tab_title = pivot_table.get("title")

          $tab_link = $('<a></a>').attr("href", "#" + tab_id).data("pivot-table", id).text(tab_title)
          $tab_link.append(@render_pivot_table_menu(id))
          $tab_link.click(@show_tab)
          $tab_link.on('show.bs.tab', @on_show_pivot_tab)
          $tab = $('<li></li>').html($tab_link)
          $tabs.append($tab)

          $tab_content = $('<div class="tab-pane"></div>').attr("id", tab_id)
          $tabs_content.append($tab_content)

        $add = $('<button class="btn btn-link pull-right cdx-add-tab"><i class="fa fa-plus"></i></button>')
        $add.click(@add_pivot_table)
        $tabs.append($add)

        @$tabsholder.append([$tabs, $tabs_content])
        $table_tab.find("a").tab('show')

    render_layouts: () ->
      @$namespace = $('<div class="namespaceholder hundredpct"></div>')
      @$tabsholder = $('<div class="tabsholder hundredpct"></div>')
      @$plotholder = $('<div class="plotholder hundredpct"></div>')
      @$plotlistholder = $('<div class="plotlistholder hundredpct"></div>')
      @plotbox = new Layout.HBoxView(
        elements : [@$namespace, @$tabsholder, @$plotholder, @$plotlistholder]
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
