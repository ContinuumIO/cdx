ContinuumView = require("../common/continuum_view").ContinuumView
base = require("../base")
HasProperties = require("../base").HasProperties
locations = base.locations
pandas = require("../pandas/pandas")

class NamespaceView extends ContinuumView
  initialize: (options) ->
    super(options)
    @render()

  events:
    "click .namespace-dataset": "click"

  click: (event) =>
    varname = $(event.currentTarget).data('varname')
    @trigger("view", varname)

  delegateEvents: (events) ->
    super(events)
    @listenTo(@model, 'change', @render)

  template: require("./namespacetemplate")

  render: () ->
    div = $("<div/>")
    @$el.html(div)
    @renderElements(div)
    div.accordion({
        header: "> .namespace-element > .namespace-dataset",
        heightStyle: "content",
    }).sortable({
        handle: ".namespace-dataset",
        axis: "y",
    })

  renderElements: (el) ->
    data = @mget('data') || {}
    html =
        if _.size(data) == 0
            $("<div>No datasets</div>")
        else
            @template({data: data})
     el.html(html)

class Namespace extends HasProperties
  default_view : NamespaceView
  type : "Namespace"
  defaults :
    namespace : {}

class Namespaces extends Backbone.Collection
  model : Namespace

exports.NamespaceView = NamespaceView
exports.Namespace = Namespace
exports.namespaces = new Namespaces
