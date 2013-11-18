define [
  "underscore"
  "jquery"
  "backbone"
], (_, $, Backbone) ->

  class TwoPointEventGenerator
    # Implementation of TwoPointEventGenerator which is plot independent
    # we should probably make the one in tools use this one?
    constructor : () ->
      @id = _.uniqueId('twopointeventgen')

    coordinate_notify : (eventname) ->
      if _.isUndefined(eventname)
        eventname = 'coordinates'
      @trigger(eventname, @basepoint, @last_coords, @coords)

    set_coords : (pageX, pageY, isbasepoint) =>
      @last_coords = @coords
      @coords =
        pageX : pageX
        pageY : pageY
      if isbasepoint
        @basepoint = @coords

    mousedown : (e) =>
      #you call this function to start everything
      @set_coords(e.pageX, e.pageY, true)
      @coordinate_notify('dragstart')
      $(document).on("mousemove.#{@id}", @mousemove)
      $(document).on("mouseup.#{@id}", @mouseup)

    mousemove : (e) =>
      @set_coords(e.pageX, e.pageY, true)
      @coordinate_notify('dragmove')
      e.preventDefault()

    mouseup : (e) =>
      @set_coords(e.pageX, e.pageY, true)
      @coordinate_notify('dragstop')
      $(document).off("mousemove.#{@id}")
      $(document).off("mouseup.#{@id}")

  _.extend(TwoPointEventGenerator.prototype, Backbone.Events)

  return {
    TwoPointEventGenerator: TwoPointEventGenerator
  }
