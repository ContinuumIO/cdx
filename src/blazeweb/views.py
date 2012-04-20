from app import app
from flask import request, current_app
import simplejson

@app.route("/data/<path:datapath>", methods=['GET'])
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

