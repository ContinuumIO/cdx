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
  midPanelHeight = (cdxRootHeight * .65)
  pyEdPaneHeight = (cdxRootHeight * .20)

  $('#cdxRoot').height(cdxRootHeight)
  $('.midPanel').height(midPanelHeight)
  $('#cdxMidContainer').width(winWidth * .95)
  $('.cdx-py-pane').width(winWidth * .85)
  $('.cdx-py-pane').height(pyEdPaneHeight)

$CDX.resize_loop = () ->
  window.$CDX.resizeRoot()
#  IPython.notebook.scroll_to_bottom()
  resizeTimer = setTimeout($CDX.resize_loop, 500)

# blaze_doc_loaded is a better name, doc_loaded could be confused with
# the dom event

$CDX._doc_loaded = $.Deferred()
$CDX.doc_loaded = $CDX._doc_loaded.promise()
$CDX._viz_instatiated = $.Deferred()
$CDX.viz_instatiated = $CDX._viz_instatiated.promise()

$CDX.add_blaze_table_tab = (varname, url, columns) ->
  data_source = Continuum.Collections['ObjectArrayDataSource'].create(
    {}, {local:true})

  deferred = $.get("/data" + url, {}, (data) ->
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
      , local : true
    )
    view = new datatable.default_view(
      model : datatable,
    )
    tabelement = $CDX.main_tab_set.add_tab_el(
      tab_name:varname , view: view, route : varname
    )
  )

