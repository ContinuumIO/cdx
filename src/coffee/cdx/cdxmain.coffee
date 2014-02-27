define [
  "underscore"
  "jquery"
  "backbone"
  "main"
  "common/base"
  "./cdxapp"
  "./ipython"
  "./data_table"
  "./pivot_table"
  "./remote_data_source"
], (_, $, Backbone, Bokeh, Base, CDXApp, ipython, data_table, pivot_table, remote_data_source) ->

  Bokeh.server_page()

  class CDXRouter extends Backbone.Router
    routes :
      "cdx/:title" : 'main'

    initCode: (arrayserver_port, cdx_addr, title) ->
      """
      import cdx.remotedata.pandasserver as pds; pds.run(#{arrayserver_port})
      from cdx.session import CDXSession
      sess = CDXSession(serverloc='#{cdx_addr}', arrayserver_port=#{arrayserver_port})
      get_ipython().register_post_execute(lambda: sess.cdx.namespace.populate())
      sess.use_doc('#{title}')
      """

    main: (title) ->
      $body = $('body')

      cdx_addr = $body.data('cdx-addr')
      ipython_ws_addr = $body.data('ipython-ws-addr')
      arrayserver_port = $body.data('arrayserver-port')

      callbacks = {
        execute_reply: (content) =>
          console.log(content)
        output: (msg_type, content) =>
          console.log(msg_type, content)
      }

      # XXX: uncomment and remove delay() after switching to IPython 2.0

      #$([IPython.events]).on 'status_started.Kernel', (event, data) =>
      #  code = @initCode(arrayserver_port, cdx_addr, title)
      #  data.kernel.execute(code, callbacks, {silent: false})

      kernel = ipython.init_kernel(ipython_ws_addr)

      _.delay((() =>
          code = @initCode(arrayserver_port, cdx_addr, title)
          kernel.execute(code, callbacks, {silent: false})),
      1000)

      view = new CDXApp.View({title: title, kernel: kernel})
      $('#CDX').html(view.el)

  register_models = () ->
    console.log("register_models")
    Base.locations['RemoteDataSource'] = "cdx/remote_data_source"
    Base.locations['DataTable'] = "cdx/data_table"
    Base.locations['PivotTable'] = "cdx/pivot_table"
    Base.locations['Workspace'] = "cdx/workspace"
    Base.locations['Namespace'] = "cdx/namespace"
    Base.locations['CDX'] = "cdx/cdxapp"

  $(()->
    register_models()
    router = new CDXRouter()
    Backbone.history.start()
  )
