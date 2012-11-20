if not window.$CDX
  window.$CDX = {}
$CDX = window.$CDX
if not $CDX.Models
  $CDX.Models = {}
if not $CDX.Collections
  $CDX.Collections = {}
if not $CDX.Views
  $CDX.Views = {}

$CDX = window.$CDX
$CDX.Deferreds = {}
$CDX.Promises = {}
$CDX.Deferreds._doc_loaded = $.Deferred()
$CDX.Promises.doc_loaded = $CDX.Deferreds._doc_loaded.promise()
Continuum.HasProperties.prototype.sync = Backbone.sync

$CDX.utility =
  load_default_document : () ->
    user = $.get('/cdx/userinfo/', {}, (data) ->
      console.log(data)
      docs = JSON.parse(data)['docs']
      console.log(docs)
      $CDX.utility.instantiate_doc(docs[0])
    )
  instantiate_doc : (docid) ->
    $.get("/cdx/cdxinfo/#{docid}", {}, (data) ->
      data = JSON.parse(data)
      $CDX.plot_context_ref = data['plot_context_ref']
      $CDX.docid = data['docid'] # in case the server returns a different docid
      Continuum.docid = $CDX.docid
      #hack
      docid = $CDX.docid
      $('.resetlink').click(()->
        $.get("/cdx/bb/#{docid}/reset")
      )
      $CDX.all_models = data['all_models']
      Continuum.load_models($CDX.all_models)

      $CDX.socket = Continuum.submodels($CDX.ws_conn_string,
        $CDX.docid,
        data.apikey)
      $CDX.apikey = data['apikey']
      console.log("from cdx import plot")
      url = window.location.origin
      console.log("p = plot.PlotClient('#{docid}', '#{url}', '#{$CDX.apikey}')")
      $CDX.utility.render_plots()
      $CDX.Deferreds._doc_loaded.resolve($CDX.docid)

    )
  render_plots : () ->
    plotcontext = Continuum.resolve_ref(
      $CDX.plot_context_ref['collections'],
      $CDX.plot_context_ref['type'],
      $CDX.plot_context_ref['id']
    )
    plotcontextview = new plotcontext.default_view(
      model : plotcontext,
      render_loop: true
    )
    $CDX.plotcontext = plotcontext
    $CDX.plotcontextview = plotcontextview
    $CDX.plotcontextview.render()
