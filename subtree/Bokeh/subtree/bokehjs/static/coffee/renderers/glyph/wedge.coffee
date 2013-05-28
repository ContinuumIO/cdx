
properties = require('../properties')
glyph_properties = properties.glyph_properties
line_properties = properties.line_properties
fill_properties = properties.fill_properties

glyph = require('./glyph')
Glyph = glyph.Glyph
GlyphView = glyph.GlyphView


class WedgeView extends GlyphView

  initialize: (options) ->
    glyphspec = @mget('glyphspec')
    @glyph_props = new glyph_properties(
      @,
      glyphspec,
      ['x', 'y', 'radius', 'start_angle', 'end_angle', 'direction:string'],
      [
        new fill_properties(@, glyphspec),
        new line_properties(@, glyphspec)
      ]
    )

    @do_fill   = @glyph_props.fill_properties.do_fill
    @do_stroke = @glyph_props.line_properties.do_stroke
    super(options)

  _set_data: (@data) ->
    @x = @glyph_props.v_select('x', data)
    @y = @glyph_props.v_select('y', data)
    start_angle = (@glyph_props.select('start_angle', obj) for obj in data) # TODO deg/rad
    @start_angle = (-angle for angle in start_angle)
    end_angle = (@glyph_props.select('end_angle', obj) for obj in data) # TODO deg/rad
    @end_angle = (-angle for angle in end_angle)
    @direction = new Array(@data.length)
    for i in [0..@data.length-1]
      dir = @glyph_props.select('direction', data[i])
      if dir == 'clock' then @direction[i] = false
      else if dir == 'anticlock' then @direction[i] = true
      else @direction[i] = NaN

  _render: () ->
    [@sx, @sy] = @plot_view.map_to_screen(@x, @glyph_props.x.units, @y, @glyph_props.y.units)
    @radius = @distance(@data, 'x', 'radius', 'edge')

    ctx = @plot_view.ctx

    ctx.save()
    if @glyph_props.fast_path
      @_fast_path(ctx)
    else
      @_full_path(ctx)
    ctx.restore()

  _fast_path: (ctx) ->
    if @do_fill
      @glyph_props.fill_properties.set(ctx, @glyph_props)
      for i in [0..@sx.length-1]
        if isNaN(@sx[i] + @sy[i] + @radius[i] + @start_angle[i] + @end_angle[i] + @direction[i])
          continue

        ctx.beginPath()
        ctx.arc(@sx[i], @sy[i], @radius[i], @start_angle[i], @end_angle[i], @direction[i])
        ctx.lineTo(@sx[i], @sy[i])
        ctx.closePath()
        ctx.fill()

    if @do_stroke
      @glyph_props.line_properties.set(ctx, @glyph_props)
      for i in [0..@sx.length-1]
        if isNaN(@sx[i] + @sy[i] + @radius[i] + @start_angle[i] + @end_angle[i] + @direction[i])
          continue

        ctx.beginPath()
        ctx.arc(@sx[i], @sy[i], @radius[i], @start_angle[i], @end_angle[i], @direction[i])
        ctx.lineTo(@sx[i], @sy[i])
        ctx.closePath()
        ctx.stroke()

  _full_path: (ctx) ->
    for i in [0..@sx.length-1]
      if isNaN(@sx[i] + @sy[i] + @radius[i] + @start_angle[i] + @end_angle[i] + @direction[i])
        continue

      ctx.beginPath()
      ctx.arc(@sx[i], @sy[i], @radius[i], @start_angle[i], @end_angle[i], @direction[i])
      ctx.lineTo(@sx[i], @sy[i])
      ctx.closePath()

      if @do_fill
        @glyph_props.fill_properties.set(ctx, @data[i])
        ctx.fill()

      if @do_stroke
        @glyph_props.line_properties.set(ctx, @data[i])
        ctx.stroke()


class Wedge extends Glyph
  default_view: WedgeView
  type: 'GlyphRenderer'


Wedge::display_defaults = _.clone(Wedge::display_defaults)
_.extend(Wedge::display_defaults, {

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


exports.Wedge = Wedge
exports.WedgeView = WedgeView
