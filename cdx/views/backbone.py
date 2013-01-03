from cdx.app import app
from flask import (
        render_template, request, current_app,
        send_from_directory, make_response)
import flask
import os
import logging
import uuid
import urlparse
import cdx.bbmodel as bbmodel
import cdx.wsmanager as wsmanager
import cdx.models.convenience as convenience
log = logging.getLogger(__name__)
import cdx.models.docs as docs

#backbone model apis
@app.route("/cdx/bb/<docid>/reset", methods=['GET'])
def reset(docid):
    if not convenience.can_write_from_request(docid, request, app):
        return app.ph.serialize_web(
            {'msgtype' : 'error',
             'msg' : 'unauthorized'}
            )
    models = current_app.collections.get_bulk(docid)
    for m in models:
        if m.typename != 'CDXPlotContext':
            current_app.collections.delete(m.typename, m.id)
        else:
            m.set('children', [])
            current_app.collections.add(m)
    return 'success'

#backbone model apis
@app.route("/cdx/bb/<docid>/rungc", methods=['GET'])
def rungc(docid):
    if not convenience.can_write_from_request(docid, request, app):
        return app.ph.serialize_web(
            {'msgtype' : 'error',
             'msg' : 'unauthorized'}
            )
    all_models = docs.prune_and_get_valid_models(current_app, docid, delete=True)
    return 'success'

@app.route("/cdx/bb/<docid>/bulkupsert", methods=['POST'])
def bulk_upsert(docid):
    if not convenience.can_write_from_request(docid, request, app):
        return app.ph.serialize_web(
            {'msgtype' : 'error',
             'msg' : 'unauthorized'}
            )
    data = current_app.ph.deserialize_web(request.data)
    models = [bbmodel.ContinuumModel(x['type'], **x['attributes']) \
              for x in data]
    for m in models:
        if m.get('docs') is None:
            m.set('docs', [docid])
        m.set('created', True)
        current_app.collections.add(m)
    docs = set()
    for m in models:
        docs.update(m.get('docs'))
    clientid = request.headers.get('Continuum-Clientid', None)
    for doc in docs:
        relevant_models = [x for x in models if doc in x.get('docs')]
        current_app.wsmanager.send("cdxplot:" + doc, app.ph.serialize_web(
            {'msgtype' : 'modelpush',
             'modelspecs' : [x.to_broadcast_json() for x in relevant_models]}),
            exclude={clientid})
    return app.ph.serialize_web(
        {'msgtype' : 'modelpush',
         'modelspecs' : [x.to_broadcast_json() for x in relevant_models]})

@app.route("/cdx/bb/<docid>/<typename>/", methods=['POST'])
@app.route("/cdx/bb/<docid>/<typename>", methods=['POST'])
def create(docid, typename):
    if not convenience.can_write_from_request(docid, request, app):
        return app.ph.serialize_web(
            {'msgtype' : 'error',
             'msg' : 'unauthorized'}
            )
    log.debug("create, %s, %s", docid, typename)
    modeldata = current_app.ph.deserialize_web(request.data)
    model = bbmodel.ContinuumModel(typename, **modeldata)
    if model.get('docs') is None:
        model.set('docs', [docid])
    model.set('created', True)
    current_app.collections.add(model)
    if model.typename == 'ObjectArrayDataSource':
        print current_app.collections.get(model.typename, model.id)
        print current_app.collections.get(model.typename, model.id).id
    clientid=request.headers.get('Continuum-Clientid', None)
    for doc in model.get('docs'):
        current_app.wsmanager.send("cdxplot:" + doc, app.ph.serialize_web(
            {'msgtype' : 'modelpush',
             'modelspecs' : [model.to_broadcast_json()]}),
            exclude={clientid})
    return app.ph.serialize_web(model.to_json())

@app.route("/cdx/bb/<docid>/<typename>/<id>", methods=['PUT'])
def put(docid, typename, id):
    if not convenience.can_write_from_request(docid, request, app):
        return app.ph.serialize_web(
            {'msgtype' : 'error',
             'msg' : 'unauthorized'}
            )
    modeldata = current_app.ph.deserialize_web(request.data)
    if typename == 'CDXPlotContext':
        log.debug("put, %s, %s, %s", docid, typename, len(modeldata['children']))
    else:
        log.debug("put, %s, %s", docid, typename)
    model = bbmodel.ContinuumModel(typename, **modeldata)
    if model.get('docs') is None:
        model.set('docs', [docid])
    current_app.collections.add(model)
    clientid=request.headers.get('Continuum-Clientid', None)
    for doc in model.get('docs'):
        current_app.wsmanager.send("cdxplot:" + doc, app.ph.serialize_web(
            {'msgtype' : 'modelpush',
             'modelspecs' : [model.to_broadcast_json()]}),
                                   exclude={clientid})
    return app.ph.serialize_web(model.to_json())

@app.route("/cdx/bb/<docid>/", methods=['GET'])
@app.route("/cdx/bb/<docid>/<typename>/", methods=['GET'])
@app.route("/cdx/bb/<docid>/<typename>/<id>", methods=['GET'])
def get(docid, typename=None, id=None):
    #not distinguishing between read/write yet
    if not convenience.can_write_from_request(docid, request, app):
        return app.ph.serialize_web(None)
    if typename is not None and id is not None:
        model = current_app.collections.get(typename, id)
        if model is not None and docid in model.get('docs'):
            return app.ph.serialize_web(model.to_json())
        return app.ph.serialize_web(None)
    else:
        models = current_app.collections.get_bulk(docid, typename=typename)
        if typename is not None:
            return app.ph.serialize_web([x.to_json() for x in models])
        else:
            return app.ph.serialize_web([x.to_broadcast_json() for x in models])

@app.route("/cdx/bb/<docid>/<typename>/<id>", methods=['DELETE'])
def delete(docid, typename, id):
    if not convenience.can_write_from_request(docid, request, app):
        return app.ph.serialize_web(
            {'msgtype' : 'error',
             'msg' : 'unauthorized'}
            )
    model = current_app.collections.get(typename, id)
    log.debug("DELETE, %s, %s", docid, typename)
    clientid = request.headers.get('Continuum-Clientid', None)
    if docid in model.get('docs'):
        current_app.collections.delete(typename, id)
        for doc in model.get('docs'):
            current_app.wsmanager.send("cdxplot:" + doc, app.ph.serialize_web(
                {'msgtype' : 'modeldel',
                 'modelspecs' : [model.to_broadcast_json()]}),
                                       exclude={clientid})
        return app.ph.serialize_web(model.to_json())
    else:
        return "INVALID"
