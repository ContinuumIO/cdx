from flask import (
    render_template, request, current_app,
    send_from_directory, make_response)
import flask
import os
import logging
import uuid
import urlparse

from cdx.app import app

import cdx.bbmodel as bbmodel
import cdx.views.common as common
import cdx.wsmanager as wsmanager

log = logging.getLogger(__name__)

#web socket subscriber
@app.route('/cdx/sub')
def sub():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        wsmanager.run_socket(
            ws, current_app.wsmanager,
            lambda auth, topic : True, current_app.ph)
    return
