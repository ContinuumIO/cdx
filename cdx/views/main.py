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
import cdx.models.convenience as mconv

#main pages

@app.route('/cdx/')
@app.route('/cdx/<path:unused>/')
def index(*unused_all, **kwargs):
    return render_template('cdx.html')


@app.route('/cdx/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')

@app.route('/cdx/userinfo/')
def get_user():
    user = app.current_user(request)
    return current_app.ph.serialize_web(user.to_public_json())
def _make_plot_file(docid, apikey, url):
    lines = ["from cdxlib import mpl",
             "p = mpl.PlotClient('%s', '%s', '%s')" % (docid, url, apikey)]
    return "\n".join(lines)

def write_plot_file(docid, apikey, url):
    user = app.current_user(request)
    codedata = _make_plot_file(docid, apikey, url)
    app.write_plot_file(user.username, codedata)

@app.route('/cdx/cdxinfo/<docid>')
def get_cdx_info(docid):
    doc = docs.Doc.load(app.model_redis, docid)
    user = app.current_user(request)
    if not mconv.can_write_doc(doc, user):
        return null
    plot_context_ref = doc.plot_context_ref
    all_models = docs.prune_and_get_valid_models(current_app, docid)
    print "num models", len(all_models)
    all_models = [x.to_broadcast_json() for x in all_models]
    returnval = {'plot_context_ref' : plot_context_ref,
                 'docid' : docid,
                 'all_models' : all_models,
                 'apikey' : doc.apikey}
    returnval = current_app.ph.serialize_web(returnval)
    write_plot_file(docid, doc.apikey, request.scheme + "://" + request.host)
    return returnval

import pdb
@app.route('/cdx/publiccdxinfo/<docid>')
def get_public_cdx_info(docid):
    doc = docs.Doc.load(app.model_redis, docid)
    plot_context_ref = doc.plot_context_ref
    all_models = docs.prune_and_get_valid_models(current_app, docid)
    public_models = [x for x in all_models if x.get('public', False)]
    if len(public_models) == 0:
        return False
    all_models_json = [x.to_broadcast_json() for x in all_models]
    returnval = {'plot_context_ref' : plot_context_ref,
                 'docid' : docid,
                 'all_models' : all_models_json,
                 'apikey' : doc.apikey}
    returnval = current_app.ph.serialize_web(returnval)
    #return returnval

    return (returnval, "200",
            {"Access-Control-Allow-Origin": "*"})


@app.route('/cdx/sampleerror')
def sampleerror():
    return 1 + "sdf"
