from flask import request
import gevent
import gevent.monkey
gevent.monkey.patch_all()
from gevent.pywsgi import WSGIServer
import uuid
import socket
import redis
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine
from geventwebsocket.handler import WebSocketHandler
from cdx.app import app
import cdx.wsmanager as wsmanager
from cdxlib import protocol
import cdx.bbmodel as bbmodel
import cdx.models.user as user
import cdx.models.docs as docs
#import cdx.ipython.runnotebook as runnotebook
import logging
import time
from environments import ENV
from wakariserver.flasklib import RequestSession
port = 5006
log = logging.getLogger(__name__)

pubsub = "inproc://apppub"
pushpull = "inproc://apppull"

def prepare_app(rhost='127.0.0.1', rport=6379):
    #must import views before running apps
    import cdx.views.deps
    app.debug = ENV.DEBUG
    app.wsmanager = wsmanager.WebSocketManager()
    app.ph = protocol.ProtocolHelper()
    app.collections = bbmodel.ContinuumModelsStorage(
        redis.Redis(host=rhost, port=rport, db=2)
        )
    #for non-backbone models
    app.model_redis = redis.Redis(host=rhost, port=rport, db=3)
    app.secret_key = str(uuid.uuid4())
    app.dbengine = create_engine(ENV.DB_CONNSTRING)
    app.Session = sessionmaker(bind=app.dbengine)
    rs = RequestSession(app)
    rs.setup_app()
    return app

def shutdown_app():
    print 'shutting down app!'
    app.proxy.kill = True
    app.proxyclient.kill = True

http_server = WSGIServer(('', port), app,
                         handler_class=WebSocketHandler,
                         keyfile="/etc/nginx/wakari.key",
                         certfile="/etc/nginx/wakari.crt"
                         )
def start_app():
    http_server.serve_forever()

if __name__ == "__main__":
    prepare_app()
    import werkzeug.serving
    @werkzeug.serving.run_with_reloader
    def helper ():
        start_app()
