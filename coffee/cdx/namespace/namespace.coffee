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

  rowclick : (e) =>
    varname = $(e.currentTarget).attr('varname')
    @trigger("view", varname)

  delegateEvents : (events) ->
    super(events)
    @listenTo(@model, 'change', @render)

  template : require("./namespacetemplate")
  render : () ->
    data = @mget('data')
    metadata = {}
    metadata._varnames = _.keys(data)
    metadata._varnames.sort()
    for own variable, variable_data of data
      metadata[variable] = {}
      metadata[variable]._colnames = _.keys(variable_data)
      metadata[variable]._colnames.sort()
      for own colname, col_data of variable_data
        metadata[variable][colname] = {}
        metadata[variable][colname]._statnames = _.keys(col_data)
        metadata[variable][colname]._statnames.sort()
    html = @template(
      metadata: metadata
      data: data
    )
    @$el.html(html)

class Namespace extends HasProperties
  default_view : NamespaceView
  type : "Namespace"
  defaults :
    namespace : null

class Namespaces extends Backbone.Collection
  model : Namespace

exports.namespaces = new Namespaces
exports.Namespace = Namespace
exports.NamespaceView = NamespaceView