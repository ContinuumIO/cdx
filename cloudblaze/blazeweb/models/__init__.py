import simplejson

class UnauthorizedException(Exception):
    pass

class ServerModel(object):
    idfield = None
    typename = None
    
    @classmethod
    def modelkey(cls, objid):
        return "model:%s:%s"% (cls.typename, objid)

    def mykey(self):
        return self.modelkey(getattr(self, self.idfield))

    def to_json(self):
        raise NotImplementedError
    
    @staticmethod
    def from_json(obj):
        raise NotImplementedError        
        #return User(obj['email'], obj['passhash'], obj['docs'])
    
    def save(self, client):
        client.set(self.mykey(), simplejson.dumps(self.to_json()))
        
    @classmethod
    def load(cls, client, objid):
        data = client.get(cls.modelkey(objid))
        if data is None:
            return None
        attrs = simplejson.loads(data)
        return cls.from_json(attrs)
