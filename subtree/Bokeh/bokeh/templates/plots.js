var all_models = {{ all_models }};
var modelid = "{{ modelid }}";
var modeltype = "{{ modeltype }}";
var elementid = "{{ elementid }}";
var view;
base = require("./base")
console.log(modelid, modeltype, elementid);
base.load_models(all_models);
var model = base.Collections(modeltype).get(modelid)
window.model=model;
var view = new model.default_view(
    {model : model}
);
window.view = view;
view.render()
_.delay(function(){
    $('#{{ elementid }}').append(view.$el)
}, 1000);
