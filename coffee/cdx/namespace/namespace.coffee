ContinuumView = require("../common/continuum_view").ContinuumView
base = require("../base")
HasProperties = require("../base").HasProperties
locations = base.locations

class NamespaceView extends ContinuumView

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