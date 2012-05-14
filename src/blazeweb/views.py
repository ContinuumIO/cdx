from app import app
from flask import request, current_app
import flask
import simplejson
import logging
import urlparse
import blazeclient
import stockreport
import continuumweb.bbmodel as bbmodel
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


@app.route("/bb/<docid>/<typename>", methods=['POST'])
def create(docid, typename):
    log.debug("create, %s, %s", docid, typename)
    modeldata = current_app.ph.deserialize_web(request.data)
    model = bbmodel.ContinuumModel(typename, **modeldata)
    current_app.collections.add(model)
    return app.ph.serialize_web(model.to_json())

@app.route("/bb/<docid>/<typename>/<id>", methods=['PUT'])
def put(docid, typename, id):
    log.debug("put, %s, %s", docid, typename)
    modeldata = current_app.ph.deserialize_web(request.data)
    model = bbmodel.ContinuumModel(typename, **modeldata)
    current_app.collections.add(model)
    return app.ph.serialize_web(model.to_json())

@app.route("/bb/<docid>/", methods=['GET'])
@app.route("/bb/<docid>/<typename>", methods=['GET'])
@app.route("/bb/<docid>/<typename>/<id>", methods=['GET'])
def get(docid, typename=None, id=None):
    if typename is not None and id is not None:
        model = current_app.collections.get(typename, id)
        if docid in model.get('docs'):
            return app.ph.serialize_web(model.to_json())
        else:
            return None
    else:
        models = current_app.collections.get_bulk(docid, typename=typename, id=id)
        if typename is not None:
            return app.ph.serialize_web([x.to_json() for x in models])
        else:
            return app.ph.serialize_web([x.to_broadcast_json() for x in models])
        
@app.route("/bb/<docid>/<typename>/<id>", methods=['DELETE'])
def delete(docid, typename, id):
    model = current_app.collections.get(typename, id)
    if docid in model.get('docs'):
        current_app.collections.delete(typename, id)
    return app.ph.serialize_web(model.to_json())


