base = require('../../base')
HasParent = base.HasParent
safebind = base.safebind

properties = require('../properties')
line_properties = properties.line_properties
text_properties = properties.text_properties

PlotWidget = require('../../common/plot_widget').PlotWidget
ticking = require('../../common/ticking')

signum = (x) -> x ? x<0 ? -1:1:0


_angle_lookup = {
  top:
    parallel: 0
    normal: -Math.PI/2
    horizontal: 0
    vertical: -Math.PI/2
  bottom:
    parallel: 0
    normal: Math.PI/2
    horizontal: 0
    vertical: Math.PI/2
  left:
    parallel: -Math.PI/2
    normal: 0
    horizontal: 0
    vertical: -Math.PI/2
  right:
    parallel: Math.PI/2
    normal: 0
    horizontal: 0
    vertical: Math.PI/2
}

_baseline_lookup = {
  top:
    parallel: 'alphabetic'
    normal: 'middle'
    horizontal: 'alphabetic'
    vertical: 'middle'
  bottom:
    parallel: 'hanging'
    normal: 'middle'
    horizontal: 'hanging'
    vertical: 'middle'
  left:
    parallel: 'alphabetic'
    normal: 'middle'
    horizontal: 'middle'
    vertical: 'alphabetic'
  right:
    parallel: 'alphabetic'
    normal: 'middle'
    horizontal: 'middle'
    vertical: 'alphabetic'
}

_align_lookup = {
  top:
    parallel: 'center'
    normal: 'left'
    horizontal: 'center'
    vertical: 'left'
  bottom:
    parallel: 'center'
    normal: 'left'
    horizontal: 'center'
    vertical: 'right'
  left:
    parallel: 'center'
    normal: 'right'
    horizontal: 'right'
    vertical: 'center'
  right:
    parallel: 'center'
    normal: 'left'
    horizontal: 'left'
    vertical: 'center'
}




