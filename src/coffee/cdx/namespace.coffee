define [
  "underscore"
  "jquery"
  "bootstrap"
  "backbone"
  "common/continuum_view"
  "common/has_properties"
], (_, $, Bootstrap, Backbone, ContinuumView, HasProperties) ->

  class NamespaceView extends ContinuumView.View
    initialize: (options) ->
      super(options)
      @render(options.active)

    delegateEvents: (events) ->
      super(events)
      @listenTo(@model, 'change', @render)

    activateDataset: (event) =>
      name = $(event.target).data('name')
      @trigger("activate", name)

    renderDataset: (name, dataset, active) ->
      el = $("""
        <div class="panel panel-default">
          <div class="panel-heading">
            <h4 class="panel-title">
              <a data-toggle="collapse" data-parent="#namespace-accordion" href="#namespace-#{name}">
                #{name}
              </a>
            </h4>
          </div>
          <div id="namespace-#{name}" data-name="#{name}" class="panel-collapse collapse">
            <div class="panel-body">
              <ul></ul>
            </div>
          </div>
        </div>
        """)
      columns = ($('<li></li>').text(colname) for colname in dataset)
      el.find(".panel-body > ul").html(columns)
      if name == active then el.find(".panel-collapse").addClass("in")
      el

    renderDatasets: (accordion, datasets, active) ->
      for name in _.keys(datasets).sort()
        accordion.append(@renderDataset(name, datasets[name], active))

    render: (active) ->
      datasets = @mget('datasets') || {}

      if _.size(datasets) == 0
        @$el.html("<div>No datasets</div>")
      else
        accordion = $('<div id="namespace-accordion" class="panel-group"></div>')
        @renderDatasets(accordion, datasets, active)
        accordion.on("show.bs.collapse", @activateDataset)
        @$el.html(accordion)

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
