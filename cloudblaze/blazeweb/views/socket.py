from flask import (
    render_template, request, current_app,
    send_from_directory, make_response)
import flask
import os
import simplejson
import logging
import uuid
import urlparse

from cloudblaze.blazeweb.app import app

import cloudblaze.blazeweb.blazeclient as blazeclient
import cloudblaze.continuumweb.bbmodel as bbmodel
import cloudblaze.blazeweb.views.common as common
import cloudblaze.blazeweb.wsmanager as wsmanager

log = logging.getLogger(__name__)

#web socket subscriber
@app.route('/sub')
def sub():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        wsmanager.run_socket(
            ws, current_app.wsmanager,
            lambda auth, topic : True, current_app.ph)
    return
