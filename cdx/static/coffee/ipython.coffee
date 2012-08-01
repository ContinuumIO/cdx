$CDX = window.$CDX
$CDX.IPython = {}


execute_code =  (code) ->
  cells = IPython.notebook.cells()
  last_cell = cells[(cells.length - 1)]
  last_cell.set_code(code)
  IPython.notebook.select((cells.length - 1))
  IPython.notebook.execute_selected_cell()

$CDX.IPython.execute_code = execute_code
$CDX.IPython.inject_plot_client = () ->
  code = "import cloudblaze.continuumweb.interactive as interactive"
  execute_code(code)
  url = document.URL
  code = "clients = interactive.CDXClient('#{url}')"
  execute_code(code)

$CDX.IPython.setup_ipython_events = () ->
  IPython.Kernel.prototype.namespace_request = () ->
    content = {}
    msg = @get_msg("namespace_request", content)
    @shell_channel.send(JSON.stringify(msg))
    return msg.header.msg_id
  IPython.Eventer = _.clone(Backbone.Events)

$CDX.IPython.setup_ipython_events()
class $CDX.Models.Namespace extends Continuum.HasProperties
    type : 'Namespace'
    defaults :
      variables : []
      newvars : []
    get_vars : (varnames) ->
      indexed = {}
      for varentry in @get('variables')
        indexed[varentry.name] = varentry
      return (indexed[x] for x in varnames when indexed[x])

$CDX.IPython.namespace = new $CDX.Models.Namespace({})
IPython.Eventer.on('iopub:namespace', (header, content) ->
  #console.log("iopub namespace", header, content)
  $CDX.IPython.namespace.set(
    'variables' : content.variables,
    'newvars': content.newvars
  )
)


IPython.Notebook.prototype.scroll_to_bottom = () ->
  element = this.element.parent()
  element.animate({scrollTop:element.get(0).scrollHeight}, 0)

$CDX.IPython.suggest_variable_name = (target) ->
  target = target.replace(/\W|^(?=\d)|/ , '_')
  target = target.replace(/\//g, '_')
  target = target.replace(/\./g, '_')
  target = target.replace(/-/g, '_')
  # Trim the name down to only include the last two parts.
  urlParts = target.split('_')
  if (urlParts.length >= 2)
    newTarget = urlParts[urlParts.length - 2] + '_' + urlParts[urlParts.length - 1]
    target = newTarget
  target = 'da_' + target
  varnames = {}
  for variable in $CDX.IPython.namespace.get('variables')
    varnames[variable.name] = true
  candidate = target
  counter = 1
  while varnames[candidate]
    candidate = target + String(counter)
    counter += 1
  return candidate
