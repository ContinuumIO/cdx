import gevent
import gevent.monkey
gevent.monkey.patch_all()
import gevent_zeromq
gevent_zeromq.monkey_patch()

import zmq
from gevent.pywsgi import WSGIServer
import uuid
import socket
import redis
from geventwebsocket.handler import WebSocketHandler

#import cdx.webzmqproxy as webzmqproxy
from cdx.app import app
import cdx.wsmanager as wsmanager
import arrayserver.protocol as protocol
import cdx.bbmodel as bbmodel
import cdx.models.user as user
import cdx.models.docs as docs
from wakariserver.djangointerface import (get_session_data,
                                          get_user,
                                          get_current_user,
                                          login_required
                                          )
#import cdx.ipython.runnotebook as runnotebook
import logging
import time
log = logging.getLogger(__name__)

pubsub = "inproc://apppub"
pushpull = "inproc://apppull"

def prepare_app(reqrepaddr, rhost='localhost', desktopmode=True,
                rport=6379, timeout=15.0, ctx=None):
    #must import views before running apps
    import cdx.views.deps
    app.debug = True
    app.wsmanager = wsmanager.WebSocketManager()
    app.ph = protocol.ProtocolHelper()
    app.collections = bbmodel.ContinuumModelsStorage(
        redis.Redis(host=rhost, port=rport, db=2)
        )
    #for non-backbone models
    app.model_redis = redis.Redis(host=rhost, port=rport, db=3)
    app.secret_key = str(uuid.uuid4())
    app.desktopmode = desktopmode
    return app

def get_cdx_user(app, session=None):
    """reads django user information, if a user is present,
    we create/ensure an equivalent one lives in our DB.
    We'll call this every time for now.. but we can be more
    efficient about it in the future
    """
    try:
        dbsession = session if session else app.Session() 
        auth_user, wakari_user = get_current_user(dbsession, request)
        if auth_user is None or wakari_user is None:
            return None
        else:
            cdxuser = user.User.load(app.model_redis, auth_user.username)
            if cdxuser is None:
                docid = str(uuid.uuid4())
                doc = docs.new_doc(app, docid, 'main', [email])
                cdxuser = user.new_user(app.model_redis,
                                        auth_user.email, str(uuid.uuid4()), docs=[doc.docid])
            return cdxuser
    finally:
        #close session if it was not passed  in
        if not session:
            dbsession.close()
        
def shutdown_app():
    print 'shutting down app!'
    app.proxy.kill = True
    app.proxyclient.kill = True

http_server = WSGIServer(('', 5006), app, handler_class=WebSocketHandler)
def start_app():
    http_server.serve_forever()
