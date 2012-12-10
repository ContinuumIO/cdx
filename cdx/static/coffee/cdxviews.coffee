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
    'click .closeall' : 'closeall'
    'keydown .plottitle' : 'savetitle'
  size_textarea : (textarea) ->
    scrollHeight = $(textarea).height(0).prop('scrollHeight')
    $(textarea).height(scrollHeight)

  savetitle : (e) =>
    if e.keyCode == 13 #enter
      e.preventDefault()
      plotnum = parseInt($(e.currentTarget).parent().attr('data-plot_num'))
      s_pc = @model.resolve_ref(@mget('children')[plotnum])
      s_pc.set('title', $(e.currentTarget).val())
      s_pc.save()
      $(e.currentTarget).blur()
      return false
    @size_textarea($(e.currentTarget))

  closeall : (e) =>
    @mset('children', [])
    @model.save()

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
    @$el.append("<div><a class='closeall' href='#'>Close All Plots</a></div>")
    @$el.append("<br/>")
    to_render = []
    tab_names = {}
    for modelref, index in @mget('children')
      view = @views[modelref.id]
      node = $("<div class='jsp' data-plot_num='#{index}'></div>"  )
      @$el.append(node)
      title = view.model.get('title')
      node.append($("<textarea class='plottitle'>#{title}</textarea>"))
      node.append($("<a class='plotclose'>[close]</a>"))
      node.append(view.el)
    _.defer(() =>
      for textarea in @$el.find('.plottitle')
        @size_textarea($(textarea))
    )
    return null

class PlotContextViewState extends Continuum.HasProperties
  defaults :
    maxheight : 600
    maxwidth : 600
    selected : 0

class $CDX.Views.CDXPlotContextViewWithMaximized extends $CDX.Views.CDXPlotContextView
  initialize : (options) ->
    @selected = 0
    @viewstate = new PlotContextViewState(
      maxheight : options.maxheight
      maxwidth : options.maxwidth
    )
    super(options)
    Continuum.safebind(this, @viewstate, 'change', @render)
    Continuum.safebind(this, @model, 'change:children', () =>
      selected = @viewstate.get('selected')
      if selected > @model.get('children') - 1
        @viewstate.set('selected', 0)
    )
  events :
    'click .maximize' : 'maximize'
    'click .plotclose' : 'removeplot'
    'click .closeall' : 'closeall'
    'keydown .plottitle' : 'savetitle'

  maximize : (e) ->
    plotnum = parseInt($(e.currentTarget).parent().attr('data-plot_num'))
    @viewstate.set('selected', plotnum)

  render : () ->
    super()
    @build_children()
    for own key, val of @views
      val.$el.detach()
    @$el.html('')
    main = $("<div class='plotsidebar'><div>")
    @$el.append(main)
    @$el.append("<div class='maxplot'>")
    main.append("<div><a class='closeall' href='#'>Close All Plots</a></div>")
    main.append("<br/>")
    to_render = []
    tab_names = {}
    for modelref, index in @mget('children')
      view = @views[modelref.id]
      node = $("<div class='jsp' data-plot_num='#{index}'></div>"  )
      main.append(node)
      title = view.model.get('title')
      node.append($("<textarea class='plottitle'>#{title}</textarea>"))
      node.append($("<a class='maximize'>[max]</a>"))
      node.append($("<a class='plotclose'>[close]</a>"))
      node.append(view.el)
    if @mget('children').length > 0
      modelref = @mget('children')[@viewstate.get('selected')]
      model = @model.resolve_ref(modelref)
      @maxview = new model.default_view(
        model : model
      )
    else
      @maxview = null
    @$el.find('.maxplot').append(@maxview.$el)
    _.defer(() =>
      for textarea in main.find('.plottitle')
        @size_textarea($(textarea))
      if @maxview
        width = model.get('width')
        height = model.get('height')
        maxwidth = @viewstate.get('maxwidth')
        maxheight = @viewstate.get('maxheight')
        widthratio = maxwidth/width
        heightratio = maxheight/height
        ratio = _.min([widthratio, heightratio])
        newwidth = ratio * width
        newheight = ratio * height
        @maxview.viewstate.set('height', newheight)
        @maxview.viewstate.set('width', newwidth)

    )
    return null



class $CDX.Views.CDXSinglePlotContext extends Continuum.ContinuumView
  initialize : (options) ->
    @views = {}
    @views_rendered = [false]
    @child_models = []
    @target_model_id = options.target_model_id
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

  single_plot_children : () ->
    return (x for x in @mget('children') when x.id == @target_model_id)
  build_children : () ->
    children = @single_plot_children()
    created_views = Continuum.build_views(
      @model, @views, children
    )
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
    for modelref, index in @single_plot_children()
      console.log("modelref.id ", modelref.id)
      view = @views[modelref.id]
      node = $("<div class='jsp' data-plot_num='#{index}'></div>"  )
      @$el.append(node)
      title = view.model.get('title')
      node.append($("<p>#{title}</p>"))
      node.append(view.el)
    return null
