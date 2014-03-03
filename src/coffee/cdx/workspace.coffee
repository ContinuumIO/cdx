define [
  "underscore"
  "jquery"
  "bootstrap"
  "backbone"
  "common/base"
  "common/continuum_view"
  "common/has_properties"
  "common/bulk_save"
], (_, $, $$1, Backbone, Base, ContinuumView, HasProperties, bulk_save) ->

  class WorkspaceView extends ContinuumView.View
    initialize: (options) ->
      super(options)
      @render()

    delegateEvents: (events) ->
      super(events)
      @listenTo(@model, 'change:pivot_tables', @render_tabs)

    render_data_table: () ->
      data_table = @model.get_obj("data_table")
      new data_table.default_view({ model: data_table, el: @$table })

    render_pivot_table_menu: (id) ->
      items = ["Delete", "Duplicate", "Protect", "Hide", "Edit"]
      menu = $('<ul class="dropdown-menu"></ul>')
      menu_items = _.map items, (item) =>
        link = $('<a tabindex="-1"></a>').text(item)
        link.click (event) => @del_pivot_table(id)
        menu_item = $('<li></li>')
        menu_item.append(link)
      menu.append(menu_items)
      dropdown = $('<span class="dropdown"></span>')
      button = $('<button class="btn btn-link btn-xs dropdown-toggle" data-toggle="dropdown"></button>')
      button.append($('<span class="caret"></span>'))
      dropdown.append([button.dropdown(), menu])

    show_tab: (event) =>
      event.preventDefault()
      $(event.target).tab('show')

    on_show_table_tab: (event) =>
      @render_data_table()

    on_show_pivot_tab: (event) =>
      id = $(event.target).data("pivot-table")
      if id?
        collection = Base.Collections("PivotTable")
        pivot_table = collection.find((obj) -> obj.get('id') == id)
        new pivot_table.default_view({ model: pivot_table, el: $("#tab-" + id) })

    add_pivot_table: (event) =>
      collection = Base.Collections("PivotTable")
      pivot_table = new collection.model()
      pivot_table.set_obj('source', @model.get_obj("data_table").get_obj("source"))
      collection.add(pivot_table)

      pivot_tables = @model.get('pivot_tables')
      updated_pivot_tables = pivot_tables.concat([pivot_table.ref()])
      @model.set("pivot_tables", updated_pivot_tables, {silent: true})

      bulk_save([@model, pivot_table]).done () =>
        @model.trigger('change:pivot_tables')

    del_pivot_table: (id) =>
      pivot_tables = @model.get('pivot_tables')
      updated_pivot_tables = _.filter(pivot_tables, (obj) -> obj.id != id)
      @model.set('pivot_tables', updated_pivot_tables)
      @model.save()

    render_tabs: () ->
      $tabs = $('<ul class="nav nav-tabs"></ul>')
      $table_link = $('<a href="#tab-table">Data Table</a>')
      $table_link.click(@show_tab)
      $table_link.on('show.bs.tab', @on_show_table_tab)
      $table_tab = $('<li></li>').html($table_link)
      $tabs.append($table_tab)

      $tabs_content = $('<div class="tab-content"></div>')
      @$table = $('<div id="tab-table" class="tab-pane"></div>')
      $tabs_content.append(@$table)

      pivot_tables = @model.get_obj('pivot_tables')
      _.each pivot_tables, (pivot_table) =>
        id = pivot_table.get("id")

        tab_id = "tab-" + id
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

      @$el.empty()
      @$el.append([$tabs, $tabs_content])

      $table_tab.find("a").tab('show')

    render: () ->
      @render_tabs()

  class Workspace extends HasProperties
    default_view: WorkspaceView
    type: "Workspace"
    defaults:
      varname: null
      data_table: null
      pivot_tables: []
      plots: []
      plot_context: null
      active_tab: 0

  class Workspaces extends Backbone.Collection
    model: Workspace

  return {
    Model: Workspace
    Collection: new Workspaces()
    View: WorkspaceView
  }
