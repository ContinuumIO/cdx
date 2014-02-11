define [
  "underscore"
  "jquery"
  "jquery_ui/sortable"
  "jquery_ui/accordion"
  "backbone"
  "common/continuum_view"
  "common/has_properties"
  "./namespacetemplate"
], (_, $, $$1, $$2, Backbone, ContinuumView, HasProperties, NamespaceTemplate) ->

  class NamespaceView extends ContinuumView.View
    initialize: (options) ->
      super(options)
      @render(options.active)

    events:
      "click .namespace-dataset": "click"

    click: (event) =>
      varname = $(event.currentTarget).data('varname')
      @trigger("view", varname)

    delegateEvents: (events) ->
      super(events)
      @listenTo(@model, 'change', @render)

    get_active_index: (activeName) ->
      if activeName?
        for dataset, i in @$accordion.find(".namespace-dataset")
          if $(dataset).data("varname") == activeName
            return i

    template: NamespaceTemplate

    render: (activeName) ->
      @$accordion = $("<div/>")
      @renderElements(@$accordion)
      @$accordion.accordion({
        header: "> .namespace-element > .namespace-dataset",
        heightStyle: "content",
        active: @get_active_index(activeName),
      }).sortable({
        handle: ".namespace-dataset",
        axis: "y",
      })
      @$el.html(@$accordion)

    renderElements: (el) ->
      datasets = @mget('datasets') || {}
      html =
        if _.size(datasets) == 0
          $("<div>No datasets</div>")
        else
          @template({data: datasets})
       el.html(html)

  class Namespace extends HasProperties
    default_view: NamespaceView
    type: "Namespace"
    defaults:
      namespace: {}

  class Namespaces extends Backbone.Collection
    model : Namespace

  return {
    Model: Namespace
    Collection: new Namespaces()
    View: NamespaceView
  }
