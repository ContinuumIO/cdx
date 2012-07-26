from flask import (session,
    render_template, request, current_app,
    send_from_directory, make_response)
import flask
import os
import logging
import uuid
import urlparse

from cloudblaze.blazeweb.app import app

import cloudblaze.blazeweb.blazeclient
import cloudblaze.continuumweb.bbmodel as bbmodel
import cloudblaze.blazeweb.wsmanager as wsmanager
import cloudblaze.blazeweb.models.user as user
import cloudblaze.blazeweb.models.docs as docs
import cloudblaze.blazeweb.controllers.maincontroller as maincontroller
import cloudblaze.blazeweb.controllers.namespaces as namespaces
import cloudblaze.ipython.runnotebook as runnotebook

#main pages

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')

@app.route('/pageRender/<filename>')
def pageRender(filename):
    app.logger.debug('pageRender filename=[%s]',filename)
    # Note the corresponding html file must be in the templates folder.
    return render_template(filename + '.html')

@app.route('/pageRenderTests/<filename>')
def pageRender2(filename):
    app.logger.debug('pageRender filename=[%s]',filename)
    # Note the corresponding html file must be in the templates folder.
    return render_template("tests/" + filename + '.html')

@app.route('/cdx')
@app.route('/cdx/<unused>')
@app.route('/cdx/<unused>/<unused_2>')
@app.route('/cdx/<unused>/<unused_2>/<unused_3>')
def index(*unused_all, **kwargs):
    current_user = maincontroller.get_current_user(current_app, session)
    if current_user is None:
        #redirect to login, we don't have login page yet..
        pass
    return render_template('cdx.html')

@app.route('/cdx_help')
@app.route('/cdx_help/<unused>')
@app.route('/cdx_help/<unused>/<unused_2>')
@app.route('/cdx_help/<unused>/<unused_2>/<unused_3>')
def cdx_help(*unused_all, **kwargs):
    current_user = maincontroller.get_current_user(current_app, session)
    if current_user is None:
        #redirect to login, we don't have login page yet..
        pass
    return render_template('cdx_help.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')

@app.route('/pageRender/<filename>')
def pageRender(filename):
    app.logger.debug('pageRender filename=[%s]',filename)
    # Note the corresponding html file must be in the templates folder.
    return render_template(filename + '.html')

@app.route('/docinfo/<docid>')
def get_doc(docid):
    doc = docs.Doc.load(app.model_redis, docid)
    user = maincontroller.get_current_user(current_app, session)
    if (user.email in doc.rw_users) or (user.email in doc.r_users):
        return current_app.ph.serialize_web(
            {'plot_context' : doc.plot_context_ref})

@app.route('/userinfo/')
def get_user():
    user = maincontroller.get_current_user(current_app, session)
    return current_app.ph.serialize_web(user.to_public_json())

@app.route('/ipythoninfo/<docid>')
def get_ipython_info(docid):
    docid, kernelid, notebookid = namespaces.create_or_load_namespace(
        current_app, docid)
    return current_app.ph.serialize_web(
        {'docid' : docid,
         'kernelid' : kernelid,
         'notebookid' : notebookid,
         'baseurl' : request.host.split(':')[0] + ':' + str(runnotebook.app.port)
         }
        )
@app.route('/cdxinfo/<docid>')
def get_cdx_info(docid):
    doc = docs.Doc.load(app.model_redis, docid)
    user = maincontroller.get_current_user(current_app, session)
    if not ((user.email in doc.rw_users) or (user.email in doc.r_users)):
        return null
    plot_context_ref = doc.plot_context_ref
    all_models = current_app.collections.get_bulk(docid)
    all_models = [x.to_broadcast_json() for x in all_models]
    docid, kernelid, notebookid = namespaces.create_or_load_namespace(
        current_app, docid)
    ipythonbaseurl = request.host.split(':')[0] + ':' + str(runnotebook.app.port)
    returnval = {'plot_context_ref' : plot_context_ref,
                 'docid' : docid,
                 'kernelid' : kernelid,
                 'notebookid' : notebookid,
                 'baseurl' : ipythonbaseurl,
                 'all_models' : all_models,
                 'blazeaddress' : current_app.proxy.reqrepaddr
                 }
    returnval = current_app.ph.serialize_web(returnval)
    return returnval
