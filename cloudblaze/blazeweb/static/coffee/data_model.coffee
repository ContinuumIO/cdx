

class PublishModel extends Continuum.HasProperties
  collections : Continuum.Collections
  type : 'PublishModel'
  default_view : $CDX.Views.PublishView
  defaults :
    plot_tab_info : []
    plots : []
    arrays : []
    array_tab_info : []

class PublishModels extends Backbone.Collection
  model : PublishModel

Continuum.register_collection('PublishModel', new PublishModels())


class CDXPlotContext extends Continuum.Component
  type : 'CDXPlotContext',
  default_view : $CDX.Views.CDXPlotContextView
  url : () ->

    return super()
  defaults :
    children : []
    render_loop : true

class CDXPlotContexts extends Backbone.Collection
  model : CDXPlotContext

Continuum.register_collection('CDXPlotContext', new CDXPlotContexts())

