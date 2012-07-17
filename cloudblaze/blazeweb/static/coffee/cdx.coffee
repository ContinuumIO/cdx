# CDX Coffee Script
#
# This is the main script file for the CDX app.

# module setup stuff
window.$CDX = {}
$CDX = window.$CDX
$CDX.IPython = {}

window.$CDX.resizeRoot = () ->
  winHeight = $(window).height()
  winWidth = $(window).width()
  cdxRootHeight=(winHeight * .85)
  midPanelHeight = (cdxRootHeight * .85)
  pyEdPaneHeight = midPanelHeight

  $('#cdxRoot').height(cdxRootHeight)
  $('.midPanel').height(midPanelHeight)
  $('#cdxMidContainer').width(winWidth * .95)
  #$('.cdx-py-pane').width(winWidth * .85)
  $('.cdx-py-pane').height(pyEdPaneHeight)
  $('.pane').height(midPanelHeight)
  $('.pane-holder').height(midPanelHeight)

$CDX.resize_loop = () ->
  window.$CDX.resizeRoot()
#  IPython.notebook.scroll_to_bottom()
  resizeTimer = setTimeout($CDX.resize_loop, 500)

# blaze_doc_loaded is a better name, doc_loaded could be confused with
# the dom event
$CDX._tab_rendered = $.Deferred()
$CDX.tab_rendered = $CDX._tab_rendered.promise()
$CDX._doc_loaded = $.Deferred()
$CDX.doc_loaded = $CDX._doc_loaded.promise()
$CDX._ipython_loaded = $.Deferred()
$CDX.ipython_loaded = $CDX._ipython_loaded.promise()

$CDX._basetabs_rendered = $.Deferred()
$CDX.basetabs_rendered = $CDX._basetabs_rendered.promise()

$CDX.add_blaze_table_tab = (varname, url, columns) ->
  data_source = Continuum.Collections['ObjectArrayDataSource'].create(
    {}, {local:true})

  $.get("/data" + url, {}, (data) ->
    arraydata = JSON.parse(data)
    transformed = []
    for row in arraydata['data']
      transformedrow = {}
      for temp in _.zip(row, arraydata['colnames'])
        [val, colname] = temp
        transformedrow[colname] = val
      transformed.push(transformedrow)
    data_source.set('data', transformed)
    datatable = Continuum.Collections['DataTable'].create(
      columns : arraydata['colnames'],
      data_source : data_source.ref()
      name : varname
      url : url
      total_rows: arraydata['shape'][0]
      , local : true
    )
    view = new datatable.default_view model : datatable
    tabelement = $CDX.main_tab_set.add_tab_el(
      tab_name:varname , view: view, route : varname)
  )

