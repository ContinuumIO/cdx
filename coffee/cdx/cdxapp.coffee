layout = require("./layout/index")
bokehutils = require("./serverutils")
utils = require("./serverutils")
base = require("./base")
Config = base.Config
utility = utils.utility
Config.ws_conn_string = "ws://#{window.location.host}/bokeh/sub"
usercontext = require("usercontext/usercontext")

class CDXApp extends Backbone.View
  attributes :
    class : 'cdxmain'
  initialize : () ->
    @init_bokeh()
    @render()

  init_bokeh : () ->
    wswrapper = utility.make_websocket()
    userdocs = new usercontext.UserDocs()
    userdocs.subscribe(wswrapper, 'defaultuser')
    window.userdocs = userdocs
    load = userdocs.fetch(update : true)
    userdocsview = new usercontext.UserDocsView(collection : userdocs)
    @userdocsview = userdocsview
    @userdocs = userdocs
    @wswrapper = wswrapper

  render : () ->
    second = $('<div id="thecell"></div>')
    second.css('height', '100%')
    second.css('width', '100%')
    view = new layout.VBoxView(
      elements : [@userdocsview.el, second]
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