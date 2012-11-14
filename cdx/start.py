from flask import request
import gevent
import gevent.monkey
gevent.monkey.patch_all()
import uuid
import socket
import redis
from cdx.app import app
import cdx.wsmanager as wsmanager
from cdxlib import protocol
import cdx.bbmodel as bbmodel
import cdx.models.user as user
import cdx.models.docs as docs
#import cdx.ipython.runnotebook as runnotebook
import logging
import time
port = 5006
log = logging.getLogger(__name__)

pubsub = "inproc://apppub"
pushpull = "inproc://apppull"

def prepare_app(rhost='127.0.0.1', rport=6379):
    #must import views before running apps
    import cdx.views.deps
    app.wsmanager = wsmanager.WebSocketManager()
    app.ph = protocol.ProtocolHelper()
    app.collections = bbmodel.ContinuumModelsStorage(
        redis.Redis(host=rhost, port=rport, db=2)
        )
    #for non-backbone models
    app.model_redis = redis.Redis(host=rhost, port=rport, db=3)
    app.secret_key = str(uuid.uuid4())
    
def shutdown_app():
    print 'shutting down app!'
    app.proxy.kill = True
    app.proxyclient.kill = True


