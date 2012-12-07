from flask import (
    render_template, request, current_app,
    send_from_directory, make_response)
import flask
import os
import logging
import uuid
import urlparse

from cdx.blueprint import cdx_blueprint

import cdx.bbmodel as bbmodel
import cdx.wsmanager as wsmanager
import cdx.models.user as user
import cdx.models.docs as docs
import cdx.models.convenience as mconv

#main pages

@cdx_blueprint.route('/cdx/')
@cdx_blueprint.route('/cdx/<path:unused>/')
def index(*unused_all, **kwargs):
    return render_template('cdx.html')


@cdx_blueprint.route('/cdx/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')

@cdx_blueprint.route('/cdx/userinfo/')
def get_user():
    user = current_app.current_user(request)
    return current_app.ph.serialize_web(user.to_public_json())
def _make_plot_file(docid, apikey, url):
    lines = ["from cdxlib import mpl",
             "p = mpl.PlotClient('%s', '%s', '%s')" % (docid, url, apikey)]
    return "\n".join(lines)

def write_plot_file(docid, apikey, url):
    user = current_app.current_user(request)
    codedata = _make_plot_file(docid, apikey, url)
    current_app.write_plot_file(user.username, codedata)

@cdx_blueprint.route('/cdx/cdxinfo/<docid>')
def get_cdx_info(docid):
    doc = docs.Doc.load(current_app.model_redis, docid)
    user = current_app.current_user(request)
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
@cdx_blueprint.route('/cdx/publiccdxinfo/<docid>')
def get_public_cdx_info(docid):
    doc = docs.Doc.load(current_app.model_redis, docid)
    plot_context_ref = doc.plot_context_ref
    all_models = current_app.collections.get_bulk(docid)
    mod1 = all_models[1]
    all_models_json = [
        x.to_broadcast_json() for x in all_models if x.get('public', False)]
    all_models_json2 = [x.to_broadcast_json() for x in all_models]
    if len(all_models_json2) == 0:
        return False
    print all_models_json
    returnval = {'plot_context_ref' : plot_context_ref,
                 'docid' : docid,
                 'all_models' : all_models_json2,
                 'apikey' : doc.apikey}
    returnval = current_app.ph.serialize_web(returnval)
    #return returnval

    return (returnval, "200",
            {"Access-Control-Allow-Origin": "*"})


@cdx_blueprint.route('/cdx/sampleerror')
def sampleerror():
    return 1 + "sdf"
