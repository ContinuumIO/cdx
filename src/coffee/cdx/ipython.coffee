define [
  "jquery"
  "CodeMirror"
  "IPython"
], ($, CodeMirror, IPython) ->

  setup_ipython = (container, ws_url) ->
    patch_codemirror()

    IPython.tooltip = new IPython.Tooltip()

    kernel = new IPython.Kernel('/kernels')
    kernel._kernel_started({kernel_id: '1', ws_url: ws_url})

    cell = new IPython.CodeCell(kernel)
    container.append(cell.element)
    cell.select()

    $(document).keydown (event) ->
      key = IPython.utils.keycodes

      if event.which is key.ESC
        # Intercept escape at highest level to avoid closing
        # websocket connection with firefox
        event.preventDefault()
      else if event.which is key.SHIFT
        # ignore shift keydown
        return true
      else if event.which is key.ENTER && event.shiftKey
        cell.execute()
        return false

    $("a#restart").click(() -> kernel.restart())
    $("a#interrupt").click(() -> kernel.interrupt())

    [kernel, cell]

  patch_codemirror = () ->
    # monkey patch CM to be able to syntax highlight cell magics
    # bug reported upstream,
    # see https://github.com/marijnh/CodeMirror2/issues/670
    if not CodeMirror.getMode(1,'text/plain').indent?
      CodeMirror.modes.null = () -> {
        token: (stream) -> stream.skipToEnd()
        indent: () -> 0
      }

    CodeMirror.patchedGetMode = (config, mode) ->
      cmmode = CodeMirror.getMode(config, mode)
      if cmmode.indent == null
        cmmode.indent = () -> 0
      cmmode

  return {
    setup_ipython: setup_ipython
  }
