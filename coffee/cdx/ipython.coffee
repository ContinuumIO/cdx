exports.setup_ipython = (ws_url) ->
    patch_codemirror()

    IPython.tooltip = new IPython.Tooltip()

    kernel = new IPython.Kernel('/kernels')
    kernel._kernel_started({kernel_id: '1', ws_url: ws_url})
    thecell = new IPython.CodeCell(kernel)
    $("div#thecell").append(thecell.element)
    window.thecell = thecell
    thecell.code_mirror.setSize("100%", 106)
    # set some example input
    # focus the cell
    thecell.select()

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
            thecell.execute()
            return false

    $("a#restart").click(() -> kernel.restart())
    $("a#interrupt").click(() -> kernel.interrupt())

patch_codemirror = () ->
    # monkey patch CM to be able to syntax highlight cell magics
    # bug reported upstream,
    # see https://github.com/marijnh/CodeMirror2/issues/670
    if not CodeMirror.getMode(1,'text/plain').indent?
        console.log('patching CM for undefined indent')
        CodeMirror.modes.null = () -> {
            token: (stream) -> stream.skipToEnd()
            indent: () -> 0
        }

    CodeMirror.patchedGetMode = (config, mode) ->
        cmmode = CodeMirror.getMode(config, mode)
        if cmmode.indent == null
            console.log("patch mode '#{mode}' on the fly")
            cmmode.indent = () -> 0
        cmmode
