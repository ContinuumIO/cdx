define [
  "underscore"
  "jquery"
  "jquery_terminal"
  "backbone"
], (_, $, $$1, Backbone) ->

  class IPythonTerminalView extends Backbone.View
    initialize: (kernel, options) ->
      super(options)
      @kernel = kernel
      @render()

    render: () ->
      @$el.addClass('cdx-terminal')
      @$el.terminal(@evaluate_handler, {
        name: "ipython",
        greetings: false,
        prompt: '>>> ',
        tabcompletion: true,
        completion: @complete_handler,
      })

    evaluate_handler: (code, term) =>
      term.pause()

      display = (output) =>
        if output? and output.length > 0
          output = output + '\n' if output[output.length-1] != '\n'
          term.echo(output)

      callbacks = {
        execute_reply: (content) =>
          for data in content.payload
            display(data.text)
          term.resume()
        output: (msg_type, content) =>
          output = switch msg_type
            when 'pyout', 'display_data'
              content.data['text/plain']
            when 'pyerr'
              content.traceback?.join("\n")
            when 'stream'
              content.data
          display(output)
      }

      msg_id = @kernel.execute(code, callbacks, {silent: false})
      console.log("CDX -> IPython (evaluate:#{msg_id})")

      return

    complete_handler: (term, code, complete) =>
      term.pause()

      callbacks = {
        complete_reply: (content) =>
          complete(content.matches)
          term.resume()
      }

      msg_id = @kernel.complete(code, code.length, callbacks)
      console.log("CDX -> IPython (complete:#{msg_id})")

      return

  return {
    View: IPythonTerminalView,
  }
