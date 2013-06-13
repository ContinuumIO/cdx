ContinuumView = require("../common/continuum_view").ContinuumView
base = require("../base")
HasProperties = require("../base").HasProperties
locations = base.locations

class NamespaceView extends ContinuumView
  initialize : (options) ->
    super(options)
    @render()
  template : require("./namespacetemplate")
  render : () ->
    data = @mget('data')
    varnames = _.keys(data)
    varnames.sort()
    fields = {}
    metrics = {}
    for own colname, col of data
      for own variable, variable_metrics of col
        fields[variable] = _.keys(variable_metrics)
        fields[variable].sort()
        metrics[variable] = variable_metrics
    html = @template(
      varnames : varnames
      fields : fields
      metrics : metrics
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