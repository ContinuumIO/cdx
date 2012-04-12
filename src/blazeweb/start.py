import gevent
import gevent.monkey
gevent.monkey.patch_all()
from gevent_zeromq import zmq
from gevent.queue import Queue

from gevent.wsgi import WSGIServer
from app import app
import views

import continuumweb.webzmqproxy as webzmqproxy

def start_app(reqrepaddr):
	app.debug = True
	ctx = zmq.Context()
	app.proxy = webzmqproxy.Proxy(reqrepaddr, "inproc://#1", "inproc://#2", ctx)	
	app.proxyclient = webzmqproxy.ProxyClient("inproc://#1", "inproc://#2", ctx)
	http_server = WSGIServer(('', 5000), app)
	http_server.serve_forever()

	
if __name__ == "__main__":
	import sys
	reqrepaddr = sys.argv[1]
	start_app(reqrepaddr)
