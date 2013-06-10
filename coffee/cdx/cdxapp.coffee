layout = require("./layout/index")
bokehutils = require("./serverutils")
utils = require("./serverutils")
base = require("./base")
Config = base.Config
utility = utils.utility
Config.ws_conn_string = "ws://#{window.location.host}/bokeh/sub"
usercontext = require("usercontext/usercontext")
DocView = require("./doc").DocView
class CDXApp extends Backbone.View
  attributes :
    class : 'cdxmain'
  initialize : (options) ->
    title = options.title
    @init_bokeh(title)
    @render()

  init_bokeh : (title) ->
    wswrapper = utility.make_websocket()
    doc = new usercontext.Doc(title : title)
    view = new DocView(model : doc)
    load = doc.load(true)
    @docview = view
    @wswrapper = wswrapper

  render : () ->
    second = $('<div id="thecell"></div>')
    second.css('height', '100%')
    second.css('width', '100%')
    view = new layout.VBoxView(
      elements : [@docview.el, second]
      height : '100%'
      width : '100%'
    )
    view.sizes = [80,20]
    view.set_sizes()
    @layout = view
    @$el.append(view.el)
    window.setup_ipython("ws://localhost:10010")

utility = utils.utility
Promises = utils.Promises
Config.ws_conn_string = "ws://#{window.location.host}/bokeh/sub"

usercontext = require("usercontext/usercontext")

exports.CDXApp = CDXApp