$(() ->

  $CDX.utility = {
    instantiate_main_tab_set : () ->
      if $CDX._tab_rendered.isResolved()
        return
      $.when($CDX.layout_render).then( ->
        $("#layout-root").prepend($CDX.layout_render.el)
        $CDX.main_tab_set = new $CDX.TabSet(
          el:$("#main-tab-area")
          tab_view_objs: []
        )
        $CDX._tab_rendered.resolve()
        return null
      )
    instantiate_base_tabs : () ->
      if $CDX._basetabs_rendered.isResolved()
        return
      @instantiate_main_tab_set()
      $.when($CDX.tab_rendered).then( ->
        plotcontext = Continuum.resolve_ref($CDX.plot_context_ref['collections'],
          $CDX.plot_context_ref['type'], $CDX.plot_context_ref['id'])
        plotcontextview = new plotcontext.default_view(
          model : plotcontext,
          render_loop: true
        )
        window.pc = plotcontext
        window.pcv = plotcontextview
        $CDX.main_tab_set.add_tab(
          {view: $CDX.summaryView, route:'main', tab_name:'Summary'}
        )
        $CDX.main_tab_set.add_tab(
          {view : plotcontextview, route:'viz', tab_name: 'viz'}
        )
        $CDX._basetabs_rendered.resolve()
        return null
      )


    instantiate_doc : (docid) ->
      if not $CDX._doc_loaded.isResolved()
        $.get("/cdxinfo/#{docid}", {}, (data) ->
          data = JSON.parse(data)
          $CDX.plot_context_ref = data['plot_context_ref']
          $CDX.docid = data['docid'] # in case the server returns a different docid
          Continuum.docid = $CDX.docid
          $CDX.all_models = data['all_models']
          Continuum.load_models($CDX.all_models)
          ws_conn_string = "ws://#{window.location.host}/sub"
          socket = Continuum.submodels(ws_conn_string, $CDX.docid)

          $CDX.IPython.kernelid = data['kernelid']
          $CDX.IPython.notebookid = data['notebookid']
          $CDX.IPython.baseurl = data['baseurl']
          $CDX.resize_loop()
          $CDX._doc_loaded.resolve($CDX.docid)
        )

    instantiate_ipython: (docid) ->
      if not $CDX._ipython_loaded.isResolved()
          IPython.loadfunc()
          IPython.start_notebook()
          _.delay(
            () =>
              $CDX.IPython.inject_plot_client($CDX.docid)
            , 1000
          )
  }

  WorkspaceRouter = Backbone.Router.extend(
    routes: {
      "cdx" : "load_default_document",
      "cdx/unknown/sharecurrent": "sharecurrent",
      "cdx/:docid": "load_doc",
      "cdx/:docid/share": "share",
      "cdx/:docid/published/:modelid" : "load_published"
      },

    load_published : (docid, modelid) ->
      $('#cdxMenu').hide()
      $('#cdxnamespace').hide()
      $('#cdxPyPane').hide()
      $('#main-tab-area').removeClass('span5')
      $('#main-tab-area').addClass('span12')

      $CDX.utility.instantiate_doc(docid)
      $CDX.utility.instantiate_main_tab_set()
      $.when($CDX.doc_loaded).then(()->
        $.when($CDX.tab_rendered).then(() ->
          model = Continuum.Collections['PublishModel'].get(modelid)
          view = new model.default_view(
            model : model
            tab_view : $CDX.main_tab_set
          )
        )
      )
    load_default_document : () ->
      user = $.get('/userinfo/', {}, (data) ->
        docs = JSON.parse(data)['docs']
        console.log('URL', "cdx/#{docs[0]}")
        $CDX.router.navigate("cdx/#{docs[0]}", {trigger : true})
      )

    share : (docid) ->
      $CDX.docid = docid
      $CDX.utility.instantiate_doc(docid)
      $.when($CDX.doc_loaded).then(
        () ->
          $CDX.utility.instantiate_ipython(docid)
          $CDX.utility.instantiate_base_tabs()
          view = new ConfigurePublishView({'tab_view' : $CDX.main_tab_set})
      )

    sharecurrent : (docid) ->
      console.log('SHARE CURRENT')
      docid = $CDX.docid
      $CDX.router.navigate("cdx/#{docid}/share", {trigger : true})

    load_doc : (docid) ->
      $CDX.docid = docid
      $CDX.utility.instantiate_doc(docid)
      $.when($CDX.doc_loaded).then(
        () ->
          $CDX.utility.instantiate_base_tabs()
          $CDX.utility.instantiate_ipython(docid)
      )
      console.log('RENDERING')
  )

  MyApp = new Backbone.Marionette.Application()

  Layout = Backbone.Marionette.Layout.extend(
    template: "#layout-template",

    regions: {
      viz_tab: "viz-tab"
      }
    events:
      "click .js-navigate" : (e) ->
        el = $(e.currentTarget)
        route_target = el.attr("data-route_target")
        $CDX.router.navigate(route_target, {trigger: true})
    )

  class SummaryView extends Backbone.View
    render: () ->
      console.log('summaryView render')
      summary_template = $('#variable-summary-template').html()
      snip2 = ''
      $.when($CDX.blaze.get_summary($CDX.IPython.namespace.get('variables'), (array) ->
        for sa_ele in array
          snip2 += _.template2(summary_template, {item:sa_ele})
        ))
      .then(=>
        $(this.el).html(snip2) )
      return $(this.el)


  $CDX.summaryView = new SummaryView()
  $CDX.layout = new Layout()
  $CDX.router = new WorkspaceRouter()
  $CDX.layout_render = $CDX.layout.render()
  $.when($CDX.layout_render).then( ->
    $("#layout-root").prepend($CDX.layout_render.el)
  )
  console.log("history start", Backbone.history.start(pushState:true))
  $CDX.IPython.namespace.on('change', -> $CDX.summaryView.render())

  )


