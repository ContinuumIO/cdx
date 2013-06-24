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
        cdx = base.Collections('CDX').create(doc : doc.id)
        pc = doc.get_obj('plot_context')
        children = _.clone(pc.get('children'))
        children.push(cdx.ref())
        pc.set('children', children)
        pc.save()
        cdx.set_obj('plotcontext', pc)
        cdx.save()
      ns = cdx.get_obj('namespace')
      if not ns
        ns = base.Collections('Namespace').create(doc : doc.id)
        cdx.set_obj('namespace', ns)
        cdx.save()
      plotlist = cdx.get_obj('plotlist')
      if not plotlist
        plotlist = base.Collections('PlotList').create(doc : doc.id)
        cdx.set_obj('plotlist', plotlist)
        cdx.save()
      @cdxmodel = cdx
      @render_namespace()
      @render_plotlist()
      @render_activetable()
    )

    @wswrapper = wswrapper
  render_namespace : () ->
    @nsview = new namespace.NamespaceView(
      model : @cdxmodel.get_obj('namespace')
    )
    @$namespace.append(@nsview.$el)
  render_plotlist : () ->
    plotlist = @cdxmodel.get_obj('plotlist')
    @plotlistview = new plotlist.default_view(model : plotlist)
    @$plotholder.append(@plotlistview.$el)

  render_activetable : () ->
    activetable = @cdxmodel.get_obj('activetable')
    if activetable
      @activetableview = new activetable.default_view(model : activetable)
      @$table.append(@activetableview.$el)

  render_layouts : () ->
    @$namespace = $('<div class="namespaceholder hundredpct"></div>')
    @$table = $('<div class="tableholder hundredpct"></div>')
    @$plotholder = $('<div class="plotholder hundredpct"></div>')
    ##@$plotlist = $('<div class="plotlistholder hundredpct"></div>')
    @plotbox = new layout.HBoxView(
      elements : [@$namespace, @$table, @$plotholder]
      height : '100%',
      width : '100%',
    )
    @plotbox.sizes = [20, 40, 40]
    @plotbox.set_sizes()
    ipcell = $('<div id="thecell" class="hundredpct"></div>')
    @layout = new layout.VBoxView(
      elements : [@plotbox.$el, ipcell]
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