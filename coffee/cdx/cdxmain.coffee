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
    ipython_ws_addr = $('body').data('ipython-ws-addr')
    window.setup_ipython(ipython_ws_addr)
    cdx_addr = $('body').data('cdx-addr')
    code = "import cdx.remotedata.pandasserver as pds; pds.run()\n"
    code += "from cdx.session import CDXSession; sess = CDXSession(serverloc='#{cdx_addr}')\n"
    code += "sess.use_doc('#{title}')\n"

    thecell.set_text(code)
    #hacky...
    _.delay((() => thecell.execute()), 1000)

$(()->
  register_models()
  router = new CDXRouter()
  Backbone.history.start()
)


register_models = () ->
  locations['Namespace'] = ["./namespace/namespace", "namespaces"]
  locations['CDX'] = ["./cdxapp", "cdxs"]