_.delay(
  () ->
    $('#menuDataSelect').click( -> $CDX.showModal('#dataSelectModal'))
    $CDX.resize_loop
  , 1000
)


$CDX.popDataTab = (itemName, url, totalRows) ->
  $.when($CDX.add_blaze_table_tab(itemName, url)).then(->
    $CDX.main_tab_set.activate(itemName))

$CDX.addDataArray = (itemName, url, totalRows) ->
  itemName = $CDX.IPython.suggest_variable_name(url)
  command = "#{itemName} = bc.blaze_source('#{url}')"
  console.log(command)
  $CDX.IPython.execute_code(command)
  $CDX.add_blaze_table_tab(itemName, url)

$CDX.buildTreeNode = (tree, treeData, depth) ->
    #console.log(JSON.stringify(treeData));
    loopCount = 0
    $.each(treeData, () ->
        loopCount++
        urlStr = JSON.stringify(this.url)
        #console.log('##\nurl='+urlStr+'\n')
        #console.log('type='+JSON.stringify(this.type)+'\n##')
        itemName = this.url.split('/').reverse()[0]
        if (this.type == 'group')
          itemID = 'item-' + depth


          for i in [0..depth]
            #itemID = itemID + '-' + i
            itemID = "#{itemID}-#{i}"
          tmp = "<li><input type='checkbox' id='#{itemID}' />"
          tmp += "<label for='#{itemID}'> #{itemName}</label><ul>"


          tree = tree + tmp
          tree = $CDX.buildTreeNode(tree, this.children, ++depth)
          tree = tree + '\n</ul></li>'

        if (this.type == 'array' || this.type =='disco')
          tmp = "<li><a href='#' onClick=\"$CDX.addDataArray('#{itemName}','#{this.url}')\">#{itemName}</a></li>"

          #tmp = "<li><a class='js-blaze_click' href='#' data-blaze-url='#{this.url}'>#{itemName}</a></li>"

          tree = tree + tmp
    ) if treeData
    return tree

$CDX.showModal = (modalID) ->
    $(modalID).empty()
    $.get('/metadata/', {}, (data) ->
        treeData = $.parseJSON(data)
        treeRoot = $('#tree-template').html()
        tree = $CDX.buildTreeNode(treeRoot, treeData.children, 0)
        tree = tree + '</ul></li></ul></div></div>'
        $(modalID).append(tree)
        $(modalID).modal('show')
        #console.log(tree)
    )
    return

$CDX.togglePyPane = () ->
  console.log('togglepypane')
  #  $("#cdxPyPane").slideToggle()


class ConfigurePublishView extends Backbone.View
  initialize : (options) ->
    super(options)
    @tab_view = options['tab_view']
    @render()

  render : () ->
    template = $('#publish-selection').html()
    tabs = _.keys(@tab_view.tab_view_dict)
    arrays = []
    plots = []
    for x in tabs
      view = @tab_view.tab_view_dict[x].view
      if view.model
        if view.model.type == 'Plot' || view.model.type == 'GridPlotContainer'
          plots.push(x)
        if view.model.type == 'DataTable'
          arrays.push(x)
    @$el.html(_.template2(template, {'plots' : plots, 'arrays' : arrays}))
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

    publishmodel = Continuum.Collections['PublishModel'].create(
      plot_tab_info : plot_tab_info
      plots : plots
      arrays : arrays
      array_tab_info : array_tab_info
    )
    docid = $CDX.docid
    modelid = publishmodel.id
    window.open("/cdx/#{docid}/published/#{modelid}", '_blank')
    @$el.modal('hide')