class LinearAxisView extends PlotWidget
  initialize: (attrs, options) ->
    #hugo : i don't think views take 2 params for initialize
    super(attrs, options)

    guidespec = @mget('guidespec')
    @rule_props = new line_properties(@, guidespec, 'axis_')
    @major_tick_props = new line_properties(@, guidespec, 'major_tick_')
    @major_label_props = new text_properties(@, guidespec, 'major_label_')
    @axis_label_props = new text_properties(@, guidespec, 'axis_label_')

  render: () ->

    ctx = @plot_view.ctx
    ctx.save()

    @_draw_rule(ctx)

    @_draw_major_ticks(ctx)

    @_draw_major_labels(ctx)

    @_draw_axis_label(ctx)

    ctx.restore()

  bind_bokeh_events: () ->
    safebind(this, @model, 'change', @request_render)

  padding_request: () ->
    return @_padding_request()

  _draw_rule: (ctx) ->
    [x, y] = @mget('rule_coords')
    [sx, sy] = @plot_view.map_to_screen(x, "data", y, "data")
    @rule_props.set(ctx, @)
    ctx.beginPath()
    ctx.moveTo(sx[0], sy[0])
    for i in [1..sx.length-1]
      ctx.lineTo(sx[i], sy[i])
    ctx.stroke()
    return

  _draw_major_ticks: (ctx) ->
    [x, y] = @mget('major_coords')
    [sx, sy] = @plot_view.map_to_screen(x, "data", y, "data")
    [nx, ny] = @mget('normals')
    tin = @mget('major_tick_in')
    tout = @mget('major_tick_out')
    @major_tick_props.set(ctx, @)
    for i in [0..sx.length-1]
      ctx.beginPath()
      ctx.moveTo(sx[i]+nx*tout, sy[i]+ny*tout)
      ctx.lineTo(sx[i]-nx*tin,  sy[i]-ny*tin)
      ctx.stroke()
    return

  _draw_major_labels: (ctx) ->
    [x, y] = coords = @mget('major_coords')
    [sx, sy] = @plot_view.map_to_screen(x, "data", y, "data")
    [nx, ny] = @mget('normals')
    dim = @mget('guidespec').dimension
    side = @mget('side')
    orient = @mget('major_label_orientation')

    if _.isString(orient)
      angle = _angle_lookup[side][orient]
    else
      angle = -orient
    standoff = @_tick_extent() + @mget('major_label_standoff')

    formatter = new ticking.BasicTickFormatter()
    labels = formatter.format(coords[dim])

    # override baseline and alignment with heuristics for tick labels
    @major_label_props.set(ctx, @)
    @_apply_location_heuristics(ctx, side, orient)

    for i in [0..sx.length-1]
      if angle
        ctx.translate(sx[i]+nx*standoff, sy[i]+ny*standoff)
        ctx.rotate(angle)
        ctx.fillText(labels[i], 0, 0)
        ctx.rotate(-angle)
        ctx.translate(-sx[i]-nx*standoff, -sy[i]-ny*standoff)
      else
        ctx.fillText(labels[i], sx[i] + nx*standoff, sy[i] + ny*standoff)

    return

  _draw_axis_label: (ctx) ->
    label = @mget('axis_label')

    if not label?
      return

    [x, y] = @mget('rule_coords')
    [sx, sy] = @plot_view.map_to_screen(x, "data", y, "data")
    [nx, ny] = @mget('normals')
    side = @mget('side')
    orient = 'parallel'

    angle = _angle_lookup[side][orient]
    standoff = @_tick_extent() + @_tick_label_extent() + @mget('axis_label_standoff')
    sx = (sx[0] + sx[sx.length-1])/2
    sy = (sy[0] + sy[sy.length-1])/2

    # override baseline and alignment with heuristics for axis labels
    @axis_label_props.set(ctx, @)
    @_apply_location_heuristics(ctx, side, orient)

    if angle
      ctx.translate(sx+nx*standoff, sy+ny*standoff)
      ctx.rotate(angle)
      ctx.fillText(label, 0, 0)
      ctx.rotate(-angle)
      ctx.translate(-sx-nx*standoff, -sy-ny*standoff)
    else
      ctx.fillText(label, sx+nx*standoff, sy+ny*standoff)

    return

  _apply_location_heuristics: (ctx, side, orient) ->
    if _.isString(orient)
      baseline = _baseline_lookup[side][orient]
      align = _align_lookup[side][orient]

    else if orient == 0
      baseline = _baseline_lookup[side][orient]
      align = _align_lookup[side][orient]

    else if orient < 0
      baseline = 'middle'
      if side == 'top'
        align = 'right'
      else if side == 'bottom'
        align = 'left'
      else if side == 'left'
        align = 'right'
      else if side == 'right'
        align = 'left'

    else if orient > 0
      baseline = 'middle'
      if side == 'top'
        align = 'left'
      else if side == 'bottom'
        align = 'right'
      else if side == 'left'
        align = 'right'
      else if side == 'right'
        align = 'left'

    ctx.textBaseline = baseline
    ctx.textAlign = align

  _tick_extent: () ->
    return @mget('major_tick_out')

  _tick_label_extent: () ->
    extent = 0

    dim = @mget('guidespec').dimension
    coords = @mget('major_coords')
    side = @mget('side')
    orient = @mget('major_label_orientation')

    formatter = new ticking.BasicTickFormatter()
    labels = formatter.format(coords[dim])

    @major_label_props.set(@plot_view.ctx, @)

    if _.isString(orient)
      factor = 1
      angle = _angle_lookup[side][orient]
    else
      factor = 2
      angle = -orient
    angle = Math.abs(angle)
    c = Math.cos(angle)
    s = Math.sin(angle)

    if side == "top" or side == "bottom"
      for i in [0..labels.length-1]
        if not labels[i]?
          continue
        w = @plot_view.ctx.measureText(labels[i]).width * 1.3 # height overestimates, compensate
        h = @plot_view.ctx.measureText(labels[i]).ascent
        val = w*s + (h/factor)*c
        if val > extent
          extent = val
    else
      for i in [0..labels.length-1]
        if not labels[i]?
          continue
        w = @plot_view.ctx.measureText(labels[i]).width * 1.3 # height overestimates, compensate
        h = @plot_view.ctx.measureText(labels[i]).ascent
        val = w*c + (h/factor)*s
        if val > extent
          extent = val

    if extent > 0
      extent += @mget('major_label_standoff')

    rounding = @mget('rounding_value')

    return (Math.floor(extent/rounding) + 1) * rounding

  _axis_label_extent: () ->
    extent = 0

    side = @mget('side')
    orient = 'parallel'

    @major_label_props.set(@plot_view.ctx, @)

    angle = Math.abs(_angle_lookup[side][orient])
    c = Math.cos(angle)
    s = Math.sin(angle)

    if @mget('axis_label')
      extent += @mget('axis_label_standoff')
      @axis_label_props.set(@plot_view.ctx, @)
      w = @plot_view.ctx.measureText(@mget('axis_label')).width
      h = @plot_view.ctx.measureText(@mget('axis_label')).ascent
      if side == "top" or side == "bottom"
        extent += w*s + h*c
      else
        extent += w*c + h*s

    return extent

    # rounding = @mget('rounding_value')

    # return (Math.floor(extent/rounding) + 1) * rounding

  _padding_request: () ->
    req = {}

    side = @mget('side')
    loc = @mget('guidespec').location ? 'min'

    if not _.isString(loc)
      return req

    padding = 0
    padding += @_tick_extent()
    padding += @_tick_label_extent()
    padding += @_axis_label_extent()

    req[side] = padding
    return req


