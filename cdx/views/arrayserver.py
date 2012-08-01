from cdx.app import app
from flask import (
    render_template, request, current_app,
    send_from_directory, make_response)
import flask
import os
import logging
import uuid
import urlparse
import cdx.arrayserverclient as arrayserverclient
import cdx.views.common as common
import cdx.bbmodel as bbmodel
import cdx.wsmanager as wsmanager

log = logging.getLogger(__name__)

#http api for arrayserver server
@app.route("/metadata/", methods=['GET'])
@app.route("/metadata/<path:datapath>", methods=['GET'])
def get_metadata(datapath="/"):
    depth = request.args.get('depth', None)
    if depth is not None:
        depth = int(depth)
    response = arrayserverclient.get_tree(
        current_app.rpcclient, datapath, depth=depth)
    return app.ph.serialize_web(response)

@app.route("/data/<path:datapath>", methods=['GET'])
def get_data(datapath):
    data_slice=common.get_slice(request)
    response, dataobj = arrayserverclient.raw_get(
        current_app.rpcclient, datapath, data_slice=data_slice)
    if response['type'] != 'group':
        arr = dataobj[0]
        if arr.dtype.names:
            response['data'] = arr.tolist()
            response['colnames'] = arr.dtype.names
        else:
            if len(arr.shape) == 1:
                response['data'] = arr.reshape((len(arr), 1)).tolist()
                response['colnames'] = ['0']
            else:
                response['data'] = arr.tolist()
                response['colnames'] = [str(x) for x in range(arr.shape[1])]
    return app.ph.serialize_web(response)

# @app.route("/data/<path:datapath>", methods=['DELETE'])
# def delete_data(datapath):
#     newmsg = {'path' : datapath}
#     retval = current_app.proxyclient.request([simplejson.dumps(newmsg)])
#     return retval[0]

# @app.route("/data/<path:datapath>", methods=['POST'])
# def create_data(datapath):
#     newmsg = {'path' : datapath,
#               'message' : request.form['message']}
#     retval = current_app.proxyclient.request([simplejson.dumps(newmsg)])
#     return retval[0]

# @app.route("/data/<path:datapath>", methods=['PATCH'])
# def update_data(datapath):
#     newmsg = {'path' : datapath,
#               'message' : request.form['message']}
#     retval = current_app.proxyclient.request([appsimplejson.dumps(newmsg)])
#     return retval[0]


@app.route("/summary/<path:datapath>")
def summary(datapath):
    summary =  arrayserverclient.get_summary(current_app.rpcclient, datapath)
    return current_app.ph.serialize_web(summary)

@app.route("/bulksummary/")
def bulk_summary():
    paths = app.ph.deserialize_web(request.args['paths'])
    summaries = []
    for p in paths:
        try:
            summary = arrayserverclient.get_summary(current_app.rpcclient, p)
        except Exception as e:
            log.exception(e)
            summary = None
        summaries.append(summary)
    print 'SUMMARIES', summaries
    return current_app.ph.serialize_web(summaries)
