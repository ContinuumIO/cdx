ContinuumView = require("../common/continuum_view").ContinuumView
events = require("./events")
gridtemplate = require("./gridtemplate")

class GridLayout extends ContinuumView

  grid_selector: ".gridster ul"
  template: gridtemplate

  initialize: (options) ->
    super(options)
    @render()

  render: () ->

    top_height = 11
    max_size_y = 12
    max_size_x = 12

    namespace =
      title: "namespaceholder"
      x: 1
      y: top_height
      r: 1
      c: 1

    title =
      title: "tableholder"
      x: (max_size_x / 2) - 1
      y: top_height
      r: 1
      c: 2

    plotholder =
      title: "plotholder"
      x: (max_size_x / 2) - 1
      y: top_height
      r: 1
      c: 3

    plotlist =
      title: "plotlistholder"
      x: 1
      y: top_height
      r: 1
      c: 4

    ipcell =
      title: "thecell"
      x: max_size_x / 2
      y: max_size_y - top_height
      r: top_height + 1
      c: 1

    ipoutput =
      title: "ipoutput"
      x: max_size_x / 2
      y: max_size_y - top_height
      r: top_height + 1
      c: max_size_x / 2

    @elements = [namespace, title, plotholder, plotlist, ipcell, ipoutput]

    html = @template({elements : @elements})
    $(@grid_selector).append(html)

    $(@grid_selector).gridster
      widget_base_dimensions: [80, 80]
      widget_margins: [10, 10]
      widget_selector: ".griditem"
      max_size_x: max_size_x
      max_size_y: max_size_y
      helper: 'clone'
      resize:
        enabled: true




exports.GridLayout = GridLayout
