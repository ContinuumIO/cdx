$(function(){
    table = Continuum.Collections['Table'].create(table_obj);
    view = new table.default_view({'model' : table});
    $('body').append(view.el);
    view.render();
});
