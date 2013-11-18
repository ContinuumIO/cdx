define [
  "underscore"
  "jquery"
  "backbone"
  "common/base"
  "./cdxapp"
  "./ipython"
], (_, $, Backbone, Base, CDXApp, IPython) ->

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
      view = new CDXApp.CDXApp(title : title)
      $('#CDX').append(view.el)
      window.view = view
      view.layout.sizes = [100,0]
      view.layout.set_sizes()
      view.plotbox.sizes = [0,0,80,20]
      view.plotbox.set_sizes()

    initCode: (arrayserver_port, cdx_addr, title) ->
      """
      import cdx.remotedata.pandasserver as pds; pds.run(#{arrayserver_port})
      from cdx.session import CDXSession
      sess = CDXSession(serverloc='#{cdx_addr}', arrayserver_port=#{arrayserver_port})
      get_ipython().register_post_execute(lambda: sess.cdx.namespace.populate())
      sess.use_doc('#{title}')
      """

    plotCode: () ->
      """
      import pandas as pd; auto = pd.read_csv('cdx/remotedata/auto-mpg.csv')
      sess.cdx.namespace.populate(); sess.plot('weight', 'mpg', 'auto')
      """

    main : (title) ->
      #hacky
      cdxlink = window.location.href.replace("#justplots", "#cdx")
      plotlink = window.location.href.replace("#cdx", "#justplots")
      $('.justcdx').attr('href', cdxlink)
      $('.justplots').attr('href', plotlink)
      view = new CDXApp.CDXApp(title : title)
      $('#CDX').append(view.el)
      window.view = view
      ipython_ws_addr = $('body').data('ipython-ws-addr')

      [kernel, cell] = IPython.setup_ipython($("div#thecell"), ipython_ws_addr)
      cdx_addr = $('body').data('cdx-addr')
      arrayserver_port = $('body').data('arrayserver-port')

      _.delay((() =>
          code = @initCode(arrayserver_port, cdx_addr, title)
          kernel.execute(code)),
      1000) # XXX: otherwise throws InvalidStateError 11, why?

      cell.set_text(@plotCode())

  register_models = () ->
    Base.locations['Namespace'] = ["./namespace/namespace", "namespaces"]
    Base.locations['CDX'] = ["./cdxapp", "cdxs"]

  $(()->
    register_models()
    router = new CDXRouter()
    Backbone.history.start()
  )
