from cloudblaze.blazeweb.app import app
from flask import (
	render_template, request, current_app,
	send_from_directory, make_response)
import flask
import os
import simplejson
import logging
import uuid
import urlparse
import cloudblaze.blazeweb.blazeclient as blazeclient
import cloudblaze.blazeweb.views.common as common
import cloudblaze.continuumweb.bbmodel as bbmodel
import cloudblaze.blazeweb.wsmanager as wsmanager

log = logging.getLogger(__name__)

#http api for blaze server
@app.route("/data/<path:datapath>", methods=['GET'])
def get_data(datapath):
    data_slice=common.get_slice(request)
    response, dataobj = blazeclient.raw_get(
        current_app.rpcclient, datapath, data_slice=data_slice)
    if response['type'] != 'group': response['data'] = dataobj[0].tolist()
    return simplejson.dumps(response)

@app.route("/data/<path:datapath>", methods=['DELETE'])
def delete_data(datapath):
    newmsg = {'path' : datapath}
    retval = current_app.proxyclient.request([simplejson.dumps(newmsg)])
    return retval[0]

@app.route("/data/<path:datapath>", methods=['POST'])
def create_data(datapath):
    newmsg = {'path' : datapath,
              'message' : request.form['message']}
    retval = current_app.proxyclient.request([simplejson.dumps(newmsg)])
    return retval[0]
    
@app.route("/data/<path:datapath>", methods=['PATCH'])
def update_data(datapath):
    newmsg = {'path' : datapath,
              'message' : request.form['message']}
    retval = current_app.proxyclient.request([simplejson.dumps(newmsg)])
    return retval[0]