class LinearAxis extends HasParent
  default_view: LinearAxisView
  type: 'GuideRenderer'

  dinitialize: (attrs, options)->
    super(attrs, options)
    @register_property('bounds', @_bounds, false)
    @add_dependencies('bounds', this, ['guidespec'])
    @add_dependencies('bounds', @get_obj('plot'), ['x_range', 'y_range'])

    @register_property('rule_coords', @_rule_coords, false)
    @add_dependencies('rule_coords', this, ['bounds', 'dimension', 'location'])

    @register_property('major_coords', @_major_coords, false)
    @add_dependencies('major_coords', this, ['bounds', 'dimension', 'location'])

    @register_property('normals', @_normals, false)
    @add_dependencies('normals', this, ['bounds', 'dimension', 'location'])

    @register_property('side', @_side, false)
    @add_dependencies('side', this, ['normals'])

    @register_property('padding_request', @_padding_request, false)

  _bounds: () ->
    i = @get('guidespec').dimension
    j = (i + 1) % 2

    ranges = [@get_obj('plot').get_obj('x_range'),
      @get_obj('plot').get_obj('y_range')]

    user_bounds = @get('guidespec').bounds ? 'auto'
    range_bounds = [ranges[i].get('min'), ranges[i].get('max')]

    if _.isArray(user_bounds)
      start = Math.min(user_bounds[0], user_bounds[1])
      end = Math.max(user_bounds[0], user_bounds[1])
      if start < range_bounds[0]
        start = range_bounds[0]
      else if start > range_bounds[1]
        start = null
      if end > range_bounds[1]
        end = range_bounds[1]
      else if end < range_bounds[0]
        end = null
    else
      [start, end] = range_bounds

    return [start, end]

  _rule_coords: () ->
    i = @get('guidespec').dimension
    j = (i + 1) % 2

    ranges = [@get_obj('plot').get_obj('x_range'), @get_obj('plot').get_obj('y_range')]
    range = ranges[i]
    cross_range = ranges[j]

    [start, end] = @get('bounds')

    xs = new Array(2)
    ys = new Array(2)
    coords = [xs, ys]

    loc = @get('guidespec').location ? 'min'
    if _.isString(loc)
      if loc == 'left' or loc == 'bottom'
        loc = 'start'
      else if loc == 'right' or loc == 'top'
        loc = 'end'
      loc = cross_range.get(loc)

    coords[i][0] = start
    coords[i][1] = end
    coords[j][0] = loc
    coords[j][1] = loc

    return coords

  _major_coords: () ->
    i = @get('guidespec').dimension
    j = (i + 1) % 2

    ranges = [@get_obj('plot').get_obj('x_range'), @get_obj('plot').get_obj('y_range')]
    range = ranges[i]
    cross_range = ranges[j]

    [start, end] = @get('bounds')

    tmp = Math.min(start, end)
    end = Math.max(start, end)
    start = tmp

    interval = ticking.auto_interval(start, end)
    ticks = ticking.auto_ticks(null, null, start, end, interval)

    loc = @get('guidespec').location ? 'min'
    if _.isString(loc)
      if loc == 'left' or loc == 'bottom'
        loc = 'start'
      else if loc == 'right' or loc == 'top'
        loc = 'end'
      loc = cross_range.get(loc)

    xs = []
    ys = []
    coords = [xs, ys]

    for ii in [0..ticks.length-1]
      coords[i].push(ticks[ii])
      coords[j].push(loc)

    return coords

  _normals: () ->
    i = @get('guidespec').dimension
    j = (i + 1) % 2

    ranges = [@get_obj('plot').get_obj('x_range'), @get_obj('plot').get_obj('y_range')]
    range = ranges[i]
    cross_range = ranges[j]

    [start, end] = @get('bounds')

    loc = @get('guidespec').location ? 'min'
    cstart = cross_range.get('start')
    cend = cross_range.get('end')

    normals = [0, 0]

    if _.isString(loc)
      normals[j] = if (end-start) < 0 then -1 else 1
      if i == 0
        if (loc == 'max' and (cstart < cend)) or (loc == 'min' and (cstart > cend)) or loc == 'right' or loc == 'top'
          normals[j] *= -1
      else if i == 1
        if (loc == 'min' and (cstart < cend)) or (loc == 'max' and (cstart > cend)) or loc == 'left' or loc == 'bottom'
          normals[j] *= -1

    else
      if i == 0
        if Math.abs(loc-cstart) <= Math.abs(loc-cend)
          normals[j] = 1
        else
          normals[j] = -1
      else
        if Math.abs(loc-cstart) <= Math.abs(loc-cend)
          normals[j] = -1
        else
          normals[j] = 1
    return normals

  _side: () ->
    n = @get('normals')
    if n[1] == -1
      side = 'top'
    else if n[1] == 1
      side = 'bottom'
    else if n[0] == -1
      side = 'left'
    else if n[0] == 1
      side = 'right'
    return side




