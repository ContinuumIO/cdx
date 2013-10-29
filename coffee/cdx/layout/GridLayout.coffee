ContinuumView = require("../common/continuum_view").ContinuumView
events = require("./events")
gridtemplate = require("./gridtemplate")

class GridView extends ContinuumView

  grid_selector: ".gridster"
  template: gridtemplate

  initialize: (options) ->
    super(options)
    @elements = options.elements
    @render()

  render: () ->
    @$el.html('')
    @$el.html(@template({elements : @elements}))
    gridster = $(@grid_selector).gridster(
        widget_base_dimensions: [140, 140]
        widget_margins: [5, 5]
        widget_selector: 'div.griditem'
        helper: 'clone'
        resize:
          enabled: true
    ).data('gridster')

    gridster.add_widget(e.content, e.x, e.y, e.r, e.c) for e in @elements


exports.GridView = GridView