class PublishView extends Continuum.ContinuumView
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
      @tab_view.add_tab_el(
        tab_name: info.tab_name , view: @plots[plotid], route : info.route
      )
    for info, idx in @mget('array_tab_info')
      arrayid = @mget('arrays')[idx].id
      console.log('ADDTAB', info)
      @tab_view.add_tab_el(
        tab_name: info.tab_name , view: @arrays[arrayid], route : info.route
      )

class PublishModel extends Continuum.HasProperties
  collections : Continuum.Collections
  type : 'PublishModel'
  default_view : PublishView
  defaults :
    plot_tab_info : []
    plots : []
    arrays : []
    array_tab_info : []

class PublishModels extends Backbone.Collection
  model : PublishModel

Continuum.register_collection('PublishModel', new PublishModels())


add_plot = ->
  $CDX.IPython.execute_code("p.line(x=[1,2,3,4,5], y=[1,2,3,4,5])")

class CDXPlotContextView extends Continuum.ContinuumView
  initialize : (options) ->
    @views = {}
    @views_rendered = [false]
    @child_models = []
    super(options)
    @render()

  delegateEvents: ->
    safebind(this, @model, 'destroy', @remove)
    safebind(this, @model, 'change', @render)
    super()

  generate_remove_child_callback : (view) ->
    callback = () =>
      return null
    return callback

  build_children : () ->
    view_specific_options = []
    for spec, plot_num in @mget('children')
      model = @model.resolve_ref(spec)
      @child_models[plot_num] = model
      view_specific_options.push({'el' : $("<div/>")})

    created_views = build_views(
      @model, @views, @mget('children'), {}, view_specific_options)
    window.pc_created_views = created_views
    window.pc_views = @views
    return null

  events :
    'click .jsp' : 'newtab'
    'click .plotclose' : 'removeplot'

  removeplot : (e) =>
    plotnum = parseInt($(e.currentTarget).parent().attr('data-plot_num'))
    s_pc = @model.resolve_ref(@mget('children')[plotnum])
    view = @views[s_pc.get('id')].remove();
    newchildren = (x for x in @mget('children') when x.id != view.model.id)
    @mset('children', newchildren)
    @model.save()
    return false

  newtab : (e) =>
    plotnum = parseInt($(e.currentTarget).attr('data-plot_num'))
    s_pc = @model.resolve_ref(@mget('children')[plotnum])
    plotview = new s_pc.default_view(model: s_pc, render_loop:true)
    $CDX.main_tab_set.add_tab_el(
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
      $.when(view.to_png_daturl()).then((data_url) =>
        tab_name = $CDX.IPython.suggest_variable_name
        renderobj =
          data_url : data_url
          index : index
          title : view.model.get('title')
        to_render.push(renderobj)
      )
    template = _.template2($('#plot-context').html())
    html = template(to_render : to_render)
    @$el.html(html)
    return null

class CDXPlotContext extends Component
  type : 'CDXPlotContext',
  default_view : CDXPlotContextView
  url : () ->

    return super()
  defaults :
    children : []
    render_loop : true

class CDXPlotContexts extends Backbone.Collection
  model : CDXPlotContext

Continuum.register_collection('CDXPlotContext', new CDXPlotContexts())
$CDX.pystate = 'normal'
$CDX.togglePyPane = () ->
  if $CDX.pystate == 'normal'
    $CDX.pystate = 'hidden'
    $('#main-tab-area').removeClass('span5')
    $('#main-tab-area').addClass('span10')

    $('#main-tab-area').show()
    $('#cdxPyPane').hide()
  else if $CDX.pystate == 'hidden'
    $CDX.pystate = 'max'
    $('#cdxPyPane').removeClass('span5')
    $('#cdxPyPane').addClass('span10')

    $('#main-tab-area').hide()
    $('#cdxPyPane').show()
  else if $CDX.pystate =='max'
    $CDX.pystate = 'normal'
    $('#cdxPyPane').removeClass('span10')
    $('#cdxPyPane').addClass('span5')
    $('#main-tab-area').removeClass('span10')
    $('#main-tab-area').addClass('span5')

    $('#main-tab-area').show()
    $('#cdxPyPane').show()
