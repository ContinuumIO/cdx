
class BlahView extends Backbone.View
  render: () ->
    return "<h3> blah view </h3>"

$(-> 

  global_routing_object = new Backbone.Router.extend({})
  instatiated_view = new BlahView()
  ts = TabSet(
    el: "#layout-root",
    router: global_routing_object,
    tab_views : [
      { tab_name : "tab 1", view: instatiated_view, route: "cdx/tab_1"}
      ]
    )
  instatiated_view2 = new BackboneView()
  ts.add_tab(
     tab_name : "tab 2", view: instatiated_view2, route: "cdx/tab_2"
  )


);