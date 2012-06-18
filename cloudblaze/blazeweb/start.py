import gevent
import gevent.monkey
gevent.monkey.patch_all()
import gevent_zeromq
gevent_zeromq.monkey_patch()
import zmq

from gevent.queue import Queue
from gevent.pywsgi import WSGIServer

from app import app
import views
import time
from geventwebsocket.handler import WebSocketHandler
import cloudblaze.continuumweb.webzmqproxy as webzmqproxy
import wsmanager
import blaze.server.rpc.protocol as protocol
import cloudblaze.continuumweb.bbmodel as bbmodel
import redis

pubsub = "inproc://apppub"
pushpull = "inproc://apppull"

def prepare_app(reqrepaddr, rhost='localhost', rport=6379, timeout=1.0, ctx=None):
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
    return app

http_server = WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
def start_app():
    http_server.serve_forever()

def shutdown_app():
    print 'shutting down app!'
    app.proxy.kill = True
    app.proxyclient.kill = True
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    prepare_app(reqrepaddr)
    start_app()


        
