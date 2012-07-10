$CDX = window.$CDX
$CDX.IPython = {}
$CDX.IPython.inject_plot_client = (docid) ->
  url = _.template("http://{{ host }}/bb/", {'host' : window.location.host})
  code = _.template("import cloudblaze.continuumweb.plot as plot; p = plot.PlotClient('{{ docid }}', '{{ url }}')",
    docid : docid
    url : url
  )
  cells = IPython.notebook.cells()
  last_cell = cells[(cells.length - 1)]
  last_cell.set_code(code)
  IPython.notebook.select((cells.length - 1))
  IPython.notebook.execute_selected_cell()

$CDX.IPython.setup_ipython_events = () ->
  IPython.Kernel.prototype.namespace_request = () ->
    content = {}
    msg = @get_msg("namespace_request", content)
    @shell_channel.send(JSON.stringify(msg))
    return msg.header.msg_id
  IPython.Eventer = _.clone(Backbone.Events)
  IPython.Eventer.on('shellmsg:namespace', (header, content)->
    console.log(header, content)
  )

IPython.Notebook.prototype.scroll_to_bottom = () ->
  element = this.element.parent()
  element.animate({scrollTop:element.get(0).scrollHeight}, 0);

