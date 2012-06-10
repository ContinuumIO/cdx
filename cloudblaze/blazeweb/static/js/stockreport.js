$(function(){
    Continuum.load_models(all_components);
    main_model = Continuum.resolve_ref(main['collections'], 
				       main['type'], main['id']);
    _.delay(function(){
	main_view = new main_model.default_view({'model':main_model})
	$('body').append(main_view.el)
	main_view.render()
    }, 500.0);
});