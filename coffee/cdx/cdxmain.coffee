base = require("./base")
layout = require("./layout/index")
locations = base.locations
CDXApp = require("./cdxapp").CDXApp
class CDXRouter extends Backbone.Router
  routes :
    "cdx/:title" : 'main'
    "justplots/:title" : 'justplots'

  justplots : (title) ->
    #hacky
    cdxlink = window.location.href.replace("#justplots", "#cdx")
    plotlink = window.location.href.replace("#cdx", "#justplots")
    $('.justcdx').attr('href', cdxlink)
    $('.justplots').attr('href', plotlink)
    view = new CDXApp(title : title)
    $('#CDX').append(view.el)
    window.view = view
    view.layout.sizes = [100,0]
    view.layout.set_sizes()
    view.plotbox.sizes = [0,0,80,20]
    view.plotbox.set_sizes()

  main : (title) ->
    #hacky
    cdxlink = window.location.href.replace("#justplots", "#cdx")
    plotlink = window.location.href.replace("#cdx", "#justplots")
    $('.justcdx').attr('href', cdxlink)
    $('.justplots').attr('href', plotlink)
    view = new CDXApp(title : title)
    $('#CDX').append(view.el)
    window.view = view
    ipython_ws_addr = $('body').data('ipython-ws-addr')
    window.setup_ipython(ipython_ws_addr)
    cdx_addr = $('body').data('cdx-addr')
    arrayserver_port = $('body').data('arrayserver-port')
    code  = "import cdx.remotedata.pandasserver as pds; pds.run(#{arrayserver_port})\n"
    code += "from cdx.session import CDXSession\n"
    code += "sess = CDXSession(serverloc='#{cdx_addr}', arrayserver_port=#{arrayserver_port})\n"
    code += "sess.use_doc('#{title}')\n"
    code += "import pandas as pd; auto = pd.read_csv('cdx/remotedata/auto-mpg.csv')\n"
    code += "sess.cdx.namespace.populate(); sess.plot('weight', 'mpg', 'auto')\n"

    thecell.set_text(code)
    #hacky...
    _.delay((() => thecell.execute()), 1000)
    view.split_ipython()

    # hide scrollbars from ipython console
    $('#thecell').parent().css('overflow', 'hidden')


$(()->
  register_models()
  router = new CDXRouter()
  Backbone.history.start()
)


register_models = () ->
  locations['Namespace'] = ["./namespace/namespace", "namespaces"]
  locations['CDX'] = ["./cdxapp", "cdxs"]
