layout = require("./layout/index")

class CDXApp extends Backbone.View
  initialize : () ->
    @render()

  render : () ->
    first = $('<div>div1</div>')
    second = $('<div>div2</div>')
    third = $('<div>div3</div>')
    for temp in _.zip([first, second, third], ['red', 'yellow', 'green'])
      [node, color] = temp
      node.css('background-color', color)
      node.css('height', '100%')
      node.css('width', '100%')
    view = new layout.VBoxView(
      elements : [first, second, third]
      height : 300
      width : 100
    )
exports.CDXApp = CDXApp