ContinuumView = require("../common/continuum_view").ContinuumView
base = require("../base")
HasProperties = require("../base").HasProperties
locations = base.locations
pandas = require("../pandas/pandas")

class NamespaceView extends ContinuumView
  initialize : (options) ->
    super(options)
    @render()
  events :
    "click .namespace-row" : "rowclick"

  rowclick : (event) =>
    varname = $(event.currentTarget).data('varname')
    @trigger("view", varname)

  delegateEvents : (events) ->
    super(events)
    @listenTo(@model, 'change', @render)

  template : require("./namespacetemplate")
  render : () ->
    data = @mget('data') || {}
    html = @template(data: data)
    @$el.html(html)

class Namespace extends HasProperties
  default_view : NamespaceView
  type : "Namespace"
  defaults :
    namespace : {}

class Namespaces extends Backbone.Collection
  model : Namespace

exports.namespaces = new Namespaces
exports.Namespace = Namespace
exports.NamespaceView = NamespaceView
