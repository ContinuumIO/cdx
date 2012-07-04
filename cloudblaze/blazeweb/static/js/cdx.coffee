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

window.call_inject =   (docid) ->
  targeturl = _.template("http://{{ host }}/bb/", {'host' : window.location.host})
  inject_plot_client(docid, targeturl)


$(() ->
  WorkspaceRouter = Backbone.Router.extend({
    routes: {
      "cdx" : "load_default_document",
      "cdx/:docid":                 "load_doc",     #help
      "cdx/:docid/viz":             "load_doc_viz",     #help
      "module/help2":                 "help2",     #help
      "module/search/:query":        "search",   #search/kiwis
      "module/search/:query/p:page": "search",   #search/kiwis/p7
    },
    load_default_document : () ->
      user = $.get('/userinfo/', {}, (data) ->
        docs = JSON.parse(data)['docs']
        console.log('URL', "cdx/#{docs[0]}")
        $CDX.router.navigate("cdx/#{docs[0]}", {trigger : true}))
    load_doc : (docid) ->
      return $.get("/cdxinfo/#{docid}", {}, (data) ->
        data = JSON.parse(data)
        $CDX.plot_context_ref = data['plot_context_ref']
        $CDX.docid = data['docid']
        $CDX.kernelid = data['kernelid']
        $CDX.notebookid = data['notebookid']
        $CDX.all_models = data['all_models']
        $CDX.baseurl = data['baseurl']
        IPython.start_notebook()
        Continuum.load_models($CDX.all_models);
        ws_conn_string = "ws://#{window.location.host}/sub";
        socket = Continuum.submodels(ws_conn_string, docid);
        plotcontext = Continuum.resolve_ref($CDX.plot_context_ref['collections'],
          $CDX.plot_context_ref['type'], $CDX.plot_context_ref['id'])
        plotcontextview = new plotcontext.default_view({'model' : plotcontext, 'el' : $('#dvp-tabs1-pane2')});
        _.delay((() -> window.call_inject(docid)), 1000)
        console.log('RENDERING');)

    load_doc_viz : (docid) ->
      $.when( @load_doc(docid) ).then( ->
        $('a[href="#dvp-tabs1-pane2"]').tab('show'))
    help: () -> 
      console.log("help");
      
    help2: () ->
      console.log("help2");
      
    search: (query, page) -> 
      console.log("search");

  });

  window.$CDX = {};
  window.$CDX.router = new WorkspaceRouter();
  console.log("history start", Backbone.history.start(pushState:true))

  );

  