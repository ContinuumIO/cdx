
$(window).unload(->
  #$CDX.helpWindow.close()
  )
Continuum.HasProperties.prototype.sync = Backbone.sync
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
  resizeTimer = setTimeout($CDX.resize_loop, 500)


$CDX.Deferreds = {}
$CDX.Promises = {}
# arrayserver_doc_loaded is a better name, doc_loaded could be confused with
# the dom event

$CDX.Deferreds._tab_rendered = $.Deferred()
$CDX.Promises.tab_rendered = $CDX.Deferreds._tab_rendered.promise()
$CDX.Deferreds._doc_loaded = $.Deferred()
$CDX.Promises.doc_loaded = $CDX.Deferreds._doc_loaded.promise()
$CDX.Deferreds._ipython_loaded = $.Deferred()
$CDX.Promises.ipython_loaded = $CDX.Deferreds._ipython_loaded.promise()

$CDX.Deferreds._basetabs_rendered = $.Deferred()
$CDX.Promises.basetabs_rendered = $CDX.Deferreds._basetabs_rendered.promise()



_.delay(
  () ->
    $('#menuDataSelect').click( -> $CDX.showModal('#dataSelectModal'))
    $('#helpCDX').click( -> $CDX.showHelp(event, 'cdx'))
    $('#helpPython').click( -> $CDX.showHelp(event, 'python'))
    $CDX.resize_loop
  , 1000
)

$CDX.showHelp = (event, section) ->
  """
  $CDX.helpWindow = window.open('/cdx_help?section='+section,
    'CDX Help',
    'width=600,height=600,scrollbars=yes,resizable=yes,location=no,status=yes')
  """
  event.preventDefault()
  return false
