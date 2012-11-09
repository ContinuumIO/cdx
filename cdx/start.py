from flask import request
import gevent
import gevent.monkey
gevent.monkey.patch_all()
from gevent.pywsgi import WSGIServer
import uuid
import socket
import redis
from sqlalchemy.orm import sessionmaker
from geventwebsocket.handler import WebSocketHandler

import settings
from cdx.app import app
import cdx.wsmanager as wsmanager
from cdxlib import protocol
import cdx.bbmodel as bbmodel
import cdx.models.user as user
import cdx.models.docs as docs
#import cdx.ipython.runnotebook as runnotebook
import logging
import time
log = logging.getLogger(__name__)

pubsub = "inproc://apppub"
pushpull = "inproc://apppull"

def prepare_app(rhost='127.0.0.1', rport=6379):
    #must import views before running apps
    import cdx.views.deps
    app.debug = settings.ENV.DEBUG
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
    from flask import _request_ctx_stack
    from werkzeug.local import LocalProxy

    class RequestSession(object):
        def __init__(self):
            self.is_testing = False

        def setup_app(self, app):
            """
            Configures an application. This registers a `before_request` and an
            `after_request` call, and sets up a request lived database_session
            :param app: The `flask.Flask` object to configure.
            """
            app.before_request(self._start_request)
            app.after_request(self._after_request)
            self.is_testing = False

        def _start_request(self):
            if not self.is_testing:
                #in the testing context we want the process wide session
                request.session = app.Session()

        def _after_request(self, response):
            if not self.is_testing:
                #in the testing context, tearDown should be the only place
                #commit is called
                request.session.commit()
                request.session.close()
            return response

    rs = RequestSession()
    rs.setup_app(app)
    return app

def shutdown_app():
    print 'shutting down app!'
    app.proxy.kill = True
    app.proxyclient.kill = True

http_server = WSGIServer(('', settings.port), app,
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
