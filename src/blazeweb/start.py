import gevent
import gevent.monkey
gevent.monkey.patch_all()
from gevent_zeromq import zmq
from gevent.queue import Queue
from gevent.pywsgi import WSGIServer

from app import app
import views
import time

import continuumweb.webzmqproxy as webzmqproxy
pubsub = "inproc://#1"
pushpull = "inproc://#3"

def prepare_app(reqrepaddr, ctx=None):
	app.debug = True
	if ctx is None:
		ctx = zmq.Context()
	app.proxy = webzmqproxy.Proxy(reqrepaddr, pushpull, pubsub, ctx=ctx)
	app.proxy.start()
	app.proxyclient = webzmqproxy.ProxyClient(pushpull, pubsub, ctx=ctx)
	app.proxyclient.start()
	return app

def start_app():
	http_server = WSGIServer(('', 5000), app)
	http_server.serve_forever()

	
if __name__ == "__main__":
	import sys
	reqrepaddr = sys.argv[1]
	prepare_app(reqrepaddr)
	#start_app()
