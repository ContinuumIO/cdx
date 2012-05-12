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
        
class ContinuumModels(object):
    def __init__(self):
        self.collections = {}

    def get(self, typename, id):
        return self.collections.get((typename, id))

    def add(self, typename, model):
        self.collections[typename, model.attributes['id']] = model
        
class ContinuumModelsClient(ContinuumModels):
    def __init__(self, docid, baseurl, ph):
        self.ph = ph
        self.baseurl = baseurl
        self.docid = docid
        self.s = requests.session()
        super(ContinuumModelsClient, self).__init__()
        
    def create(self, typename, **kwargs):
        model =  ContinuumModel(typename, **kwargs)
        self.add(typename, model)
        url = utils.urljoin(self.baseurl, self.docid +"/", typename)
        log.debug("create %s", url)
        self.s.post(url, data=self.ph.serialize_msg(model.to_json()))
        return model
    
