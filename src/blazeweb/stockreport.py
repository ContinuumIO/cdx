from app import app
from flask import request, current_app
import flask

import uuid
import simplejson
import logging
import urlparse
import blazeclient
import stockreport
import logging
log = logging.getLogger(__name__)

class ContinuumModel(object):
    collections = ['Continuum', 'Collections']    
    def __init__(self, typename, **kwargs):
        self.attributes = kwargs
        self.typename = typename
        self.attributes.setdefault('id', str(uuid.uuid4()))
        
    def ref(self):
        return {
            'collections' : self.collections,
            'type' : self.typename,
            'id' : self.attributes['id']
            }
    def get(self, key):
        return self.attributes[key]
    
    def set(self, key, val):
        self.attributes[key] = val
        
    def to_json(self):
        json = self.ref()
        json['attributes'] = self.attributes
        return json
    
class ContinuumModels(object):
    def __init__(self):
        self.collections = {}
        
    def create(self, typename, **kwargs):
        model =  ContinuumModel(typename, **kwargs)
        coll = self.collections.setdefault(typename, {})
        coll[model.attributes['id']] = model
        return model
    
    def get(self, typename, id):
        return self.collections[typename][model.attributes['id']]

@app.route("/stockdates/", methods = ['get'])
def stock_page():
    response, dataobj = blazeclient.raw_get(
        current_app.rpcclient, "/hugodata")
    dates = [[x, "/stockreport/%s" % x] for x in response['children']]
    return flask.render_template('stockdates.html', dates=dates)
                 
@app.route("/stockreport/<date>")
def stock_report(date):
    response, dataobj = blazeclient.raw_get(
        current_app.rpcclient, "/hugodata/%s/names" % date)
    names = dataobj[0]
    response, dataobj = blazeclient.raw_get(
        current_app.rpcclient, "/hugodata/%s/prices" % date)
    shape = response['shape']
    prices = dataobj[0]
    response, dataobj = blazeclient.raw_get(
        current_app.rpcclient, "/hugodata/%s/dates" % date)
    dates = dataobj[0]
    ds = []
    for row in prices:
        point = {}
        for name, price in zip(names, row):
            point[name] = price
        ds.append(point)
    models = ContinuumModels()
    data_source = models.create('ObjectArrayDataSource', data=ds)
    container = models.create('GridPlotContainer', children=[])
    all_components = []
    all_components.append(data_source)
    all_components.append(container)
    log.debug("%s", names)
    for idx, n1 in enumerate(names):
        for n2 in names[idx+1:]:
            log.debug("%s, %s", n1, n2)
            components = stock_compare_plot(
                models, data_source, container, n1, n2)
            all_components.extend(components)
            container.attributes['children'].append([components[0].ref()])
    main = container.ref()
    all_components = [x.to_json() for x in all_components]

    return flask.render_template(
        'stockreport.html',
        main=simplejson.dumps(main),
        all_components=simplejson.dumps(all_components))

            
def stock_compare_plot(models, data_source, container, name1, name2):
    xr = models.create('Range1d', start=0, end=200)
    yr = models.create('Range1d', start=0, end=200)
    plot = models.create('Plot', data_sources={'prices' : data_source.ref()},
                         xrange=xr.ref(), yrange=yr.ref(), parent=container.ref())
    datarange1 = models.create('DataRange1d', data_source=data_source.ref(),
                               columns=[name1])
    datarange2 = models.create('DataRange1d', data_source=data_source.ref(),
                               columns=[name2])
    xmapper = models.create('LinearMapper', data_range=datarange1.ref(),
                            screen_range=plot.attributes['xrange'])
    ymapper = models.create('LinearMapper', data_range=datarange2.ref(),
                            screen_range=plot.attributes['yrange'])
    scatter = models.create('ScatterRenderer', data_source=data_source.ref(),
                            xfield=name1, yfield=name2, xmapper=xmapper.ref(),
                            ymapper=ymapper.ref(), parent=plot.ref())
    plot.set('renderers', [scatter.ref()])
    return (plot, datarange1, datarange2, xr, yr, xmapper, ymapper, scatter)


