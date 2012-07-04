(function() {
  var inject_plot_client;

  inject_plot_client = function(docid, url) {
    var cells, code, last_cell;
    code = _.template("import cloudblaze.continuumweb.plot as plot; p = plot.PlotClient('{{ docid }}', '{{ url }}')", {
      docid: docid,
      url: url
    });
    cells = IPython.notebook.cells();
    last_cell = cells[cells.length - 1];
    last_cell.set_code(code);
    IPython.notebook.select(cells.length - 1);
    return IPython.notebook.execute_selected_cell();
  };

  window.call_inject = function(docid) {
    var targeturl;
    targeturl = _.template("http://{{ host }}/bb/", {
      'host': window.location.host
    });
    return inject_plot_client(docid, targeturl);
  };

  $(function() {
    var WorkspaceRouter;
    WorkspaceRouter = Backbone.Router.extend({
      routes: {
        "cdx": "load_default_document",
        "cdx/:docid": "load_doc",
        "module/help2": "help2",
        "module/search/:query": "search",
        "module/search/:query/p:page": "search"
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
        var docdata;
        return docdata = $.get("/cdxinfo/" + docid, {}, function(data) {
          var plotcontext, plotcontextview, socket, ws_conn_string;
          data = JSON.parse(data);
          $CDX.plot_context_ref = data['plot_context_ref'];
          $CDX.docid = data['docid'];
          $CDX.kernelid = data['kernelid'];
          $CDX.notebookid = data['notebookid'];
          $CDX.all_models = data['all_models'];
          $CDX.baseurl = data['baseurl'];
          IPython.start_notebook();
          Continuum.load_models($CDX.all_models);
          ws_conn_string = "ws://" + window.location.host + "/sub";
          socket = Continuum.submodels(ws_conn_string, docid);
          plotcontext = Continuum.resolve_ref($CDX.plot_context_ref['collections'], $CDX.plot_context_ref['type'], $CDX.plot_context_ref['id']);
          plotcontextview = new plotcontext.default_view({
            'model': plotcontext,
            'el': $('#dvp-tabs1-pane2')
          });
          _.delay((function() {
            return window.call_inject(docid);
          }), 1000);
          return console.log('RENDERING');
        });
      },
      help: function() {
        return console.log("help");
      },
      help2: function() {
        return console.log("help2");
      },
      search: function(query, page) {
        return console.log("search");
      }
    });
    window.$CDX = {};
    window.$CDX.router = new WorkspaceRouter();
    return console.log("history start", Backbone.history.start({
      pushState: true
    }));
  });

}).call(this);
