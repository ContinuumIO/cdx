define [
  "underscore"
  "jquery"
  "common/plot_context"
  "common/png_view"
  "common/build_views"
  "common/safebind"
], (_, $, PlotContext, PNGView, build_views, safebind) ->

  class PNGPlotView extends PlotContext.View
    initialize: (options) ->
      @thumb_x = options.thumb_x
      @thumb_y = options.thumb_y
      @views = {}
      @views_rendered = [false]
      @child_models = []
      super(options)
      @render()

    pngclick : (e) =>
      modeltype = $(e.currentTarget).attr('modeltype')
      modelid = $(e.currentTarget).attr('modelid')
      @trigger('showplot', {type : modeltype, id : modelid})

    delegateEvents: () ->
      safebind(this, @model, 'destroy', @remove)
      safebind(this, @model, 'change', @render)
      super()

    build_children: () ->
      view_classes = []
      for view_model in @mget_obj('children')
        if not view_model.get('png')
          console.log("no png for #{view_model.id} making one")
          pv = new view_model.default_view({model:view_model})
          try
            pv.save_png()
          catch error
            console.log(error)
        view_classes.push(PNGView)
      created_views = build_views(
        @views,
        @mget_obj('children'),
        {thumb_x:@thumb_x, thumb_y:@thumby},
        view_classes
      )

      window.pc_created_views = created_views
      window.pc_views = @views
      return null

    events:
      'click .plotclose': 'removeplot'
      'click .closeall': 'closeall'
      'click .pngview' : 'pngclick'
