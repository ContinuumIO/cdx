$CDX = window.$CDX
$CDX.IPython = {}
$CDX.IPython.inject_plot_client = (docid) ->
  url = "http://#{window.location.host}/bb/"
  code = "import cloudblaze.continuumweb.plot as plot; p = plot.PlotClient('#{docid}', '#{url}')"
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
  IPython.Eventer.on('shellmsg', (header, content)->
    console.log('shellmsg', header.msg_type, header, content)
  )
  IPython.Eventer.on('iopub', (header, content)->
    console.log('iopub', header.msg_type, header, content)
  )
$CDX.IPython.setup_ipython_events()
class Namespace extends Continuum.HasProperties
    type : 'Namespace'
    defaults :
      variables : []
$CDX.IPython.namespace = new Namespace({})
IPython.Eventer.on('iopub:namespace', (header, content) ->
  $CDX.IPython.namespace.set('variables', content.variables)
)

IPython.Notebook.prototype.scroll_to_bottom = () ->
  element = this.element.parent()
  element.animate({scrollTop:element.get(0).scrollHeight}, 0)
