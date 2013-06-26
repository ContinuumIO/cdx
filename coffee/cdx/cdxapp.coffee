plot_context = require("./common/plot_context")
layout = require("./layout/index")
bokehutils = require("./serverutils")
utils = require("./serverutils")
base = require("./base")
Config = base.Config
utility = utils.utility
Config.ws_conn_string = "ws://#{window.location.host}/bokeh/sub"
usercontext = require("usercontext/usercontext")
DocView = require("./doc").DocView
namespace = require("./namespace/namespace")

class CDX extends base.HasProperties
  default_view : Backbone.View
  type : 'CDX'
  defaults :
    namespace : null
    activetable : null
    activeplot : null
    plotcontext : null

class CDXs extends Backbone.Collection
  model : CDX

exports.cdxs = new CDXs()

class CDXApp extends Backbone.View
  attributes :
    class : 'cdxmain'

  delegateEvents : (events) ->
    super(events)
  initialize : (options) ->
    title = options.title
    @render_layouts()
    @init_bokeh(title)

  init_bokeh : (title) ->
    wswrapper = utility.make_websocket()
    doc = new usercontext.Doc(title : title)
    load = doc.load(true)
    load.done((data) =>
      cdx = base.Collections('CDX').first()
      if not cdx
        coll = base.Collections('CDX')
        cdx = new coll.model(doc : doc.id)
        coll.add(cdx)
        pc = doc.get_obj('plot_context')
        children = _.clone(pc.get('children'))
        children.push(cdx.ref())
        pc.set('children', children)
        cdx.set_obj('plotcontext', pc)
      ns = cdx.get_obj('namespace')
      if not ns
        coll = base.Collections('Namespace')
        ns = new coll.model(doc : doc.id)
        coll.add(ns)
        cdx.set_obj('namespace', ns)
      plotlist = cdx.get_obj('plotlist')
      if not plotlist
        coll = base.Collections('PlotList')
        plotlist = new coll.model(doc : doc.id)
        coll.add(plotlist)
        cdx.set_obj('plotlist', plotlist)
      base.Collections.bulksave([cdx, doc.get_obj('plot_context'),
        ns, plotlist])
      @cdxmodel = cdx
      @listenTo(@cdxmodel, 'change:activetable', @render_activetable)
      @listenTo(@cdxmodel, 'change:namespace', @render_namespace)
      @listenTo(@cdxmodel, 'change:plotlist', @render_plotlist)
      @listenTo(@cdxmodel, 'change:activeplot', @render_activeplot)
      @render_namespace()
      @render_plotlist()
      @render_activetable()
      @render_activeplot()
    )

    @wswrapper = wswrapper

  render_namespace : () ->
    @nsview = new namespace.NamespaceView(
      model : @cdxmodel.get_obj('namespace')
    )
    @$namespace.html('')
    @$namespace.append(@nsview.$el)
    @listenTo(@nsview, 'view', @make_table)

  conninfo :
    host : 'localhost'
    port : 10020

  make_table : (varname) ->
    coll = base.Collections("IPythonRemoteData")
    remotedata = new coll.model (
      host : @conninfo.host
      port : @conninfo.port
      varname : varname
    )
    coll.add(remotedata)
    coll = base.Collections("PandasPivotTable")
    pivot = new coll.model()
    pivot.set_obj('source', remotedata)
    coll.add(pivot)
    @cdxmodel.set({'activetable' : pivot.ref()}, {'silent' : true})
    result = base.Collections.bulksave([@cdxmodel, pivot, remotedata])
    result.done(() =>
      @cdxmodel.trigger('change:activetable')
    )

  render_plotlist : () ->
    plotlist = @cdxmodel.get_obj('plotlist')
    @plotlistview = new plot_context.PNGContextView(
      model : plotlist
      thumb_x : 150
      thumb_y : 150
    )
    @$plotlist.html('').append(@plotlistview.$el)
    @listenTo(@plotlistview, 'showplot', @showplot)

  showplot : (ref) ->
    model = @cdxmodel.resolve_ref(ref)
    @cdxmodel.set_obj('activeplot', model)

  render_activeplot : () ->
    activeplot = @cdxmodel.get_obj('activeplot')
    if activeplot
      view = new activeplot.default_view(model : activeplot)
      @$plotholder.html('').append(view.$el)
    else
      @$plotholder.html('')

  render_activetable : () ->
    activetable = @cdxmodel.get_obj('activetable')
    if activetable
      @activetableview = new activetable.default_view(model : activetable)
      @$table.html('').append(@activetableview.$el)
    else
      @$table.html('')

  split_ipython : () ->
    temp = $('#thecell').find('.output_wrapper')
    temp.detach()
    @$ipoutput.append(temp)

  render_layouts : () ->
    @$namespace = $('<div class="namespaceholder hundredpct"></div>')
    @$table = $('<div class="tableholder hundredpct"></div>')
    @$plotholder = $('<div class="plotholder hundredpct"></div>')
    @$plotlist = $('<div class="plotlistholder hundredpct"></div>')
    @plotbox = new layout.HBoxView(
      elements : [@$namespace, @$table, @$plotholder, @$plotlist]
      height : '100%',
      width : '100%',
    )
    @plotbox.sizes = [10, 40, 40, 10]
    @plotbox.set_sizes()
    @$ipcell = $('<div id="thecell" class="hundredpct"></div>')
    @$ipoutput = $("<div class='ipoutput'></div>")
    @iplayout = new layout.HBoxView(
      elements : [@$ipcell, @$ipoutput]
      height : '100%'
      width : '100%'
    )
    @layout = new layout.VBoxView(
      elements : [@plotbox.$el, @iplayout.$el]
      height : '100%'
      width : '100%'
    )
    @layout.sizes = [80,20]
    @layout.set_sizes()
    @$el.append(@layout.el)
    window.setup_ipython("ws://localhost:10010")

utility = utils.utility
Promises = utils.Promises
Config.ws_conn_string = "ws://#{window.location.host}/bokeh/sub"

usercontext = require("usercontext/usercontext")

exports.CDXApp = CDXApp