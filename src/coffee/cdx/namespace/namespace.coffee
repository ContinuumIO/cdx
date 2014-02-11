define [
  "underscore"
  "jquery"
  "jquery_ui/sortable"
  "jquery_ui/accordion"
  "backbone"
  "common/continuum_view"
  "common/has_properties"
], (_, $, $$1, $$2, Backbone, ContinuumView, HasProperties) ->

  class NamespaceView extends ContinuumView.View
    initialize: (options) ->
      super(options)
      @render(options.active)

    events:
      "click .cdx-namespace-header": "click"

    click: (event) =>
      varname = $(event.currentTarget).data('varname')
      @trigger("view", varname)

    delegateEvents: (events) ->
      super(events)
      @listenTo(@model, 'change', @render)

    get_active_index: (activeName) ->
      if activeName?
        for dataset, i in @$accordion.find(".cdx-namespace-header")
          if $(dataset).data("varname") == activeName
            return i

    render: (activeName) ->
      @$accordion = @renderElements()
      @$accordion.accordion({
        header: "> .cdx-namespace-element > .cdx-namespace-header",
        heightStyle: "content",
        active: @get_active_index(activeName),
      }).sortable({
        handle: ".cdx-namespace-header",
        axis: "y",
        distance: 10,
      })
      @$el.html(@$accordion)

    renderElements: () ->
      datasets = @mget('datasets') || {}
      if _.size(datasets) == 0
        $("<div>No datasets</div>")
      else
        @renderDatasets(datasets)

    renderDatasets: (datasets) ->
      $elements = $('<ul class="nav nav-pills nav-stacked"></ul>')

      for name in _.keys(datasets).sort()
        $header = $('<a class="cdx-namespace-header"></a>').data('varname', name).text(name)
        items = ($('<li></li>').text(colname) for colname in datasets[name])
        $columns = $('<ul></ul>').append(items)
        $element = $('<li class="cdx-namespace-element"></li>').append([$header, $columns])
        $elements.append($element)

      $elements

  class Namespace extends HasProperties
    default_view: NamespaceView
    type: "Namespace"
    defaults:
      datasets: []
      name: ""

  class Namespaces extends Backbone.Collection
    model: Namespace

  return {
    Model: Namespace
    Collection: new Namespaces()
    View: NamespaceView
  }
