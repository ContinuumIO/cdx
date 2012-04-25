from app import app
from flask import request, current_app
import flask
import simplejson
import logging
import urlparse

log = logging.getLogger(__name__)


@app.route("/data/<path:datapath>/", methods=['GET'])
def get_data(datapath):
    datapath = "/" + datapath
    retval, dataobj = current_app.rpcclient.rpc(
        'get', datapath,
        data_slice=request.args.get('data_slice', None))
    if retval['type'] == 'group':
        return simplejson.dumps(retval)
    else:
        retval['data'] = dataobj[0].tolist()
        return simplejson.dumps(retval)

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

@app.route("/dataview/", methods=['GET'])
@app.route("/dataview/<path:datapath>/", methods=['GET'])
def get_dataview(datapath=""):
    import numpy as np
    response = get_data(datapath)
    response = simplejson.loads(response)
    print response
    if response['type'] == 'group':
        child_paths = [[x, urlparse.urljoin(request.base_url, x)] for x in response['children']]
        return flask.render_template('simplegroup.html', children=child_paths)
    else:
        data = np.asarray(response['data'])
        if len(data.shape) < 2:
            columns = range(1)
            data = [[x] for x in data]
        else:
            columns = range(data.shape[1])
            data = data.tolist()
        #import pdb;pdb.set_trace()
        return flask.render_template('simpledataset.html', columns=simplejson.dumps(columns),
                                     data=simplejson.dumps(data))
