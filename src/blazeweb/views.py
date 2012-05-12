from app import app
from flask import request, current_app
import flask
import simplejson
import logging
import urlparse
import blazeclient
import stockreport
import wsmanager

log = logging.getLogger(__name__)

@app.route("/data/<path:datapath>", methods=['GET'])
def get_data(datapath):
    data_slice=get_slice(request)
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
    
# @app.route("/table/<path:datapath>/", methods=['GET'])
# def get_table(datapath=""):
#     data_slice=get_slice(request)
#     response, dataobj = blazeclient.raw_get(
#         current_app.rpcclient, datapath, data_slice=data_slice)
#     table_obj = blazeclient.build_table(
#             data, response['shape'], data_slice, datapath)
#     return simplejson.dumps(table_obj)

@app.route("/dataview/", methods=['GET'])
@app.route("/dataview/<path:datapath>", methods=['GET'])
@app.route("/monkey/<path:datapath>", methods=['GET'])
def get_dataview(datapath=""):
    data_slice=get_slice(request)
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
                                     
def get_slice(request):
    data_slice=request.args.get('data_slice', None)
    if data_slice is None:
        data_slice = [0, 100]
    else:
        data_slice = simplejson.loads(data_slice)
    return data_slice
    

@app.route('/sub')
def sub():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        wsmanager.run_socket(ws, current_app.wsmanager,
                             lambda auth, topic : True, current_app.ph)
    return