$(() ->

  $CDX.utility = {
    start_instatiate: (docid) ->
      if not $CDX._doc_loaded.isResolved()
        $.get("/cdxinfo/#{docid}", {}, (data) ->
          data = JSON.parse(data)
          $CDX.plot_context_ref = data['plot_context_ref']
          $CDX.docid = data['docid'] # in case the server returns a different docid
          $CDX.all_models = data['all_models']

          $CDX.IPython.kernelid = data['kernelid']
          $CDX.IPython.notebookid = data['notebookid']
          $CDX.IPython.baseurl = data['baseurl']

          IPython.loadfunc()
          IPython.start_notebook()
          Continuum.load_models($CDX.all_models)
          ws_conn_string = "ws://#{window.location.host}/sub"
          socket = Continuum.submodels(ws_conn_string, $CDX.docid)
          console.log("resolving _doc_loaded")
          _.delay(
            () =>
              $CDX.IPython.inject_plot_client($CDX.docid)
              $CDX.resize_loop()
              $CDX._doc_loaded.resolve($CDX.docid)
              $CDX.utility.instatiate_viz_tab()
            , 1000
          )

        )
    instatiate_viz_tab: ->
      if not $CDX._viz_instatiated.isResolved()
        $.when($CDX.doc_loaded).then(->
          plotcontext = Continuum.resolve_ref($CDX.plot_context_ref['collections'],
            $CDX.plot_context_ref['type'], $CDX.plot_context_ref['id'])
          plotcontext.set('render_loop', true)
          plotcontextview = new plotcontext.default_view(
            model : plotcontext,
          )
          $CDX.main_tab_set.add_tab_el(
            tab_name:"viz",
            view: plotcontextview,
            route:"viz"
          )
          window.pc = plotcontext
          window.pcv = plotcontextview
          _.delay((->
            pv1 = _.values(window.pcv.views)[1]
            $.when(pv1.to_png_daturl()).then( (data_url) ->
              $(pcv.el).prepend($("<img src='#{data_url}'></img>")))
          ),0)
            
          
          $CDX._viz_instatiated.resolve($CDX.docid))

    instatiate_specific_viz_tab: (plot_id) ->
      if not $CDX._viz_instatiated.isResolved()
        $.when($CDX.doc_loaded).then(->
          plotcontext = Continuum.resolve_ref($CDX.plot_context_ref['collections'],
            $CDX.plot_context_ref['type'], $CDX.plot_context_ref['id'])
          s_pc_ref = plotcontext.get('children')[0]
          s_pc = Continuum.resolve_ref(
            s_pc_ref.collections, s_pc_ref.type, s_pc_ref.id)
          s_pc.set('render_loop', true)
          plotcontextview = new s_pc.default_view(
            {'model' : s_pc, 'render_loop':true, 'el' : $('#main-tab-area')});
          # plotcontextview = new s_pc.default_view(
          #     model: s_pc,
          #     el: $CDX.main_tab_set.add_tab_el(
          #       tab_name:"plot#{plot_num}",  view: {}, route:"plot#{plot_num}"))

          $CDX._viz_instatiated.resolve($CDX.docid))
  }

  WorkspaceRouter = Backbone.Router.extend({
    routes: {
      "cdx" : "load_default_document",
      "cdx/:docid":                 "load_doc",     #help
      "cdx/:docid/viz":             "load_doc_viz",     #help
      "cdx/:docid/viz/:plot_id":    "load_specific_viz",     #help
      },
    load_default_document : () ->
      user = $.get('/userinfo/', {}, (data) ->
        docs = JSON.parse(data)['docs']
        console.log('URL', "cdx/#{docs[0]}")
        $CDX.router.navigate("cdx/#{docs[0]}", {trigger : true}))

    load_doc : (docid) ->
      $CDX.docid = docid
      $CDX.utility.start_instatiate(docid)
      console.log('RENDERING')

    load_doc_viz : (docid) ->
      $CDX.utility.start_instatiate(docid)
      @navigate_doc_viz()

    load_specific_viz : (docid, plot_id) ->
      $CDX.utility.start_instatiate(docid)
      $CDX.utility.instatiate_specific_viz_tab(0)
      $.when($CDX.viz_instatiated).then(->
        console.log("navigate_doc_viz then")
        $('a[data-route_target="navigate_doc_viz"]').tab('show'))

    navigate_doc_viz: ->
      $CDX.utility.instatiate_viz_tab()
      $.when($CDX.viz_instatiated).then(->
        console.log("navigate_doc_viz then")
        $('a[data-route_target="navigate_doc_viz"]').tab('show')
        expected_path = "cdx/#{$CDX.docid}/viz"
        sliced_path = location.pathname[1..]
        if not (sliced_path == expected_path)
          console.log('paths not equal, navigating')
          $CDX.router.navigate(expected_path)
        )
      }
  )

  MyApp = new Backbone.Marionette.Application()

  Layout = Backbone.Marionette.Layout.extend(
    template: "#layout-template",

    regions: {
      viz_tab: "viz-tab"
      }
    events: {
      "click ul.nav-tabs .js-tab_trigger" : (e) ->
        el = $(e.currentTarget)
        route_target = el.attr("data-route_target")
        $CDX.router[route_target]()
        el.tab('show')
      }

    )

  class BazView extends Backbone.View
    render: () ->
      return "<h3> baz view </h3>"


  $CDX.layout = new Layout()
  $CDX.router = new WorkspaceRouter()
  $.when($CDX.layout_render = $CDX.layout.render()).then( ->


    $("#layout-root").prepend($CDX.layout_render.el);
    $CDX.main_tab_set = new TabSet(
      el:"#main-tab-area", tab_view_objs: [{view: new BazView(), route:'main', tab_name:'main'}])

    $CDX.main_tab_set.render()
    )
  console.log("history start", Backbone.history.start(pushState:true))

  )

_.delay(
  () ->
    $('#menuDataSelect').click( -> $CDX.showModal('#dataSelectModal'))
  , 1000
)

$CDX.addDataArray = (itemName) ->
  url = itemName
  itemName = itemName.split("/")
  itemName = itemName[itemName.length - 1]
  itemName = $CDX.IPython.suggest_variable_name(itemName)
  command = "#{itemName} = bc.blaze_source('#{url}')"
  console.log(command)
  $CDX.IPython.execute_code(command)

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
          tmp = "<li><a href='#' onClick=\"$CDX.addDataArray('#{this.url}')\">#{itemName}</a></li>"

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

$CDX.render_summary = ->
  sample_data = [{url: "/blaze/data/gold.hdf5/20100114/dates",
  type:"BlazeArrayProxy", name:"dates"}, 
  {colsummary: {0:{std:6759.325780745387, max:1263502799, 
  mean:1263491099.9993594, min:1263479400}}, 
  summary:{shape:[1561], colnames:[0]}}];

  #console.log(sample_data)
  summary_template = $('#variable-summary-template').html()

  #console.log(_.template(summary_template, {item:sample_data}))

$(->
  $CDX.render_summary())
  