"""
window.add_plot = ->
  $CDX.IPython.execute_code("p.line(x=[1,2,3,4,5], y=[1,2,3,4,5])")
"""
$(() ->

  $CDX.utility = {
    instantiate_main_tab_set : () ->
      if $CDX.Deferreds._tab_rendered.isResolved()
        return
      $.when($CDX.layout_render).then( ->
        $("#layout-root").prepend($CDX.layout_render.el)
        $CDX.main_tab_set = new $CDX.TabSet(
          el:$("#main-tab-area")
          tab_view_objs: []
        )
        $CDX.Deferreds._tab_rendered.resolve()
        return null
      )
    instantiate_base_tabs : () ->
      if $CDX.Deferreds._basetabs_rendered.isResolved()
        return
      @instantiate_main_tab_set()
      $.when($CDX.Promises.tab_rendered).then( ->
        plotcontext = Continuum.resolve_ref($CDX.plot_context_ref['collections'],
          $CDX.plot_context_ref['type'], $CDX.plot_context_ref['id'])
        plotcontextview = new plotcontext.default_view(
          model : plotcontext,
          render_loop: true
        )
        $CDX.plotcontext = plotcontext
        $CDX.plotcontextview = plotcontextview
        $CDX.namespaceViewer.el = $("#left-panel");
        $CDX.namespaceViewer.render()
        $CDX.main_tab_set.add_tab(
          {view: $CDX.summaryView, route:'main', tab_name:'Summary'}
        )
        $CDX.main_tab_set.add_tab(
          {view : plotcontextview, route:'viz', tab_name: 'viz'}
        )
        $CDX.Deferreds._basetabs_rendered.resolve()
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
      if not $CDX.Deferreds._doc_loaded.isResolved()
        $.get("/cdxinfo/#{docid}", {}, (data) ->
          data = JSON.parse(data)
          $CDX.plot_context_ref = data['plot_context_ref']
          $CDX.docid = data['docid'] # in case the server returns a different docid
          $CDX.arrayserveraddress = data['arrayserveraddress']
          Continuum.docid = $CDX.docid
          $CDX.all_models = data['all_models']
          Continuum.load_models($CDX.all_models)
          ws_conn_string = "ws://#{window.location.host}/sub"
          socket = Continuum.submodels(ws_conn_string, $CDX.docid)

          #$CDX.IPython.kernelid = data['kernelid']
          #$CDX.IPython.notebookid = data['notebookid']
          #$CDX.IPython.baseurl = data['baseurl']
          $CDX.resize_loop()
          $CDX.Deferreds._doc_loaded.resolve($CDX.docid)
        )

    instantiate_ipython: (docid) ->
      if not $CDX.Deferreds._ipython_loaded.isResolved()
          #IPython.loadfunc()
          #IPython.start_notebook()
          _.delay((() -> a = 1+1), 1000)
  }

  WorkspaceRouter = Backbone.Router.extend(
    routes: {
      "cdx" : "load_default_document",
      "cdx/" : "load_default_document",
      "cdx/unknown/sharecurrent": "sharecurrent",
      "cdx/unknown/sharecurrent/": "sharecurrent",
      "cdx/:docid": "load_doc",
      "cdx/:docid/": "load_doc",
      "cdx/:docid/share": "share",
      "cdx/:docid/share/": "share",
      "cdx/:docid/published/:modelid" : "load_published"
      "cdx/:docid/published/:modelid/" : "load_published"
      },

    load_published : (docid, modelid) ->
      $('#cdxMenu').hide()
      $('#cdxnamespace').hide()
      $('#cdxPyPane').hide()
      $('#main-tab-area').removeClass('span5')
      $('#main-tab-area').addClass('span12')

      $CDX.utility.instantiate_doc(docid)
      $CDX.utility.instantiate_main_tab_set()

      $.when($CDX.Promises.doc_loaded, $CDX.Promises.tab_rendered).then(() ->
        model = Continuum.Collections['PublishModel'].get(modelid)
        view = new model.default_view(
          model : model
          tab_view : $CDX.main_tab_set
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
      $.when($CDX.Promises.doc_loaded).then(
        () ->
          $CDX.utility.instantiate_base_tabs()
          $CDX.utility.instantiate_ipython(docid)
          view = new $CDX.Views.ConfigurePublishView({'tab_view' : $CDX.main_tab_set})
      )

    sharecurrent : (docid) ->
      console.log('SHARE CURRENT')
      docid = $CDX.docid
      $CDX.router.navigate("cdx/#{docid}/share", {trigger : true})

    load_doc : (docid) ->
      $CDX.docid = docid
      $CDX.utility.instantiate_doc(docid)
      $.when($CDX.Promises.doc_loaded).then(() ->
        $CDX.utility.instantiate_base_tabs()
        $CDX.utility.instantiate_ipython(docid)
      )
      console.log('RENDERING')
  )

  MyApp = new Backbone.Marionette.Application()




  $CDX.namespaceViewer = new $CDX.Views.NamespaceViewer()
  $CDX.summaryView = new $CDX.Views.SummaryView()
  $CDX.layout = new $CDX.Views.Layout()
  $CDX.router = new WorkspaceRouter()
  $CDX.layout_render = $CDX.layout.render()
  $.when($CDX.layout_render).then( ->
    $("#layout-root").prepend($CDX.layout_render.el)
  )
  console.log("history start", Backbone.history.start(pushState:true))
  """
  $CDX.IPython.namespace.on('change:variables', ->
    $CDX.namespaceViewer.render()
    $CDX.summaryView.render())

  $CDX.IPython.namespace.on('change:newvars', (model, newvars, options) ->
    newvars = model.get_vars(newvars)
    for newvar in newvars
      if newvar.type == 'ArrayServerArrayProxy' or
        newvar.type == 'ArrayNode' or
        newvar.type == 'ndarray' or
        newvar.type == 'DataFrame'
          if newvar.url
            data_source = $CDX.get_arrayserver_source(newvar.url)
            data_source.load(0)
            $CDX.add_data_tab(newvar.name, data_source)
    return null
  )
  """

)
$CDX.get_arrayserver_source = (url) ->
  objid = url.replace(/\//g, "_")
  collection = Continuum.Collections['ArrayServerObjectArrayDataSource']
  data_source = collection.get(objid)
  if not data_source
    data_source = new Bokeh.ArrayServerObjectArrayDataSource(
      url : url,
      id : objid
    )
    Continuum.Collections[data_source.type].add(data_source)
  return data_source

$CDX.add_arrayserver_table_tab = (varname, data_source) ->
  if _.isString(data_source)
    data_source = $CDX.get_arrayserver_source(data_source)
  datatable = new Continuum.ui.DataTable(
    data_source : data_source.ref()
    name : varname
  )
  tableloaded = datatable.load(0)
  view = new datatable.default_view ({model : datatable})
  tabelement = $CDX.main_tab_set.add_tab(
    tab_name:varname , view: view, route : varname
  )
  $.when(tableloaded).then(() => data_source.save())


$CDX.add_data_tab = (itemName, url) ->
  $CDX.add_arrayserver_table_tab(itemName, url)
  $CDX.main_tab_set.activate(itemName)

$CDX.add_data_array = (url) ->
  console.log("add_data_array");
  if true
    return
  
  itemName = $CDX.IPython.suggest_variable_name(url)
  command = "#{itemName} = bc.get('#{url}')"
  console.log(command)
  $CDX.IPython.execute_code(command)

$CDX.buildTreeNode = (tree, treeData, depth) ->
    loopCount = 0
    $.each(treeData, () ->
        loopCount++
        urlStr = JSON.stringify(this.url)
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
          tmp = "<li><a href='#' onClick=\"$CDX.add_data_array('#{this.url}')\">#{itemName}</a></li>"
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
