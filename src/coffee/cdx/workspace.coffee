define [
  "underscore"
  "jquery"
  "backbone"
  "common/continuum_view"
  "common/has_properties"
], (_, $, Backbone, ContinuumView, HasProperties) ->

  class WorkspaceView extends ContinuumView.View
    initialize: (options) ->
      super(options)

  class Workspace extends HasProperties
    default_view: WorkspaceView
    type: "Workspace"
    defaults:
      varname: null
      data_table: null
      pivot_tables: []
      plots: []
      plot_context: null
      active_tab: 0

  class Workspaces extends Backbone.Collection
    model: Workspace

  return {
    Model: Workspace
    Collection: new Workspaces()
    View: WorkspaceView
  }
