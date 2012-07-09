# CDX Coffee Script
#
# This is the main script file for the CDX app.

inject_plot_client = (docid, url) ->
  #code = _.template(
  #  "import cloudblaze.continuumweb.plot as plot; p = plot.PlotClient('{{ docid }}', '{{ url }}')",
  #  docid : docid
  #  url : url)
 
  code = "import cloudblaze.continuumweb.plot as plot; p = plot.PlotClient('#{docid}', '#{url}')"
  cells = IPython.notebook.cells()
  last_cell = cells[(cells.length - 1)]
  last_cell.set_code(code)
  IPython.notebook.select((cells.length - 1))
  IPython.notebook.execute_selected_cell()  

window.call_inject =   (docid) ->
  targeturl = _.template("http://{{ host }}/bb/", {'host' : window.location.host})
  inject_plot_client(docid, targeturl)


$(() ->
  window.$CDX = {};
  $CDX = window.$CDX;
  $CDX._doc_loaded = $.Deferred();
  $CDX.doc_loaded = $CDX._doc_loaded.promise();
  $CDX._viz_instatiated = $.Deferred();
  $CDX.viz_instatiated = $CDX._viz_instatiated.promise();

  $CDX.utility = {
    start_instatiate: (docid) ->
      if not $CDX._doc_loaded.isResolved()
        $.get("/cdxinfo/#{docid}", {}, (data) ->
          data = JSON.parse(data)
          $CDX.plot_context_ref = data['plot_context_ref']
          $CDX.docid = data['docid'] # in case the server returns a different docid
          $CDX.kernelid = data['kernelid']
          $CDX.notebookid = data['notebookid']
          $CDX.all_models = data['all_models']
          $CDX.baseurl = data['baseurl']
          IPython.start_notebook()
          Continuum.load_models($CDX.all_models);
          ws_conn_string = "ws://#{window.location.host}/sub";
          socket = Continuum.submodels(ws_conn_string, $CDX.docid);
          console.log("resolving _doc_loaded");
          $CDX._doc_loaded.resolve($CDX.docid))
        
    instatiate_viz_tab: ->
      if not $CDX._viz_instatiated.isResolved()
        $.when($CDX.doc_loaded).then(->
          plotcontext = Continuum.resolve_ref($CDX.plot_context_ref['collections'],
            $CDX.plot_context_ref['type'], $CDX.plot_context_ref['id'])
          plotcontextview = new plotcontext.default_view(
            {'model' : plotcontext, 'el' : $('#viz-tab')});

          _.delay((() ->
            window.call_inject($CDX.docid)
            $CDX._viz_instatiated.resolve($CDX.docid)),
            1000))

    instatiate_specific_viz_tab: (plot_id) ->
      if not $CDX._viz_instatiated.isResolved()
        $.when($CDX.doc_loaded).then(->
          plotcontext = Continuum.resolve_ref($CDX.plot_context_ref['collections'],
            $CDX.plot_context_ref['type'], $CDX.plot_context_ref['id'])
          window.plotcontext = plotcontext
          s_pc_ref = plotcontext.get('children')[0]
          s_pc = Continuum.resolve_ref(s_pc_ref.collections, s_pc_ref.type, s_pc_ref.id)
          window.s_pc_ref = s_pc_ref
          window.s_pc = s_pc
          plotcontextview = new s_pc.default_view(
            {'model' : s_pc, 'render_loop':true, 'el' : $('#viz-tab')});
          _.delay((() ->
            window.call_inject($CDX.docid)
            $CDX._viz_instatiated.resolve($CDX.docid)),
            1000))
  };
  
  WorkspaceRouter = Backbone.Router.extend({
    routes: {
      "cdx" : "load_default_document",
      "cdx/:docid":                 "load_doc",     #help
      "cdx/:docid/viz":             "load_doc_viz",     #help
      "cdx/:docid/viz/:plot_id":    "load_specific_viz",     #help
      },
    load_default_document : () ->
      user = $.get('/userinfo/', {}, (data) ->
        docs = JSON.parse(data)['docs']
        console.log('URL', "cdx/#{docs[0]}")
        $CDX.router.navigate("cdx/#{docs[0]}", {trigger : true}))

    load_doc : (docid) ->
      $CDX.docid = docid
      $CDX.utility.start_instatiate(docid)
      console.log('RENDERING');

    load_doc_viz : (docid) ->
      $CDX.utility.start_instatiate(docid)
      @navigate_doc_viz()

    load_specific_viz : (docid, plot_id) ->
      $CDX.utility.start_instatiate(docid)
      $CDX.utility.instatiate_specific_viz_tab(0)
      $.when($CDX.viz_instatiated).then(->
        console.log("navigate_doc_viz then")
        $('a[data-route_target="navigate_doc_viz"]').tab('show'))

    navigate_doc_viz: ->
      $CDX.utility.instatiate_viz_tab()
      $.when($CDX.viz_instatiated).then(->
        console.log("navigate_doc_viz then")
        $('a[data-route_target="navigate_doc_viz"]').tab('show')
        expected_path = "cdx/#{$CDX.docid}/viz"
        sliced_path = location.pathname[1..]
        if not (sliced_path == expected_path)
          console.log('paths not equal, navigating')
          $CDX.router.navigate(expected_path)
        )
      }
  );

  MyApp = new Backbone.Marionette.Application();

  Layout = Backbone.Marionette.Layout.extend(
    template: "#layout-template",

    regions: {
      viz_tab: "viz-tab"
      }
    events: {
      "click ul.nav-tabs .js-tab_trigger" : (e) ->
        el = $(e.currentTarget)
        route_target = el.attr("data-route_target")
        $CDX.router[route_target]()
        el.tab('show');
      }

    );
  

  $CDX.layout = new Layout();
  $.when($CDX.layout_render = $CDX.layout.render()).then( ->
    $("#layout-root").prepend($CDX.layout_render.el);
    IPython.loadfunc();
    );

  $CDX.router = new WorkspaceRouter();
  console.log("history start", Backbone.history.start(pushState:true))

  );



