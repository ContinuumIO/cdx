define [
  "underscore"
  "jquery"
  "common/continuum_view"
  "./events"
  "./hboxtemplate"
  "./vboxtemplate"
], (_, $, ContinuumView, events, hboxtemplate, vboxtemplate) ->

  class SlideableLayout extends ContinuumView.View
    dim : null #width
    mouse_coord : null #pageX
    component_selector : null #hcomponent
    content_selector : null #hcontent
    template : null
    initialize : (options) ->
      super(options)
      if options.elements
        @height = options.height
        @width = options.width
        @elements = options.elements
        @sizes = (100 / @elements.length for el in @elements)
      @render()
      #state vars, call twice cause we record the old state
      @eventgenerator = new events.TwoPointEventGenerator()

    set_sizes : () ->
      for temp in _.zip(@$el.find(@component_selector), @sizes)
        [el, size] = temp
        $(el).css(@dim, String(size) + "%")
      return null

    render : () ->
      if @views
        _.map(@views, (view) -> view.$el.detach())
      @$el.html('')
      @$el.html(@template({elements : @elements}))
      for temp in _.zip(@$(@content_selector), @elements)
        [content, node] = temp
        $(content).append(node)
      if @height
        @$el.height(@height)
      if @width
        @$el.width(@width)
      @set_sizes()
      return @

    delegateEvents : (events) ->
      super(events)
      @listenTo(@eventgenerator, 'dragmove', @mousemove)
      @listenTo(@eventgenerator, 'dragstop', @mouseup)

    handle_click : (e) =>
      @idx = $(e.currentTarget).attr('idx')
      @eventgenerator.mousedown(e)
      e.preventDefault()

    mousemove : (basepoint, last_coords, coords) =>
      diff = coords[@mouse_coord] - last_coords[@mouse_coord]
      percentage_delta = (100 * diff / @$el[@dim]())
      @sizes[@idx - 1] = @sizes[@idx - 1] + percentage_delta
      @sizes[@idx] = @sizes[@idx] - percentage_delta
      @set_sizes()

  class HBoxView extends SlideableLayout
    dim : 'width'
    mouse_coord : 'pageX'
    component_selector : '.hcomponent'
    content_selector : '.hcontent'
    template : hboxtemplate
    attributes :
      class : 'cdxhbox'

    events :
      "mousedown .hseparator" :  'handle_click'

  class VBoxView extends SlideableLayout
    dim : 'height'
    mouse_coord : 'pageY'
    component_selector : '.vcomponent'
    content_selector : '.vcontent'
    template : vboxtemplate
    attributes :
      class : 'cdxvbox'

    events :
      "mousedown .vseparator" :  'handle_click'

  return {
    HBoxView: HBoxView
    VBoxView: VBoxView
  }
