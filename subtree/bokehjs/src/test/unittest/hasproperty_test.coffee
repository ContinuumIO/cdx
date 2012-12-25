class TestObject extends Continuum.HasProperties
  type : 'TestObject'
class TestObjects extends Backbone.Collection
  model : TestObject
  url : "/"

test('computed_properties', ->
  Continuum.Collections.TestObject = new TestObjects()
  model = Continuum.Collections['TestObject'].create({'a' : 1, 'b': 1})
  model.register_property('c', () -> @get('a') + @get('b'))
  model.add_dependencies('c', model, ['a', 'b'])
  temp =  model.get('c')
  ok(temp == 2)
)

test('cached_properties_react_changes', ->
  Continuum.Collections.TestObject = new TestObjects()
  model = Continuum.Collections['TestObject'].create({'a' : 1, 'b': 1})
  model.register_property('c',
    () -> @get('a') + @get('b'),
    true)
  model.add_dependencies('c', model, ['a', 'b'])
  temp =  model.get('c')
  ok(temp == 2)
  temp = model.get_cache('c')
  ok(not _.isUndefined(temp))
  model.set('a', 10)
  temp = model.get_cache('c')
  temp = model.get('c')
  ok(temp == 11)
)


test('has_prop_manages_event_lifcycle', ->
  Continuum.Collections.TestObject = new TestObjects()
  model = Continuum.Collections['TestObject'].create({'a' : 1, 'b': 1})
  model2 = Continuum.Collections['TestObject'].create({'a' : 1, 'b': 1})
  triggered = false
  Continuum.safebind(model, model2, 'change', () -> triggered = true)
  model2.set({'a' : 2})
  ok(triggered)
  triggered = false
  model.destroy()
  model2.set({'a' : 3})
  ok(not triggered)
)

test('has_prop_manages_event_for_views', ->
  Continuum.Collections.TestObject = new TestObjects()
  model = Continuum.Collections['TestObject'].create({'a' : 1, 'b': 1})
  # dummy model2 to be the default model for continuumview
  # we mostly want to test how we react to other models, which is why
  # @model for a view is already handleed
  model2 = Continuum.Collections['TestObject'].create({'a' : 1, 'b': 1})
  view = new Continuum.ContinuumView({'model' : model2})

  triggered = false
  Continuum.safebind(view, model, 'change', () -> triggered = true)
  model.set({'a' : 2})
  ok(triggered)
  triggered = false
  view.remove()
  model.set({'a' : 3})
  ok(not triggered)
)

test('property_setters', ->
  Continuum.Collections.TestObject = new TestObjects()
  model = Continuum.Collections['TestObject'].create({'a' : 1, 'b': 1})
  # dummy model2 to be the default model for continuumview
  # we mostly want to test how we react to other models, which is why
  # @model for a view is already handleed
  prop =  () -> @get('a') + @get('b')
  setter = (val) ->
    @set('a', val/2, {silent:true})
    @set('b', val/2)
  model.register_property('c', prop, true)
  model.add_dependencies('c', model, ['a', 'b'])
  model.register_setter('c', setter)
  model.set('c', 100)
  ok(model.get('a') == 50)
  ok(model.get('b') == 50)
)

test('test_vectorized_ref', () ->
  Continuum.Collections.TestObject = new TestObjects()
  model1 = Continuum.Collections['TestObject'].create(
    a : 1
    b : 1
  )
  model2 = Continuum.Collections['TestObject'].create(
    a : 2
    b : 2
  )
  model3 = Continuum.Collections['TestObject'].create(
    a : 1
    b : 1
    vectordata : [model1.ref(), model2.ref()]
  )
  output = model3.get_obj('vectordata')
  ok(output[0] == model1)
  ok(output[1] == model2)
  model3.set_obj('vectordata2', [model1, model1, model2])
  output = model3.get('vectordata2')
  ok(output[0].id == model1.ref().id)
  ok(output[1].id == model1.ref().id)
  ok(output[2].id == model2.ref().id)
  ok (not (output[0] instanceof Continuum.HasProperties))
  return null
)