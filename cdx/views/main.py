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
import cdx.wsmanager as wsmanager
import cdx.models.user as user
import cdx.models.docs as docs
import cdx.controllers.maincontroller as maincontroller

#main pages

# @app.route('/cdx/')
# @app.route('/cdx/<path:unused>/')
# def index(*unused_all, **kwargs):
#     current_user = maincontroller.get_cdx_user(current_app, request)
#     if current_user is None:
#         #redirect to login, we don't have login page yet..
#         pass
#     return render_template('cdx.html', NODE_INSTALLED=False)

# @app.route('/cdx_help')
# @app.route('/cdx_help/<path:unused>/')
# def cdx_help(*unused_all, **kwargs):
#     current_user = maincontroller.get_cdx_user(current_app, request)
#     if current_user is None:
#         #redirect to login, we don't have login page yet..
#         pass
#     return render_template('cdx_help.html')

@app.route('/cdx/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')

@app.route('/cdx/userinfo/')
def get_user():
    user = maincontroller.get_cdx_user(current_app, request)
    return current_app.ph.serialize_web(user.to_public_json())


@app.route('/cdx/cdxinfo/<docid>')
def get_cdx_info(docid):
    doc = docs.Doc.load(app.model_redis, docid)
    user = maincontroller.get_cdx_user(current_app, request)
    if not ((user.username in doc.rw_users) or (user.username in doc.r_users)):
        return null
    plot_context_ref = doc.plot_context_ref
    all_models = current_app.collections.get_bulk(docid)
    all_models = [x.to_broadcast_json() for x in all_models]
    returnval = {'plot_context_ref' : plot_context_ref,
                 'docid' : docid,
                 'all_models' : all_models,
                 }
    returnval = current_app.ph.serialize_web(returnval)
    return returnval
