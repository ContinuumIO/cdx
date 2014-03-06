import gevent
import gevent.monkey
gevent.monkey.patch_all()

from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer

from flask import request, current_app, Flask
from app import cdx_app

import os
import atexit

import bokeh
print "bokeh: %s" % bokeh.__version__
import pandas
print "pandas: %s" % pandas.version.version

from bokeh.server.app import bokeh_app
from bokeh.server.start import prepare_app as bokeh_prepare_app, start_services as bokeh_start_services

#import objects so that we can resolve them
import cdx.objects
import cdx.services

import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

PORT = 5006
REDIS_PORT = 6379
IPYTHON_PORT = 10010
ARRAY_PORT = 10020
HEM_PORT = 9394

def prepare_app(username='defaultuser',
                userapikey='nokey',
                port=PORT,
                ipython_port=IPYTHON_PORT,
                arrayserver_port=ARRAY_PORT,
                redis_host='127.0.0.1',
                redis_port=REDIS_PORT,
                start_redis=True,
                work_dir=os.getcwd(),
                debug=True,
                debugjs=True):

    app = Flask("cdx")

    backend = {
        'type': 'redis',
        'redis_host': redis_host,
        'redis_port': redis_port,
        'start_redis': start_redis,
    }

    bokeh_prepare_app(backend)
    bokeh_app.work_dir = work_dir
    app.register_blueprint(bokeh_app)

    cdx_app.port = port
    cdx_app.ipython_port = ipython_port
    cdx_app.arrayserver_port = arrayserver_port
    cdx_app.username = username
    cdx_app.userapikey = userapikey
    cdx_app.work_dir = work_dir
    cdx_app.cdx_pids = os.path.join(cdx_app.work_dir, "cdxpids.json")

    import views
    app.register_blueprint(cdx_app)

    if debug:
        app.debug = True
        cdx_app.debug = True
        bokeh_app.debug = True

    if debugjs:
        app.debugjs = True
        cdx_app.debugjs = True
        bokeh_app.debugjs = True

    bokeh_start_services()
    start_services()

    return app

def start_services():
    mproc = cdx.services.start_ipython(cdx_app.cdx_pids, cdx_app.ipython_port, cdx_app.work_dir)
    cdx_app.ipython_proc = mproc
    atexit.register(stop_services)

def stop_services():
    cdx_app.ipython_proc.close()

def start_app(app):
    global http_server
    print "Starting server on port %d ..." % cdx_app.port
    http_server = WSGIServer(('', cdx_app.port), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
