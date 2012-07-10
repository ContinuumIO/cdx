
class TabSet extends Backbone.View 
  initialize: (options) ->
    """the template for this view needs to have a tab holder element and
    a pane holder element


    I wish I had one dictionary, but I can't figure out what the key should be

    { x : {tab_el, pane_el, view}

    ahh , the key should be route
    """
    @el = $(options.el)
    #@router = router
    @tab_view_objs = options.tab_view_objs
    #note this must be appended to the dom somehow
    @tab_holder_el = $("<ul class='nav nav-tabs'></ul>")
    @pane_holder_el = $("<div class='pane-holder'></div>")

    @tab_view_dict = {}
    for tab_view_obj in @tab_view_objs
      @add_tab(tab_view_obj)

  render: ->
    $(@el).append($('<h3> from render </h3>'))
    $(@el).append(@tab_holder_el)
    $(@el).append(@pane_holder_el)
    
  add_tab: (tab_view_obj) ->
    tvo = tab_view_obj
    @tab_view_dict[tab_view_obj.route] = tab_view_obj
    tvo.tab_el =  @_create_tab(tab_view_obj)
    tvo.pane_el = @_create_pane(tab_view_obj)
    @tab_holder_el.append(tvo.tab_el)
    @pane_holder_el.append(tvo.pane_el)
    
    if _.keys(@tab_view_dict).length == 1
      @activate(_.keys(@tab_view_dict)[0])
    tvo.route
        
  _create_tab: (tab_view_obj) ->
    tab = $("<li><a>#{tab_view_obj.tab_name}</a></li>")
    tab.click( (e) =>
      @activate(tab_view_obj.route))
    # add click handler for x button to remove the tab 
    tab
  _create_pane: (tab_view_obj) ->
    pane = $("<div class='pane'></div>")
    pane.append(tab_view_obj.view.render())

  activate: (route) ->

    """ I'm not sure how to handle the deferred rendering bit here,
    should tabs only be rendered on first view? or on instatiation?
    what about tabs that depend on data being loaded?

    the common pattern in backbone land that I have seen is


    Backbone.Router.extend({
      routes: {
        "some_tab" : ->
          model = new ModelType({id:5})
          $.when(model.fetch()).then(->
            view = new View(model:model, el: '#some_id')
            view.render())}})


    so far as this tab container is concerned, I want to flip that on
    its head and somehow bundle calling render() on the view from the
    TabContainer, make the view responsible for fetching its own model

    I'm not quite sure how to do that, or whether or not I will run
    into problems that way


    hopefully I can figure out how to plumb activate into a router
    
      
    """
    console.log("activate " , route)
    tvo = tab_view_obj = @tab_view_dict[route]
    $.when(tvo.view.render()).then(
      @tab_holder_el.find('.active').removeClass('active')
      tvo.tab_el.addClass('active')
      @pane_holder_el.find('.active').removeClass('active')
      tvo.pane_el.addClass('active')
      )

  remove_tab: (route) ->
    """ TODO """
    
      



