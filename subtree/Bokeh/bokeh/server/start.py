from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from flask import request
import gevent
import gevent.monkey
gevent.monkey.patch_all()
import uuid
import socket
import redis

#server imports
from app import app
import wsmanager
from .. import protocol
from serverbb import ContinuumModelsStorage
from .. import bbmodel
bbmodel.load_special_types()

import models.user as user
import models.convenience as mconv
import models.docs as docs

import logging
import time


PORT = 5006
REDIS_PORT = 6379

log = logging.getLogger(__name__)

def prepare_app(rhost='127.0.0.1', rport=REDIS_PORT):
    #must import views before running apps
    import views.deps
    app.wsmanager = wsmanager.WebSocketManager()
    def auth(auth, docid):
        doc = docs.Doc.load(app.model_redis, docid)
        status = mconv.can_write_doc_api(doc, auth, app)
        return status
    app.wsmanager.register_auth("bokehplot", auth)
    app.bb_redis = redis.Redis(host=rhost, port=rport, db=2)
    #for non-backbone models
    app.model_redis = redis.Redis(host=rhost, port=rport, db=3)
    app.pubsub_redis = redis.Redis(host=rhost, port=rport, db=4)
    app.secret_key = str(uuid.uuid4())

def make_default_user(app):
    docid = "defaultdoc"
    bokehuser = user.new_user(app.model_redis, "defaultuser",
                              str(uuid.uuid4()), apikey='nokey', docs=[])
         
    return bokehuser
    
def prepare_local():
    #monkeypatching
    def current_user(request):
        bokehuser = user.User.load(app.model_redis, "defaultuser")
        if bokehuser is None:
            bokehuser = make_default_user(app)
        return bokehuser
    def write_plot_file(username, codedata):
        return
    app.current_user = current_user
    app.write_plot_file = write_plot_file

http_server = None

def start_app(verbose=False):
    global http_server
    if verbose:
        print "Starting server on port %d..." % PORT
    http_server = WSGIServer(('', PORT), app,
                             handler_class=WebSocketHandler,
                             )
    http_server.serve_forever()

    

#database

#logging
