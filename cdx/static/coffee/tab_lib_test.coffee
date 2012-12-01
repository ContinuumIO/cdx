
class BlahView extends Backbone.View
  render: () ->
    return "<h3> blah view </h3>"

class BazView extends Backbone.View
  render: () ->
    return "<h3> baz view </h3>"


$(-> 
  instatiated_view = new BlahView({})
  #$("#layout-root").html(instatiated_view.render())
  tvos = [{ tab_name : "tab 1", view: instatiated_view, route: "cdx/tab_1"}]
  
  ts = new TabSet(el:"#layout-root", tab_view_objs: tvos)
  window.ts = ts
  instatiated_view2 = new BazView()
  ts.add_tab(tab_name : "tab 2", view: instatiated_view2, route: "cdx/tab_2")
  ts.render()
  #$("#layout-root").(instatiated_view.render())

);