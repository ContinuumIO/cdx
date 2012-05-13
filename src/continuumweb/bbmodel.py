import websocket
import requests
import urlparse
import utils
import uuid
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
        
    def to_broadcast_json(self):
        #more verbose json, which includes collection/type info necessary
        #for recon on the JS side.
        json = self.ref()
        json['attributes'] = self.attributes
        return json
    
    def to_json(self):
        return self.attributes
"""
In our python interface to the backbone system, we separate the local collection
which stores models, from the http client which interacts with a remote store
In applications, we would use a class that combines both
"""
class ContinuumModelsStorage(object):
    def __init__(self):
        self.collections = {}

    def get(self, typename, id):
        return self.collections.get((typename, id))

    def add(self, typename, model):
        self.collections[typename, model.attributes['id']] = model

    def update(self, typename, attributes):
        id = attributes['id']
        model = self.get(typename, id)
        for k,v in attributes.iteritems():
            model.set(k, v)
        return model
    
class ContinuumModelsClient(object):
    def __init__(self, docid, baseurl, ph):
        self.ph = ph
        self.baseurl = baseurl
        self.docid = docid
        self.s = requests.session()
        super(ContinuumModelsClient, self).__init__()
        
    def create(self, typename, attributes):
        model =  ContinuumModel(typename, **attributes)
        url = utils.urljoin(self.baseurl, self.docid +"/", typename)
        log.debug("create %s", url)
        self.s.post(url, data=self.ph.serialize_msg(model.to_json()))
        return model

    def update(self, typename, attributes):
        id = attributes['id']
        model =  ContinuumModel(typename, **attributes)
        url = utils.urljoin(self.baseurl, self.docid +"/", typename + "/", id)
        log.debug("create %s", url)
        self.s.put(url, data=self.ph.serialize_msg(model.to_json()))
        return model

class ContinuumModels(object):
    def __init__(self, storage, client):
        self.storage = storage
        self.client = client
        
    def create(self, typename, attributes):
        model = self.client.create(typename, attributes)        
        self.storage.add(typename, model)        

    def update(self, typename, attributes):
        id = attributes['id']
        model = self.client.update(typename, attributes)
        self.storage.update(typename, model.attributes)
        return model
    
    def get(self, typename, id):
        return self.storage.get(typename, id)
        
        
