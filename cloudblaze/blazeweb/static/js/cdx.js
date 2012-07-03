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

  window.call_inject = function() {
    var targeturl;
    targeturl = _.template("http://{{ host }}/bb/", {
      'host': window.location.host
    });
    return inject_plot_client(window.topic, targeturl);
  };

  $(function() {
    var WorkspaceRouter;
    WorkspaceRouter = Backbone.Router.extend({
      routes: {
        "module/help": "help",
        "module/help2": "help2",
        "module/search/:query": "search",
        "module/search/:query/p:page": "search"
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
    window.$C = {};
    window.$C.router = new WorkspaceRouter();
    return console.log("history start", Backbone.history.start({
      pushState: true
    }));
  });

}).call(this);
