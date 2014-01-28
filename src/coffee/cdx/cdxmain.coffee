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
], (_, $, Backbone, Bokeh, Base, CDXApp, IPython, data_table, pivot_table, remote_data_source) ->

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

    plotCode: () ->
      """
      import pandas as pd
      auto = pd.read_csv('cdx/remotedata/auto-mpg.csv')
      stud = pd.read_csv('csv/student_activities.csv')
      """
      ###
      """
      import pandas as pd; auto = pd.read_csv('cdx/remotedata/auto-mpg.csv')
      sess.cdx.namespace.populate(); sess.plot('weight', 'mpg', 'auto')
      """
      ###

    main : (title) ->
      view = new CDXApp.View(title : title)
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
    console.log("register_models")
    Base.locations['RemoteDataSource'] = "cdx/remote_data_source"
    Base.locations['DataTable'] = "cdx/data_table"
    Base.locations['PivotTable'] = "cdx/pivot_table"
    Base.locations['Namespace'] = "cdx/namespace/namespace"
    Base.locations['CDX'] = "cdx/cdxapp"

  $(()->
    register_models()
    router = new CDXRouter()
    Backbone.history.start()
  )