LinearAxis::defaults = _.clone(LinearAxis::defaults)


LinearAxis::display_defaults = _.clone(LinearAxis::display_defaults)
_.extend(LinearAxis::display_defaults, {

  level: 'overlay'

  axis_line_color: 'black'
  axis_line_width: 1
  axis_line_alpha: 1.0
  axis_line_join: 'miter'
  axis_line_cap: 'butt'
  axis_line_dash: []
  axis_line_dash_offset: 0

  major_tick_in: 2
  major_tick_out: 6
  major_tick_line_color: 'black'
  major_tick_line_width: 1
  major_tick_line_alpha: 1.0
  major_tick_line_join: 'miter'
  major_tick_line_cap: 'butt'
  major_tick_line_dash: []
  major_tick_line_dash_offset: 0

  major_label_standoff: 5
  major_label_orientation: "horizontal"
  major_label_text_font: "helvetica"
  major_label_text_font_size: "10pt"
  major_label_text_font_style: "normal"
  major_label_text_color: "#444444"
  major_label_text_alpha: 1.0
  major_label_text_align: "center"
  major_label_text_baseline: "alphabetic"

  axis_label: ""
  axis_label_standoff: 5
  axis_label_text_font: "helvetica"
  axis_label_text_font_size: "16pt"
  axis_label_text_font_style: "normal"
  axis_label_text_color: "#444444"
  axis_label_text_alpha: 1.0
  axis_label_text_align: "center"
  axis_label_text_baseline: "alphabetic"

  rounding_value: 20

})

class LinearAxes extends Backbone.Collection
   model: LinearAxis

exports.linearaxes = new LinearAxes()
exports.LinearAxis = LinearAxis
exports.LinearAxisView = LinearAxisView
