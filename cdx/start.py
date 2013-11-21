import gevent
import gevent.monkey
gevent.monkey.patch_all()

from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer

from flask import request, current_app, Flask
from app import cdx_app

import bokeh
print "bokeh: %s" % bokeh.__version__
import pandas
print "pandas: %s" % pandas.version.version

from bokeh.server.app import bokeh_app
from bokeh.server.start import prepare_app as bokeh_prepare_app
from bokeh.server.start import prepare_local as bokeh_prepare_local

#import objects so that we can resolve them
import cdx.objects
import bokeh.pandasobjects

import logging

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
                redis_port=REDIS_PORT,
                start_redis=True,
                work_dir=None,
                debug=True,
                debugjs=True,
                rhost='127.0.0.1'):
    app = Flask("cdx")
    prepare_bokeh(app, rhost=rhost, rport=redis_port,
                  debug=debug, debugjs=debugjs)
    cdx_app.port = port
    cdx_app.ipython_port = ipython_port
    cdx_app.arrayserver_port = arrayserver_port
    cdx_app.redis_port = redis_port
    cdx_app.start_redis = start_redis
    cdx_app.username = username
    cdx_app.userapikey = userapikey
    import views
    cdx_app.hem_port = HEM_PORT
    cdx_app.work_dir = work_dir or os.getcwd()
    cdx_app.cdx_pids = os.path.join(cdx_app.work_dir, "cdxpids.json")
    app.register_blueprint(cdx_app)
    if debug:
        app.debug = True
        cdx_app.debug = True
        bokeh_app.debug = True
    if debugjs:
        app.debugjs = True
        cdx_app.debugjs = True
        bokeh_app.debugjs = True
    start_services()
    return app

import services
import os
import atexit
def start_services():
    if cdx_app.start_redis:
        mproc = services.start_redis(cdx_app.cdx_pids, cdx_app.redis_port, cdx_app.work_dir)
        cdx_app.redis_proc = mproc
    mproc = services.start_ipython(cdx_app.cdx_pids, cdx_app.ipython_port, cdx_app.work_dir)
    cdx_app.ipython_proc = mproc
    atexit.register(service_exit)

def service_exit():
    if hasattr(cdx_app, 'redis_proc'):
        cdx_app.redis_proc.close()
    cdx_app.ipython_proc.close()


def prepare_bokeh(app, rhost='127.0.0.1', rport=REDIS_PORT, debug=True, debugjs=True):
    bokeh_prepare_app(rhost=rhost, rport=rport)
    bokeh_app.hem_port = HEM_PORT
    app.register_blueprint(bokeh_app)
    if debug:
        bokeh_app.debug = True
    if debugjs:
        bokeh_app.debugjs = True

def start_app(app, verbose=False):
    global http_server
    if verbose:
        print "Starting server on port %d..." % cdx_app.port
    http_server = WSGIServer(('', cdx_app.port), app,
                             handler_class=WebSocketHandler,
                             )
    http_server.serve_forever()

def prepare_local():
    bokeh_prepare_local()
