(function() {

  test('test_table', function() {
    var table, view;
    table = Continuum.Collections['Table'].create({
      'columns': ['a', 'b'],
      'data': [[1, 2], [3, 4], [4, 5]],
      'chunksize': 3,
      'offset': 0,
      'total_rows': 3,
      'usedialog': true
    });
    view = new table.default_view({
      'model': table
    });
    view.render();
    return expect(0);
  });

}).call(this);
