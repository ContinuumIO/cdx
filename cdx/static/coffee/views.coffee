$CDX = window.$CDX
$CDX.Views = {}

class $CDX.Views.NamespaceViewer extends Backbone.View
  render: () ->
    console.log('namespaceviewer render')
    variable_item_template = $('#variable-item-template').html()
    """
    $.when($CDX.IPython.namespace.get('variables')).then( (array) =>
      window.namespace = array
      funcs = _.filter(array, (obj) -> obj.type == 'function')
      reg_variables = _.reject(array, (obj) -> obj.type in ['function', 'module'])
      grouped = _.groupBy(reg_variables, (obj) -> obj.type)
      $(this.el).html(
        _.template2(variable_item_template,
          reg_variables:grouped, funcs:funcs))
      )
    """

class $CDX.Views.SummaryView extends Backbone.View
  render: () ->
    console.log('summaryView render')
    summary_template = $('#variable-summary-template').html()
    snip2 = ''
    $.when($CDX.arrayserver.get_summary($CDX.IPython.namespace.get('variables'), (array) ->
      for sa_ele in array
        snip2 += _.template2(summary_template, {item:sa_ele})
      ))
    .then(=>
      $(this.el).html(snip2) )
    return $(this.el)

class $CDX.Views.ConfigurePublishView extends Backbone.View
  initialize : (options) ->
    super(options)
    @tab_view = options['tab_view']
    @render()

  render : () ->
    @publishmodel = Continuum.Collections['PublishModel'].create({}, {'local': true})
    docid = $CDX.docid
    modelid = @publishmodel.id
    @puburl = "/cdx/#{docid}/published/#{modelid}"

    template = $('#publish-selection').html()
    tabs = _.keys(@tab_view.tab_view_dict)
    array_routes = []
    plot_routes = []
    plot_titles = []
    array_titles = []
    for x in tabs
      view = @tab_view.tab_view_dict[x].view
      if view.model
        if view.model.type == 'Plot' || view.model.type == 'GridPlotContainer'
          plot_routes.push(x)
          plot_titles.push(@tab_view.tab_view_dict[x].tab_name)
        if view.model.type == 'DataTable'
          array_routes.push(x)
          array_titles.push(@tab_view.tab_view_dict[x].tab_name)
    @$el.html(
      _.template2(template,
          plot_routes : plot_routes
          array_routes : array_routes
          plot_titles : plot_titles
          array_titles : array_titles
          puburl : "http://" + window.location.host + @puburl
      )
    )
    @$el.modal('show')
    return null

  events :
    "click .publishsubmit" : "publishsubmit"

  publishsubmit : () ->
    plots = []
    plot_tab_info = []
    arrays = []
    array_tab_info = []
    for node in @$el.find('input:checked')
      node = $(node)
      tab = node.attr('tab')
      tvo = @tab_view.tab_view_dict[tab]
      view = tvo.view
      if view.model.type == 'Plot' || view.model.type == 'GridPlotContainer'
        view.model.save()
        plots.push(view.model.ref())
        plot_tab_info.push({'tab_name' : tvo.tab_name, 'route' :tvo.route})
      if view.model.type == 'DataTable'
        view.model.save()
        view.model.get_ref('data_source').save()
        console.log(view.model.id, view.model.get_ref('data_source').id)
        arrays.push(view.model.ref())
        array_tab_info.push({'tab_name' : tvo.tab_name, 'route' :tvo.route})

    @publishmodel.set(
      plot_tab_info : plot_tab_info
      plots : plots
      arrays : arrays
      array_tab_info : array_tab_info
    )
    @publishmodel.save()
    @$el.modal('hide')
    window.open(@puburl, '_blank')



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
      {'render_loop': true, 'scale' : 0.2})

    window.pc_created_views = created_views
    window.pc_views = @views
    return null

  events :
    'click .jsp' : 'newtab'
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

  newtab : (e) =>
    plotnum = parseInt($(e.currentTarget).attr('data-plot_num'))
    s_pc = @model.resolve_ref(@mget('children')[plotnum])
    plotview = new s_pc.default_view(model: s_pc, render_loop:true)
    $CDX.main_tab_set.add_tab(
      tab_name:s_pc.get('title'),
      view: plotview,
      route:s_pc.get('id')
    )
    $CDX.main_tab_set.activate(s_pc.get('id'))

  render : () ->
    super()
    @build_children()
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



class $CDX.Views.PublishView extends Continuum.ContinuumView
  initialize : (options) ->
    @tab_view = options['tab_view']
    @plots = {}
    @arrays = {}
    @render()
  render : () ->
    Continuum.build_views(@model, @plots, @mget('plots'), {'render_loop':true})
    Continuum.build_views(@model, @arrays, @mget('arrays'))
    for info, idx in @mget('plot_tab_info')
      plotid = @mget('plots')[idx].id
      console.log('ADDTAB', info)
      @tab_view.add_tab(
        tab_name: info.tab_name , view: @plots[plotid], route : info.route
      )
    for info, idx in @mget('array_tab_info')
      arrayid = @mget('arrays')[idx].id
      console.log('ADDTAB', info)
      @tab_view.add_tab(
        tab_name: info.tab_name , view: @arrays[arrayid], route : info.route
      )


$CDX.Views.Layout = Backbone.Marionette.Layout.extend(
  template: "#layout-template",

  regions: {
    viz_tab: "viz-tab"
    }
  events:
    "click .js-navigate" : (e) ->
      el = $(e.currentTarget)
      route_target = el.attr("data-route_target")
      $CDX.router.navigate(route_target, {trigger: true})
    "click .js-toggle_py_pane": (e) ->
      if @pystate == 'normal'
        @pystate = 'hidden'
        $('#main-tab-area').removeClass('span5')
        $('#main-tab-area').addClass('span10')

        $('#main-tab-area').show()
        $('#cdxPyPane').hide()
      else if @pystate == 'hidden'
        @pystate = 'max'
        $('#cdxPyPane').removeClass('span5')
        $('#cdxPyPane').addClass('span10')

        $('#main-tab-area').hide()
        $('#cdxPyPane').show()
      else if @pystate =='max'
        @pystate = 'normal'
        $('#cdxPyPane').removeClass('span10')
        $('#cdxPyPane').addClass('span5')
        $('#main-tab-area').removeClass('span10')
        $('#main-tab-area').addClass('span5')

        $('#main-tab-area').show()
        $('#cdxPyPane').show()


  pystate: 'normal'
  )

$CDX.pystate = 'normal'
$CDX.togglePyPane = () ->
