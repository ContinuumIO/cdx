# CDX Coffee Script
#
# This is the main script file for the CDX app.


window.$CDX = {};
$CDX = window.$CDX;
$CDX.IPython = {}
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

$CDX._doc_loaded = $.Deferred();
$CDX.doc_loaded = $CDX._doc_loaded.promise();
$CDX._viz_instatiated = $.Deferred();
$CDX.viz_instatiated = $CDX._viz_instatiated.promise();


$(() ->

  $CDX.utility = {
    start_instatiate: (docid) ->
      if not $CDX._doc_loaded.isResolved()
        $.get("/cdxinfo/#{docid}", {}, (data) ->
          data = JSON.parse(data)
          $CDX.plot_context_ref = data['plot_context_ref']
          $CDX.docid = data['docid'] # in case the server returns a different docid
          $CDX.all_models = data['all_models']

          $CDX.IPython.kernelid = data['kernelid']
          $CDX.IPython.notebookid = data['notebookid']
          $CDX.IPython.baseurl = data['baseurl']

          IPython.loadfunc()
          IPython.start_notebook()
          Continuum.load_models($CDX.all_models);
          ws_conn_string = "ws://#{window.location.host}/sub";
          socket = Continuum.submodels(ws_conn_string, $CDX.docid)
          console.log("resolving _doc_loaded")
          _.delay(
            () ->
              $CDX.IPython.inject_plot_client($CDX.docid)
              $CDX.IPython.setup_ipython_events()
              $CDX.resize_loop()
              $CDX._doc_loaded.resolve($CDX.docid)
            , 1000
          )
        )
    instatiate_viz_tab: ->
      if not $CDX._viz_instatiated.isResolved()
        $.when($CDX.doc_loaded).then(->
          plotcontext = Continuum.resolve_ref($CDX.plot_context_ref['collections'],
            $CDX.plot_context_ref['type'], $CDX.plot_context_ref['id'])
          plotcontext.set('render_loop', true)
          window.pc = plotcontext
          plotcontextview = new plotcontext.default_view(
            {'model' : plotcontext, 'el' : $('#viz-tab')});
          window.pcv = plotcontextview
          $CDX._viz_instatiated.resolve($CDX.docid))


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

          s_pc.set('render_loop', true)
          console.log(' instatiate_specific_viz_tab set render_loop to true', s_pc.get('render_loop'))
          plotcontextview = new s_pc.default_view(
            {'model' : s_pc, 'render_loop':true, 'el' : $('#viz-tab')});
          #plotcontextview.render_deferred_components()
          #plotcontextview.render()
          #plotcontextview._dirty = true
          _.delay((() ->
            window.call_inject($CDX.docid)
            $CDX.IPython.setup_ipython_events()
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
    );

  $CDX.router = new WorkspaceRouter();
  console.log("history start", Backbone.history.start(pushState:true))

  );
