from cdx import start
from cdx.blueprint import cdx_blueprint
import flask
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from cdx.app import app
import cdx.models.user as user
import cdx.models.docs as docs
import uuid
import os
import logging
app = flask.Flask('cdx')
app.register_blueprint(cdx_blueprint)
start.prepare_app(app)
start.prepare_local(app)

if __name__ == "__main__":
    start.start_app(app)

