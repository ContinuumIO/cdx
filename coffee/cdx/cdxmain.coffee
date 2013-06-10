CDXApp = require("./cdxapp").CDXApp
class CDXRouter extends Backbone.Router
  routes :
    "cdx/:title" : 'main'
  main : (title) ->
    view = new CDXApp(title : title)
    $('body').append(view.el)
    window.view = view
    window.setup_ipython("ws://localhost:10010")
$(()->
  router = new CDXRouter()
  Backbone.history.start()
)