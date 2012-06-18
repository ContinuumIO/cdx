import simplejson
from werkzeug import generate_password_hash, check_password_hash

class UnauthorizedException(Exception):
    pass

def new_user(client, email, password, docs=None):
    key = User.modelkey(email)
    with client.pipeline() as pipe:
        pipe.watch(key)
        pipe.multi()
        if client.exists(key):
            raise UnauthorizedException
        passhash = generate_password_hash(password, method='sha256')
        user = User(email, passhash, docs=docs)
        user.save(pipe)
        pipe.execute()
        return user

def auth_user(client, email, password):
    user = User.load(client, email)
    if user is None:
        raise UnauthorizedException        
    if check_password_hash(user.passhash, password):
        return user
    else:
        raise UnauthorizedException
    
class User(object):
    #we're using email as the id for now...
    def __init__(self, email, passhash, docs=None):
        self.email = email
        self.passhash = passhash
        if docs is None:
            docs = []
        self.docs = docs
        
    @staticmethod
    def modelkey(email):
        return "model:user:%s " % email
    
    def mykey(self):
        return self.modelkey(self.email)

    def to_json(self):
        return {'email' : self.email,
                'passhash' : self.passhash,
                'docs' : self.docs}
    
    def save(self, client):
        client.set(self.mykey(), simplejson.dumps(self.to_json()))
    
    @staticmethod
    def from_json(obj):
        return User(obj['email'], obj['passhash'], obj['docs'])
        
    @staticmethod
    def load(client, email):
        data = client.get(User.modelkey(email))
        if data is None:
            return None
        attrs = simplejson.loads(data)
        return User.from_json(attrs)
    
        
        
