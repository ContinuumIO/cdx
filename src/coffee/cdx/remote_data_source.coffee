define [
  "backbone",
  "common/has_properties",
], (Backbone, HasProperties) ->
  class RemoteDataSource extends HasProperties
    type: 'RemoteDataSource'
    defaults:
      computed_columns: []

  class RemoteDataSources extends Backbone.Collection
    model: RemoteDataSource

  return {
    "Model": RemoteDataSource,
    "Collection": new RemoteDataSources()
  }
