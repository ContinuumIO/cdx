define [
  "server/usercontext/usercontext"
], (UserContext) ->

  class DocView extends UserContext.DocView
    render_init : () ->
      'pass'
    render : () ->
      plot_context = @model.get_obj('plot_context')
      @plot_context_view = new plot_context.default_view(
        model : plot_context
      )
      @$el.append(@plot_context_view.el)
      return true

  return {
    DocView: DocView
  }
