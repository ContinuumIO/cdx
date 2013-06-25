base = require("./base")
locations = base.locations
CDXApp = require("./cdxapp").CDXApp
class CDXRouter extends Backbone.Router
  routes :
    "cdx/:title" : 'main'
  main : (title) ->
    view = new CDXApp(title : title)
    $('#CDX').append(view.el)
    window.view = view
    ipython_port = Number($('body').data('ipython-port'))
    window.setup_ipython("ws://localhost:#{ipython_port}")
$(()->
  register_models()
  router = new CDXRouter()
  Backbone.history.start()
)


register_models = () ->
  locations['Namespace'] = ["./namespace/namespace", "namespaces"]
  locations['CDX'] = ["./cdxapp", "cdxs"]
