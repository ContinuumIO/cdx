
CDXApp = require("./cdxapp").CDXApp
$(() ->
  view = new CDXApp()
  $('body').append(view.el)
  window.view = view
  window.setup_ipython("ws://localhost:10010")

)