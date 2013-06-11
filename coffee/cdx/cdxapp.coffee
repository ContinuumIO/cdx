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

class CDXModel extends base.HasProperties
  defaults :
    namespace : null
    activetable : null
    activeplot : null
    plotcontext : null

class CDXApp extends Backbone.View
  attributes :
    class : 'cdxmain'

  initialize : (options) ->
    title = options.title
    @render_layouts()
    @init_bokeh(title)

  init_bokeh : (title) ->
    wswrapper = utility.make_websocket()
    doc = new usercontext.Doc(title : title)
    view = new DocView(model : doc)
    load = doc.load(true)
    load.done((data) =>
      ns = base.Collections('Namespace').first()
      if not ns
        ns = base.Collections('Namespace').create(doc : doc.id)
        pc = doc.get_obj('plot_context')
        children = _.clone(pc.get('children'))
        children.push(ns.ref())
        pc.set('children', children)
        pc.save()
      @ns = ns
      @$namespace.append(@ns.$el)
    )
    @docview = view
    @$plotholder.append(@docview.$el)
    @wswrapper = wswrapper

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
    @plotbox.sizes = [10, 40, 50]
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