# CDX Coffee Script
#
# This is the main script file for the CDX app.

#some ipython stuff, let's move this to another file later
#end of ipython
window.$CDX = {};
$CDX = window.$CDX
window.$CDX.resizeRoot = () ->
  winHeight = $(window).height();
  winWidth = $(window).width();
  cdxRootHeight=(winHeight * .95);
  midPanelHeight = (cdxRootHeight * .65);
  pyEdPaneHeight = (cdxRootHeight * .20);

  $('#cdxRoot').height(cdxRootHeight);
  $('.midPanel').height(midPanelHeight);
  $('#cdxMidContainer').width(winWidth * .95);
  $('.cdx-py-pane').width(winWidth * .85);
  $('.cdx-py-pane').height(pyEdPaneHeight);

$CDX.resize_loop = () ->
  window.$CDX.resizeRoot()
  IPython.notebook.scroll_to_bottom()
  resizeTimer = setTimeout($CDX.resize_loop, 500);

$(() ->
  WorkspaceRouter = Backbone.Router.extend({
    routes: {
      "cdx" : "load_default_document",
      "cdx/:docid":                 "load_doc",     #help
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
      docdata = $.get("/cdxinfo/#{docid}", {}, (data) ->
        data = JSON.parse(data)
        $CDX.plot_context_ref = data['plot_context_ref']
        $CDX.docid = data['docid']
        $CDX.all_models = data['all_models']
        $CDX.IPython.kernelid = data['kernelid']
        $CDX.IPython.notebookid = data['notebookid']
        $CDX.IPython.baseurl = data['baseurl']
        IPython.start_notebook()
        Continuum.load_models($CDX.all_models);
        ws_conn_string = "ws://#{window.location.host}/sub";
        socket = Continuum.submodels(ws_conn_string, docid);
        plotcontext = Continuum.resolve_ref($CDX.plot_context_ref['collections'],
          $CDX.plot_context_ref['type'], $CDX.plot_context_ref['id'])
        plotcontextview = new plotcontext.default_view({'model' : plotcontext, 'el' : $('#dvp-tabs1-pane2')});
        _.delay(() ->
            $CDX.IPython.inject_plot_client(docid)
            $CDX.IPython.setup_ipython_events()
            $CDX.resize_loop()
          , 1000
        )
        console.log('RENDERING');
      )
    help: () ->
      console.log("help");

    help2: () ->
      console.log("help2");

    search: (query, page) ->
      console.log("search");

  });

  window.$CDX.router = new WorkspaceRouter();
  console.log("history start", Backbone.history.start(pushState:true))

  );

