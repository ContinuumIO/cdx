# CDX Coffee Script
#
# This is the main script file for the CDX app.

inject_plot_client = (docid, url) ->
  code = _.template("import cloudblaze.continuumweb.plot as plot; p = plot.PlotClient('{{ docid }}', '{{ url }}')",
    docid : docid
    url : url
  )
  cells = IPython.notebook.cells()
  last_cell = cells[(cells.length - 1)]
  last_cell.set_code(code)
  IPython.notebook.select((cells.length - 1))
  IPython.notebook.execute_selected_cell()  

window.call_inject =   () ->
  targeturl = _.template("http://{{ host }}/bb/", {'host' : window.location.host})
  inject_plot_client(window.topic, targeturl)


