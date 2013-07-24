
properties = require('../properties')
glyph_properties = properties.glyph_properties
line_properties = properties.line_properties
fill_properties = properties.fill_properties

glyph = require('./glyph')
Glyph = glyph.Glyph
GlyphView = glyph.GlyphView


class AnnularWedgeView extends GlyphView

  initialize: (options) ->
    ##duped in many classes
    @glyph_props = @init_glyph(@mget('glyphspec'))
    if @mget('selection_glyphspec')
      spec = _.extend({}, @mget('glyphspec'), @mget('selection_glyphspec'))
      @selection_glyphprops = @init_glyph(spec)
    if @mget('nonselection_glyphspec')
      spec = _.extend({}, @mget('glyphspec'), @mget('nonselection_glyphspec'))
      @nonselection_glyphprops = @init_glyph(spec)
    ##duped in many classes
    @do_fill   = @glyph_props.fill_properties.do_fill
    @do_stroke = @glyph_props.line_properties.do_stroke
    super(options)

  init_glyph : (glyphspec) ->
    glyph_props = new glyph_properties(
      @,
      glyphspec,
      ['x', 'y', 'inner_radius', 'outer_radius', 'start_angle', 'end_angle', 'direction:string'],
      [
        new fill_properties(@, glyphspec),
        new line_properties(@, glyphspec)
      ]
    )
    return glyph_props

  _set_data: (@data) ->
    @x = @glyph_props.v_select('x', data)
    @y = @glyph_props.v_select('y', data)
    start_angle = (@glyph_props.select('start_angle', obj) for obj in data) # TODO deg/rad
    @start_angle = (-angle for angle in start_angle)
    end_angle = (@glyph_props.select('end_angle', obj) for obj in data) # TODO deg/rad
    @end_angle = (-angle for angle in end_angle)
    @angle = new Array(@start_angle.length)
    for i in [0..@start_angle.length-1]
      @angle[i] = @end_angle[i] - @start_angle[i]
    @direction = new Array(@data.length)
    for i in [0..@data.length-1]
      dir = @glyph_props.select('direction', data[i])
      if dir == 'clock' then @direction[i] = false
      else if dir == 'anticlock' then @direction[i] = true
      else @direction[i] = NaN
    #duped
    @selected_mask = new Array(data.length-1)
    for i in [0..@selected_mask.length-1]
      @selected_mask[i] = false

  _render: () ->
    [@sx, @sy] = @plot_view.map_to_screen(@x, @glyph_props.x.units, @y, @glyph_props.y.units)
    @inner_radius = @distance(@data, 'x', 'inner_radius', 'edge')
    @outer_radius = @distance(@data, 'x', 'outer_radius', 'edge')

    ctx = @plot_view.ctx

    ctx.save()
    #duped
    selected = @mget_obj('data_source').get('selected')
    for idx in selected
      @selected_mask[idx] = true
    if @glyph_props.fast_path
      @_fast_path(ctx)
    else
      ##duped in many classes
      if selected and selected.length and @nonselection_glyphprops
        if @selection_glyphprops
          props =  @selection_glyphprops
        else
          props = @glyph_props
        @_full_path(ctx, props, 'selected')
        @_full_path(ctx, @nonselection_glyphprops, 'unselected')
      else
        @_full_path(ctx)
      ##duped in many classes
    ctx.restore()

  _fast_path: (ctx) ->
    if @do_fill
      @glyph_props.fill_properties.set(ctx, @glyph_props)
      for i in [0..@sx.length-1]
        if isNaN(@sx[i] + @sy[i] + @inner_radius[i] + @outer_radius[i] + @start_angle[i] + @end_angle[i])
          continue

        ctx.translate(@sx[i], @sy[i])
        ctx.rotate(@start_angle[i])

        ctx.moveTo(@outer_radius[i], 0)
        ctx.beginPath()
        ctx.arc(0, 0, @outer_radius[i], 0, @angle[i], @direction[i])
        ctx.rotate(@angle[i])
        ctx.lineTo(@inner_radius[i], 0)
        ctx.arc(0, 0, @inner_radius[i], 0, -@angle[i], not @direction[i])
        ctx.closePath()
        ctx.fill()

        ctx.rotate(-@angle[i]-@start_angle[i])
        ctx.translate(-@sx[i], -@sy[i])

    if @do_stroke
      @glyph_props.line_properties.set(ctx, @glyph_props)
      ctx.beginPath()
      for i in [0..@sx.length-1]
        if isNaN(@sx[i] + @sy[i] + @inner_radius[i] + @outer_radius[i] + @start_angle[i] + @end_angle[i])
          continue

        ctx.translate(@sx[i], @sy[i])
        ctx.rotate(@start_angle[i])

        ctx.moveTo(@outer_radius[i], 0)
        ctx.arc(0, 0, @outer_radius[i], 0, @angle[i], @direction[i])
        ctx.rotate(@angle[i])
        ctx.lineTo(@inner_radius[i], 0)
        ctx.arc(0, 0, @inner_radius[i], 0, -@angle[i], not @direction[i])
        ctx.closePath()

        ctx.rotate(-@angle[i]-@start_angle[i])
        ctx.translate(-@sx[i], -@sy[i])

      ctx.stroke()


  _full_path: (ctx, glyph_props, use_selection) ->
    #duped
    if not glyph_props
      glyph_props = @glyph_props
    for i in [0..@sx.length-1]
      if isNaN(@sx[i] + @sy[i] + @inner_radius[i] + @outer_radius[i] + @start_angle[i] + @end_angle[i])
        continue
      #duped
      if use_selection == 'selected' and not @selected_mask[i]
        continue
      if use_selection == 'unselected' and @selected_mask[i]
        continue
      ctx.translate(@sx[i], @sy[i])
      ctx.rotate(@start_angle[i])

      ctx.moveTo(@outer_radius[i],0)
      ctx.beginPath()
      ctx.arc(0, 0, @outer_radius[i], 0, @angle[i], @direction[i])
      ctx.rotate(@angle[i])
      ctx.lineTo(@inner_radius[i], 0)
      ctx.arc(0, 0, @inner_radius[i], 0, -@angle[i], not @direction[i])
      ctx.closePath()

      ctx.rotate(-@angle[i]-@start_angle[i])
      ctx.translate(-@sx[i], -@sy[i])

      if @do_fill
        glyph_props.fill_properties.set(ctx, @data[i])
        ctx.fill()

      if @do_stroke
        glyph_props.line_properties.set(ctx, @data[i])
        ctx.stroke()

  draw_legend: (ctx, x1, x2, y1, y2) ->
    glyph_props = @glyph_props
    line_props = glyph_props.line_properties
    fill_props = glyph_props.fill_properties
    ctx.save()
    reference_point = @get_reference_point()
    if reference_point?
      glyph_settings = reference_point
      outer_radius = @distance([reference_point],'x', 'outer_radius', 'edge')
      outer_radius = outer_radius[0]
      inner_radius = @distance([reference_point],'x', 'inner_radius', 'edge')
      inner_radius = inner_radius[0]
      start_angle = -@glyph_props.select('start_angle', reference_point)
      end_angle = -@glyph_props.select('end_angle', reference_point)
    else
      glyph_settings = glyph_props
      start_angle = -0.1
      end_angle = -3.9

    angle = end_angle - start_angle
    direction = @glyph_props.select('direction', glyph_settings)
    direction = if direction == "clock" then false else true
    border = line_props.select(line_props.line_width_name, glyph_settings)
    d = _.min([Math.abs(x2-x1), Math.abs(y2-y1)])
    d = d - 2 * border
    r = d / 2
    if outer_radius? or inner_radius?
      ratio = r / outer_radius
      outer_radius = r
      inner_radius = inner_radius * ratio
    else
      outer_radius = r
      inner_radius = r/2
    sx = (x1 + x2) / 2.0
    sy = (y1 + y2) / 2.0
    ctx.translate(sx, sy)
    ctx.rotate(start_angle)
    ctx.moveTo(outer_radius, 0)
    ctx.beginPath()
    ctx.arc(0, 0, outer_radius, 0, angle, direction)
    ctx.rotate(angle)
    ctx.lineTo(inner_radius, 0)
    ctx.arc(0, 0, inner_radius, 0, -angle, not direction)
    ctx.closePath()

    fill_props.set(ctx, glyph_settings)
    ctx.fill()
    line_props.set(ctx, glyph_settings)
    ctx.stroke()

    ctx.restore()
  ##duped
  select : (xscreenbounds, yscreenbounds) ->
    xscreenbounds = [@plot_view.view_state.sx_to_device(xscreenbounds[0]),
      @plot_view.view_state.sx_to_device(xscreenbounds[1])]
    yscreenbounds = [@plot_view.view_state.sy_to_device(yscreenbounds[0]),
      @plot_view.view_state.sy_to_device(yscreenbounds[1])]
    xscreenbounds = [_.min(xscreenbounds), _.max(xscreenbounds)]
    yscreenbounds = [_.min(yscreenbounds), _.max(yscreenbounds)]
    selected = []
    for i in [0..@sx.length-1]
      if xscreenbounds
        if @sx[i] < xscreenbounds[0] or @sx[i] > xscreenbounds[1]
          continue
      if yscreenbounds
        if @sy[i] < yscreenbounds[0] or @sy[i] > yscreenbounds[1]
          continue
      selected.push(i)
     return selected



class AnnularWedge extends Glyph
  default_view: AnnularWedgeView
  type: 'GlyphRenderer'


AnnularWedge::display_defaults = _.clone(AnnularWedge::display_defaults)
_.extend(AnnularWedge::display_defaults, {

  direction: 'anticlock'

  fill: 'gray'
  fill_alpha: 1.0

  line_color: 'red'
  line_width: 1
  line_alpha: 1.0
  line_join: 'miter'
  line_cap: 'butt'
  line_dash: []
  line_dash_offset: 0

})


exports.AnnularWedge = AnnularWedge
exports.AnnularWedgeView = AnnularWedgeView
