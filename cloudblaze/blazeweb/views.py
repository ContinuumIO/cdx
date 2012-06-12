from app import app
from flask import render_template, request, current_app, send_from_directory, make_response
import flask
import os
import simplejson
import logging
import uuid
import urlparse
import blazeclient
import cloudblaze.continuumweb.bbmodel as bbmodel
import wsmanager

log = logging.getLogger(__name__)

#main pages
@app.route('/')
def index():
	return render_template('index.html') 

@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/x-icon')
	
@app.route('/pageRender/<filename>')
def pageRender(filename):
	app.logger.debug('pageRender filename=[%s]',filename)
    # Note the corresponding html file must be in the templates folder.
	return render_template(filename + '.html') 

#http api for blaze server
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

#dummy pages for browsing hdf5 data sets in blaze
@app.route("/dataview/", methods=['GET'])
@app.route("/dataview/<path:datapath>", methods=['GET'])
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
    
#web socket subscriber
@app.route('/sub')
def sub():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        wsmanager.run_socket(
            ws, current_app.wsmanager,
            lambda auth, topic : True, current_app.ph)
    return

#backbone model apis
@app.route("/bb/<docid>/bulkupsert", methods=['POST'])
def bulk_upsert(docid):
    data = current_app.ph.deserialize_web(request.data)
    models = [bbmodel.ContinuumModel(x['type'], **x['attributes']) \
              for x in data]
    for m in models:
        current_app.collections.add(m)
    docs = set()
    for m in models:
        docs.update(m.get('docs'))
    clientid = request.headers.get('Continuum-Clientid', None)    
    for doc in docs:
        relevant_models = [x for x in models if doc in x.get('docs')]
        current_app.wsmanager.send(doc, app.ph.serialize_web(
            {'msgtype' : 'modelpush',
             'modelspecs' : [x.to_broadcast_json() for x in relevant_models]}),
            exclude={clientid})
    return app.ph.serialize_web(
        {'msgtype' : 'modelpush',
         'modelspecs' : [x.to_broadcast_json() for x in relevant_models]})
@app.route("/bb/<docid>/<typename>", methods=['POST'])
def create(docid, typename):
    log.debug("create, %s, %s", docid, typename)
    modeldata = current_app.ph.deserialize_web(request.data)
    model = bbmodel.ContinuumModel(typename, **modeldata)
    current_app.collections.add(model)
    clientid=request.headers.get('Continuum-Clientid', None)        
    for doc in model.get('docs'):
        current_app.wsmanager.send(doc, app.ph.serialize_web(
            {'msgtype' : 'modelpush',
             'modelspecs' : [model.to_broadcast_json()]}),
            exclude={clientid})
    return app.ph.serialize_web(model.to_json())

@app.route("/bb/<docid>/<typename>/<id>", methods=['PUT'])
def put(docid, typename, id):
    log.debug("put, %s, %s", docid, typename)
    modeldata = current_app.ph.deserialize_web(request.data)
    model = bbmodel.ContinuumModel(typename, **modeldata)
    current_app.collections.add(model)
    clientid=request.headers.get('Continuum-Clientid', None)
    for doc in model.get('docs'):
        current_app.wsmanager.send(doc, app.ph.serialize_web(
            {'msgtype' : 'modelpush',
             'modelspecs' : [model.to_broadcast_json()]}),
                                   exclude={clientid})
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
    log.debug("DELETE, %s, %s", docid, typename)
    clientid = request.headers.get('Continuum-Clientid', None)
    if docid in model.get('docs'):
        current_app.collections.delete(typename, id)
        for doc in model.get('docs'):
            current_app.wsmanager.send(doc, app.ph.serialize_web(
                {'msgtype' : 'modeldel',
                 'modelspecs' : [model.to_broadcast_json()]}),
                                       exclude={clientid})
        return app.ph.serialize_web(model.to_json())
    else:
        return "INVALID"

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
