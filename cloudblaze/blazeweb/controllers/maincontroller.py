import gevent
import gevent.monkey
gevent.monkey.patch_all()
import gevent_zeromq
gevent_zeromq.monkey_patch()

import zmq
from gevent.pywsgi import WSGIServer
import uuid
import redis
from geventwebsocket.handler import WebSocketHandler

import cloudblaze.continuumweb.webzmqproxy as webzmqproxy
from cloudblaze.blazeweb.app import app
import cloudblaze.blazeweb.wsmanager as wsmanager
import blaze.server.rpc.protocol as protocol
import cloudblaze.continuumweb.bbmodel as bbmodel
import cloudblaze.blazeweb.views.deps

pubsub = "inproc://apppub"
pushpull = "inproc://apppull"

def prepare_app(reqrepaddr, rhost='localhost', desktopmode=True,
                rport=6379, timeout=1.0, ctx=None):
    app.debug = True
    app.proxy = webzmqproxy.Proxy(reqrepaddr, pushpull, pubsub,
                                  timeout=timeout, ctx=ctx)
    app.proxy.start()
    app.proxyclient = webzmqproxy.ProxyClient(pushpull, pubsub,
                                              timeout=timeout,
                                              ctx=ctx)
    app.proxyclient.start()
    app.rpcclient = webzmqproxy.ProxyRPCClient(app.proxyclient)
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

def shutdown_app():
    print 'shutting down app!'
    app.proxy.kill = True
    app.proxyclient.kill = True

http_server = WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
def start_app():
    http_server.serve_forever()
