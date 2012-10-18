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
from sqlalchemy.orm import sessionmaker
from geventwebsocket.handler import WebSocketHandler

#import cdx.webzmqproxy as webzmqproxy
import cdx.settings as settings
from cdx.app import app
import cdx.wsmanager as wsmanager
import arrayserver.protocol as protocol
import cdx.bbmodel as bbmodel
import cdx.models.user as user
import cdx.models.docs as docs
#import cdx.ipython.runnotebook as runnotebook
import logging
import time
log = logging.getLogger(__name__)

pubsub = "inproc://apppub"
pushpull = "inproc://apppull"

def prepare_app(rhost='localhost', rport=6379):
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
    app.dbengine = settings.get_sqlalchemy_engine()
    app.Session = sessionmaker(bind=app.dbengine)
    return app

def shutdown_app():
    print 'shutting down app!'
    app.proxy.kill = True
    app.proxyclient.kill = True

http_server = WSGIServer(('', settings.port), app, handler_class=WebSocketHandler)
def start_app():
    http_server.serve_forever()

if __name__ == "__main__":
    prepare_app()    
    import werkzeug.serving
    @werkzeug.serving.run_with_reloader
    def helper ():
        start_app()
