toolview = require("./toolview")
ToolView = toolview.ToolView
eventgenerators = require("./eventgenerators")
OnePointWheelEventGenerator = eventgenerators.OnePointWheelEventGenerator
LinearMapper = require("../mappers/1d/linear_mapper").LinearMapper
base = require("../base")
safebind = base.safebind
HasParent = base.HasParent

class ZoomToolView extends ToolView

  initialize : (options) ->
    super(options)
    safebind(this, @model, 'change:dataranges', @build_mappers)
    @build_mappers()

  eventGeneratorClass : OnePointWheelEventGenerator
  evgen_options : {buttonText:"Zoom"}
  tool_events : {
    zoom: "_zoom"}


  build_mappers : () =>
    @mappers = {}
    for temp in _.zip(@mget_obj('dataranges'), @mget('dimensions'))
      [datarange, dim] = temp
      if dim == 'width'
        mapper = new LinearMapper({
          source_range: datarange
          target_range: @plot_view.view_state.get('inner_range_horizontal')
        })
      else
        mapper = new LinearMapper({
          source_range: datarange
          target_range: @plot_view.view_state.get('inner_range_vertical')
        })
      @mappers[dim] = mapper
    return @mappers

  mouse_coords : (e, x, y) ->
    [x_, y_] = [@plot_view.view_state.device_to_sx(x), @plot_view.view_state.device_to_sy(y)]
    return [x_, y_]

  _zoom : (e) ->
    delta   = e.delta
    screenX = e.bokehX
    screenY = e.bokehY

    [x, y]  = @mouse_coords(e, screenX, screenY)
    speed   = @mget('speed')
    factor  = speed * (delta * 50)

    xr = @plot_view.view_state.get('inner_range_horizontal')
    sx_low  = xr.get('start')
    sx_high = xr.get('end')

    yr = @plot_view.view_state.get('inner_range_vertical')
    sy_low  = yr.get('start')
    sy_high = yr.get('end')

    xstart = @plot_view.xmapper.map_from_target(sx_low  - (sx_low  - x)*factor)
    xend   = @plot_view.xmapper.map_from_target(sx_high - (sx_high - x)*factor)
    ystart = @plot_view.ymapper.map_from_target(sy_low  - (sy_low  - y)*factor)
    yend   = @plot_view.ymapper.map_from_target(sy_high - (sy_high - y)*factor)

    @plot_view.pause()
    @plot_view.x_range.set({start: xstart, end: xend})
    @plot_view.y_range.set({start: ystart, end: yend})
    @plot_view.unpause()

    return null


class ZoomTool extends HasParent
  type : "ZoomTool"
  default_view : ZoomToolView
ZoomTool::defaults = _.clone(ZoomTool::defaults)
_.extend(ZoomTool::defaults
  ,
    dimensions : []
    dataranges : []
    speed : 1/600
)

class ZoomTools extends Backbone.Collection
  model : ZoomTool



exports.ZoomToolView = ZoomToolView
exports.zoomtools = new ZoomTools