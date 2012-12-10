$CDX.ws_conn_string = "ws://#{window.location.host}/cdx/sub"
$(()->
  $CDX.utility.load_default_document()
)
$.when($CDX.Promises.doc_loaded).then(()->
  $('#PlotPane').empty().append($CDX.plotcontextview.el)
)

$CDX.utility.render_plots = () ->
  plotcontext = Continuum.resolve_ref(
    $CDX.plot_context_ref['collections'],
    $CDX.plot_context_ref['type'],
    $CDX.plot_context_ref['id']
  )
  # plotcontextview = new $CDX.Views.CDXPlotContextViewWithMaximized(
  #   model : plotcontext,
  # )
  plotcontextview = new $CDX.Views.CDXPlotContextView(
    model : plotcontext,
  )

  $CDX.plotcontext = plotcontext
  $CDX.plotcontextview = plotcontextview
  $CDX.plotcontextview.render()
