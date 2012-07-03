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

}).call(this);
