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

import cloudblaze.blazeweb.blazeclient
import cloudblaze.continuumweb.bbmodel as bbmodel
import cloudblaze.blazeweb.views.common as common
import cloudblaze.blazeweb.wsmanager as wsmanager

#main pages
@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/x-icon')
    
@app.route('/pageRender/<filename>')
def pageRender(filename):
    app.logger.debug('pageRender filename=[%s]',filename)
    # Note the corresponding html file must be in the templates folder.
    return render_template(filename + '.html') 
