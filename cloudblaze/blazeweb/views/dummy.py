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
#test app view code goes here.

#dummy pages for browsing hdf5 data sets in blaze
@app.route("/dataview/", methods=['GET'])
@app.route("/dataview/<path:datapath>", methods=['GET'])
def get_dataview(datapath=""):
    data_slice=common.get_slice(request)
    response, dataobj = blazeclient.raw_get(
        current_app.rpcclient, datapath, data_slice=data_slice)
    if response['type'] == 'group':
        base = request.base_url
        if not base.endswith('/'): base += "/"
        child_paths = [[x, urlparse.urljoin(base, x)] \
                       for x in response['children']]
        return flask.render_template('simplegroup.html', children=child_paths)
    else:
        data = dataobj[0]
        table_obj = blazeclient.build_table(
            data, response['shape'], data_slice, datapath)
        return flask.render_template('simpledataset.html',
                                     table_obj=simplejson.dumps(table_obj))


#main page for interactive plotting
@app.route("/interactive/<docid>")
def interact(docid):
    models = current_app.collections.get_bulk(docid)
    interactive_context = [x for x in models if x.typename == 'InteractiveContext']
    if len(interactive_context) == 0:
        interactive_context = bbmodel.ContinuumModel(
            'InteractiveContext', docs=[docid])
        current_app.collections.add(interactive_context)
        models.insert(0, interactive_context)
    else:
        interactive_context = interactive_context[0]
    models = [x.to_broadcast_json() for x in models]
    
    resp = make_response(flask.render_template(
        'blank.html', topic=docid,
        all_components=current_app.ph.serialize_web(models),
        main = current_app.ph.serialize_web(interactive_context.ref())
        ))
    #resp.set_cookie('clientid', str(uuid.uuid4()))
    return resp
