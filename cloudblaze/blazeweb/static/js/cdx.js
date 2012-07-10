var $CDX;

window.$CDX = {};

$CDX = window.$CDX;

$CDX.IPython = {};

window.$CDX.resizeRoot = function() {
  var cdxRootHeight, midPanelHeight, pyEdPaneHeight, winHeight, winWidth;
  winHeight = $(window).height();
  winWidth = $(window).width();
  cdxRootHeight = winHeight * .95;
  midPanelHeight = cdxRootHeight * .65;
  pyEdPaneHeight = cdxRootHeight * .20;
  $('#cdxRoot').height(cdxRootHeight);
  $('.midPanel').height(midPanelHeight);
  $('#cdxMidContainer').width(winWidth * .95);
  $('.cdx-py-pane').width(winWidth * .85);
  return $('.cdx-py-pane').height(pyEdPaneHeight);
};

$CDX.resize_loop = function() {
  var resizeTimer;
  window.$CDX.resizeRoot();
  IPython.notebook.scroll_to_bottom();
  return resizeTimer = setTimeout($CDX.resize_loop, 500);
};

$CDX._doc_loaded = $.Deferred();

$CDX.doc_loaded = $CDX._doc_loaded.promise();

$CDX._viz_instatiated = $.Deferred();

$CDX.viz_instatiated = $CDX._viz_instatiated.promise();

$(function() {
  var Layout, MyApp, WorkspaceRouter;
  $CDX.utility = {
    start_instatiate: function(docid) {
      if (!$CDX._doc_loaded.isResolved()) {
        return $.get("/cdxinfo/" + docid, {}, function(data) {
          var socket, ws_conn_string;
          data = JSON.parse(data);
          $CDX.plot_context_ref = data['plot_context_ref'];
          $CDX.docid = data['docid'];
          $CDX.all_models = data['all_models'];
          $CDX.IPython.kernelid = data['kernelid'];
          $CDX.IPython.notebookid = data['notebookid'];
          $CDX.IPython.baseurl = data['baseurl'];
          IPython.loadfunc();
          IPython.start_notebook();
          Continuum.load_models($CDX.all_models);
          ws_conn_string = "ws://" + window.location.host + "/sub";
          socket = Continuum.submodels(ws_conn_string, $CDX.docid);
          console.log("resolving _doc_loaded");
          return $CDX._doc_loaded.resolve($CDX.docid);
        });
      }
    },
    instatiate_viz_tab: function() {
      if (!$CDX._viz_instatiated.isResolved()) {
        return $.when($CDX.doc_loaded).then(function() {
          var plotcontext, plotcontextview;
          plotcontext = Continuum.resolve_ref($CDX.plot_context_ref['collections'], $CDX.plot_context_ref['type'], $CDX.plot_context_ref['id']);
          plotcontext.set('render_loop', true);
          window.pc = plotcontext;
          plotcontextview = new plotcontext.default_view({
            'model': plotcontext,
            'el': $('#viz-tab')
          });
          window.pcv = plotcontextview;
          return _.delay((function() {
            $CDX.IPython.inject_plot_client($CDX.docid);
            $CDX.IPython.setup_ipython_events();
            $CDX.resize_loop();
            return $CDX._viz_instatiated.resolve($CDX.docid);
          }), 1000);
        });
      }
    },
    instatiate_specific_viz_tab: function(plot_id) {
      if (!$CDX._viz_instatiated.isResolved()) {
        return $.when($CDX.doc_loaded).then(function() {
          var plotcontext, plotcontextview, s_pc, s_pc_ref;
          plotcontext = Continuum.resolve_ref($CDX.plot_context_ref['collections'], $CDX.plot_context_ref['type'], $CDX.plot_context_ref['id']);
          window.plotcontext = plotcontext;
          s_pc_ref = plotcontext.get('children')[0];
          s_pc = Continuum.resolve_ref(s_pc_ref.collections, s_pc_ref.type, s_pc_ref.id);
          window.s_pc_ref = s_pc_ref;
          window.s_pc = s_pc;
          s_pc.set('render_loop', true);
          console.log(' instatiate_specific_viz_tab set render_loop to true', s_pc.get('render_loop'));
          plotcontextview = new s_pc.default_view({
            'model': s_pc,
            'render_loop': true,
            'el': $('#viz-tab')
          });
          return _.delay((function() {
            window.call_inject($CDX.docid);
            $CDX.IPython.setup_ipython_events();
            return $CDX._viz_instatiated.resolve($CDX.docid);
          }), 1000);
        });
      }
    }
  };
  WorkspaceRouter = Backbone.Router.extend({
    routes: {
      "cdx": "load_default_document",
      "cdx/:docid": "load_doc",
      "cdx/:docid/viz": "load_doc_viz",
      "cdx/:docid/viz/:plot_id": "load_specific_viz"
    },
    load_default_document: function() {
      var user;
      return user = $.get('/userinfo/', {}, function(data) {
        var docs;
        docs = JSON.parse(data)['docs'];
        console.log('URL', "cdx/" + docs[0]);
        return $CDX.router.navigate("cdx/" + docs[0], {
          trigger: true
        });
      });
    },
    load_doc: function(docid) {
      $CDX.docid = docid;
      $CDX.utility.start_instatiate(docid);
      return console.log('RENDERING');
    },
    load_doc_viz: function(docid) {
      $CDX.utility.start_instatiate(docid);
      return this.navigate_doc_viz();
    },
    load_specific_viz: function(docid, plot_id) {
      $CDX.utility.start_instatiate(docid);
      $CDX.utility.instatiate_specific_viz_tab(0);
      return $.when($CDX.viz_instatiated).then(function() {
        console.log("navigate_doc_viz then");
        return $('a[data-route_target="navigate_doc_viz"]').tab('show');
      });
    },
    navigate_doc_viz: function() {
      $CDX.utility.instatiate_viz_tab();
      return $.when($CDX.viz_instatiated).then(function() {
        var expected_path, sliced_path;
        console.log("navigate_doc_viz then");
        $('a[data-route_target="navigate_doc_viz"]').tab('show');
        expected_path = "cdx/" + $CDX.docid + "/viz";
        sliced_path = location.pathname.slice(1);
        if (!(sliced_path === expected_path)) {
          console.log('paths not equal, navigating');
          return $CDX.router.navigate(expected_path);
        }
      });
    }
  });
  MyApp = new Backbone.Marionette.Application();
  Layout = Backbone.Marionette.Layout.extend({
    template: "#layout-template",
    regions: {
      viz_tab: "viz-tab"
    },
    events: {
      "click ul.nav-tabs .js-tab_trigger": function(e) {
        var el, route_target;
        el = $(e.currentTarget);
        route_target = el.attr("data-route_target");
        $CDX.router[route_target]();
        return el.tab('show');
      }
    }
  });
  $CDX.layout = new Layout();
  $.when($CDX.layout_render = $CDX.layout.render()).then(function() {
    $("#layout-root").prepend($CDX.layout_render.el);
    return IPython.loadfunc();
  });
  $CDX.router = new WorkspaceRouter();
  return console.log("history start", Backbone.history.start({
    pushState: true
  }));
});
