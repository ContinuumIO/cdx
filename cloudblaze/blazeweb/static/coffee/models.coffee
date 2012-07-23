class NamespaceViewer extends Backbone.View
  render: () ->
    console.log('namespaceviewer render')
    variable_item_template = $('#variable-item-template').html()

    $.when($CDX.IPython.namespace.get('variables')).then( (array) =>
      window.namespace = array
      funcs = _.filter(array, (obj) -> obj.type == 'function')
      reg_variables = _.reject(array, (obj) -> obj.type in ['function', 'module'])
      grouped = _.groupBy(reg_variables, (obj) -> obj.type)
      $(this.el).html(
        _.template2(variable_item_template,
          reg_variables:grouped, funcs:funcs))
      )



class PublishModel extends Continuum.HasProperties
  collections : Continuum.Collections
  type : 'PublishModel'
  default_view : PublishView
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
  default_view : CDXPlotContextView
  url : () ->

    return super()
  defaults :
    children : []
    render_loop : true

class CDXPlotContexts extends Backbone.Collection
  model : CDXPlotContext

Continuum.register_collection('CDXPlotContext', new CDXPlotContexts())

