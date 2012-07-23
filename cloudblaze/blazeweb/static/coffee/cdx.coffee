
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
  datatable = Continuum.Collections['DataTable'].create(
    data_source : data_source.ref()
    name : varname
    url : url
  ,
    local : true
  )
  datatable.load(0)
  view = new datatable.default_view ({model : datatable})
  tabelement = $CDX.main_tab_set.add_tab(
    tab_name:varname , view: view, route : varname
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
        $CDX.namespaceViewer.el = $("#left-panel");
        $CDX.namespaceViewer.render()
        $CDX.main_tab_set.add_tab(
          {view: $CDX.summaryView, route:'main', tab_name:'Summary'}
        )
        $CDX.main_tab_set.add_tab(
          {view : plotcontextview, route:'viz', tab_name: 'viz'}
        )
        $CDX._basetabs_rendered.resolve()
        Continuum.Collections.Plot.on('add', (model, b) ->
          $CDX.utility.add_plot_tab(model)
        )
        Continuum.Collections.GridPlotContainer.on('add', (model, b) ->
          $CDX.utility.add_plot_tab(model)
        )
        return null
      )

    add_plot_tab : (model) ->
      pview = new model.default_view({model:model, render_loop:true})
      $CDX.main_tab_set.add_tab(
        {view: pview , route: model.get('id'), tab_name: model.get('title')})
      $CDX.main_tab_set.activate(model.get('id'))

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
          $CDX.utility.instantiate_base_tabs()
          $CDX.utility.instantiate_ipython(docid)
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



  $CDX.namespaceViewer = new $CDX.Views.NamespaceViewer()
  $CDX.summaryView = new $CDX.Views.SummaryView()
  $CDX.layout = new Layout()
  $CDX.router = new WorkspaceRouter()
  $CDX.layout_render = $CDX.layout.render()
  $.when($CDX.layout_render).then( ->
    $("#layout-root").prepend($CDX.layout_render.el)
  )
  console.log("history start", Backbone.history.start(pushState:true))
  $CDX.IPython.namespace.on('change', ->
    $CDX.namespaceViewer.render()
    $CDX.summaryView.render())

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


window.add_plot = ->
  $CDX.IPython.execute_code("p.line(x=[1,2,3,4,5], y=[1,2,3,4,5])")

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
