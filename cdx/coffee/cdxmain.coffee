
CDXApp = require("./cdxapp").CDXApp
$(() ->
  view = new CDXApp()
  $('body').append(view.el)
)