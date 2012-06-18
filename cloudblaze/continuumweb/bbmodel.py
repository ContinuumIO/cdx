import requests
import urlparse
import utils
import uuid
import logging
import cPickle as pickle
import redis
import numpy as np
log = logging.getLogger(__name__)

class ContinuumModel(object):
    collections = ['Continuum', 'Collections']    
    def __init__(self, typename, **kwargs):
        self.attributes = kwargs
        self.typename = typename
        self.attributes.setdefault('id', str(uuid.uuid4()))
        self.id = self.get('id')
        
    def ref(self):
        return {
            'collections' : self.collections,
            'type' : self.typename,
            'id' : self.attributes['id']
            }
    def get(self, key, default=None):
        return self.attributes.get(key, default)
    
    def get_ref(self, field, client):
        ref = self.get(field)
        return client.get(ref['type'], ref['id'])
    
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

    def __str__(self):
        return "Model:%s" % self.typename
    
    def __repr__(self):
        return self.__str__()
"""
In our python interface to the backbone system, we separate the local collection
which stores models, from the http client which interacts with a remote store
In applications, we would use a class that combines both
"""
import simplejson
def serialize(obj):
    return simplejson.dumps(obj)
        
def deserialize(strdata):
    if strdata is None:
        return None
    else:
        return simplejson.loads(strdata)
    
def bbget(client, key):
    typename, modelid = parse_modelkey(key)
    attrs = deserialize(client.get(key))
    if attrs is None:
        return None
    else:
        return ContinuumModel(typename, **attrs)

def bbset(client, key, model):
    return client.set(key, serialize(model.attributes))

def dockey(docid):
    return 'doc:' + docid

def modelkey(typename, modelid):
    return 'model:%s:%s' % (typename, modelid)

def parse_modelkey(modelkey):
    _, typename, modelid = modelkey.split(":")
    return (typename, modelid)

class ContinuumModelsStorage(object):
    def __init__(self, client):
        self.client = client
        
    
    def get_bulk(self, docid, typename=None):
        doc_keys = self.client.smembers(dockey(docid))
        result = []
        for k in doc_keys:
            m = bbget(self.client, k)
            if docid in m.get('docs') and \
               (typename is None or m.typename == typename):
                result.append(m)
        return result
    
    def get(self, typename, id):
        return bbget(self.client, modelkey(typename, id))
    
    def add(self, model):
        with self.client.pipeline() as pipe:
            self._upsert(pipe, model)
            pipe.execute()
            
    def _upsert(self, pipe, model):
        mkey = modelkey(model.typename, model.id)
        pipe.watch(mkey)
        for doc in model.get('docs'):
            pipe.watch(dockey(doc))
        oldmodel = bbget(self.client, mkey)
        if oldmodel is None:
            olddocs = []
        else:
            olddocs = oldmodel.get('docs')
        for doc in olddocs:
            pipe.watch(dockey(doc))
        pipe.multi()
        docs_to_remove = set(olddocs).difference(model.get('docs'))        
        for doc in docs_to_remove:
            pipe.srem(dockey(doc), mkey)
        docs_to_add = set(model.get('docs')).difference(olddocs)
        for doc in docs_to_add:
            pipe.sadd(dockey(doc), mkey)
        bbset(pipe, mkey, model)

    def attrupdate(self, typename, attributes):
        id = attributes['id']
        mkey = modelkey(typename, id)        
        with self.client.pipeline() as pipe:
            pipe.watch(mkey)
            model = self.get(typename, id)
            for k,v in attributes.iteritems():
                model.set(k, v)
            self._upsert(pipe, model)
            pipe.execute()
        return model
    
    def delete(self, typename, id):
        mkey = modelkey(typename, id)
        oldmodel = bbget(self.client, mkey)
        olddocs = oldmodel.get('docs')
        for doc in olddocs:
            self.client.srem(dockey(doc), mkey)
        self.client.delete(mkey)
    
        
class ContinuumModelsClient(object):
    def __init__(self, docid, baseurl, ph):
        self.ph = ph
        self.baseurl = baseurl
        self.docid = docid
        self.s = requests.session(headers={'content-type':'application/json'})
        super(ContinuumModelsClient, self).__init__()
        self.buffer = []
        
    def delete(self, typename, id):
        url = utils.urljoin(self.baseurl, self.docid +"/", typename + "/", id)
        self.s.delete(url)
        
    def buffer_sync(self):
        data = self.ph.serialize_web([x.to_broadcast_json() for x in self.buffer])
        url = utils.urljoin(self.baseurl, self.docid + "/", 'bulkupsert')
        self.s.post(url, data=data)
        self.buffer = []
        
    def create(self, typename, attributes, defer=False):
        if 'docs' not in attributes:
            attributes['docs'] = [self.docid]
        model =  ContinuumModel(typename, **attributes)
        if defer:
            self.buffer.append(model)
        else:
            url = utils.urljoin(self.baseurl, self.docid +"/", typename)
            log.debug("create %s", url)
            self.s.post(url, data=self.ph.serialize_msg(model.to_json()))
        return model

    def update(self, typename, attributes, defer=False):
        if 'docs' not in attributes:
            attributes['docs'] = [self.docid]
        id = attributes['id']
        model =  ContinuumModel(typename, **attributes)
        if defer:
            self.buffer.append(model)
        else:
            url = utils.urljoin(self.baseurl, self.docid +"/", typename + "/", id)
            log.debug("create %s", url)
            self.s.put(url, data=self.ph.serialize_web(model.to_json()))
        return model
    
    def get(self, typename=None, id=None):
        return self.fetch(typename=typename, id=id)
    
    def fetch(self, typename=None, id=None):
        if typename is None:
            url = utils.urljoin(self.baseurl, self.docid)
            data = self.s.get(url).content
            specs = self.ph.deserialize_web(data)
            models =  [ContinuumModel(
                x['type'], **x['attributes']) for x in specs]
            return models
        elif typename is not None and id is None:
            url = utils.urljoin(self.baseurl, self.docid +"/", typename)
            attrs = self.ph.deserialize_web(self.s.get(url).content)
            models = [ContinuumModel(typename, **x) for x in attrs]
            return models
        elif typename is not None and id is not None:
            url = utils.urljoin(self.baseurl, self.docid +"/", typename + "/", id)
            attr = self.ph.deserialize_web(self.s.get(url).content)
            if attr is None:
                return None
            model = ContinuumModel(typename, **attr)
            return model
        
    def upsert_all(self, models):
        for m in models:
            self.update(m.typename, m.attributes, defer=True)
        self.client.buffer_sync()
        
