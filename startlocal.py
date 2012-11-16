from cdx import start
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from cdx.app import app
import cdx.models.user as user
import cdx.models.docs as docs
import uuid

import os
import logging
start.prepare_app()
start.prepare_local()

if __name__ == "__main__":
    start.start_app()

