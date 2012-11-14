if not window.$CDX
  window.$CDX = {}
$CDX = window.$CDX
if not $CDX.Models
  $CDX.Models = {}
if not $CDX.Collections
  $CDX.Collections = {}
if not $CDX.Views
  $CDX.Views = {}

$CDX = window.$CDX

class $CDX.Views.CDXPlotContextView extends Continuum.ContinuumView
  initialize : (options) ->
    @views = {}
    @views_rendered = [false]
    @child_models = []
    super(options)
    @render()

  delegateEvents: ->
    Continuum.safebind(this, @model, 'destroy', @remove)
    Continuum.safebind(this, @model, 'change', @render)
    super()

  generate_remove_child_callback : (view) ->
    callback = () =>
      return null
    return callback

  build_children : () ->
    created_views = Continuum.build_views(
      @model, @views, @mget('children'),
      {'render_loop': true, 'scale' : 1.0})

    window.pc_created_views = created_views
    window.pc_views = @views
    return null

  events :
    #'click .jsp' : 'newtab'
    'click .plotclose' : 'removeplot'

  removeplot : (e) =>
    plotnum = parseInt($(e.currentTarget).parent().attr('data-plot_num'))
    s_pc = @model.resolve_ref(@mget('children')[plotnum])
    view = @views[s_pc.get('id')]
    view.remove();
    newchildren = (x for x in @mget('children') when x.id != view.model.id)
    @mset('children', newchildren)
    @model.save()
    return false

  render : () ->
    super()
    @build_children()
    for own key, val of @views
      val.$el.detach()
    @$el.html('')
    to_render = []
    tab_names = {}
    for modelref, index in @mget('children')
      view = @views[modelref.id]
      node = $("<div class='jsp' data-plot_num='#{index}'></div>"  )
      @$el.append(node)
      title = view.model.get('title')
      node.append($("<p>#{title}</p>"))
      node.append($("<a class='plotclose'>[close]</a>"))
      node.append(view.el)
    return null
