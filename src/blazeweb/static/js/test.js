$(function(){
    table = Continuum.Collections['Table'].create({
	'columns' : JSON.parse(columns),
	'data' : JSON.parse(data)
    })
    view = new table.default_view({'model' : table})
    $('body').append(view.el)
    view.render()
});
