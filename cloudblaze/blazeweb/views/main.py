from flask import (session,
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
import cloudblaze.blazeweb.wsmanager as wsmanager
import cloudblaze.blazeweb.models.user as user
import cloudblaze.blazeweb.controllers.maincontroller as maincontroller
import cloudblaze.blazeweb.controllers.namespaces as namespaces

#main pages
    
@app.route('/')
def index():
    current_user = maincontroller.get_current_user(current_app, session)
    kernel_id = namespaces.create_or_load_namespace_for_user(
        current_app, current_user, session)
    print 'KERNEL', kernel_id
    return render_template('cdx.html', user=current_user.email)         

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
			       'favicon.ico', mimetype='image/x-icon')
    
@app.route('/pageRender/<filename>')
def pageRender(filename):
    app.logger.debug('pageRender filename=[%s]',filename)
    # Note the corresponding html file must be in the templates folder.
    return render_template(filename + '.html') 
