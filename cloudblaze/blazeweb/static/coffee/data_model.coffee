$CDX.Models = {}
$CDX.Collections = {}

class $CDX.Models.PublishModel extends Continuum.HasProperties
  collections : Continuum.Collections
  type : 'PublishModel'
  default_view : $CDX.Views.PublishView
  defaults :
    plot_tab_info : []
    plots : []
    arrays : []
    array_tab_info : []

class $CDX.Collections.PublishModels extends Backbone.Collection
  model : $CDX.Models.PublishModel

Continuum.register_collection('PublishModel', new $CDX.Collections.PublishModels())


class $CDX.Models.CDXPlotContext extends Continuum.Component
  type : 'CDXPlotContext',
  default_view : $CDX.Views.CDXPlotContextView
  url : () ->

    return super()
  defaults :
    children : []
    render_loop : true

class $CDX.Collections.CDXPlotContexts extends Backbone.Collection
  model : $CDX.Models.CDXPlotContext

Continuum.register_collection('CDXPlotContext', new $CDX.Collections.CDXPlotContexts())

