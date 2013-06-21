import pandas as pd
import numpy as np
from flask import Flask, request
from bokeh.server.views import make_json
from bokeh import protocol
import json
#app = Flask('cdx.remotedata.pandasserver')
app = Flask(__name__)
selections = {}

#should memoize this
namespace = None

def get_data(varname, transforms):
    sort = transforms.get('sort', [])
    group = transforms.get('group', [])
    agg = transforms.get('agg', 'mean')
    offset = transforms.get('offset', 0)
    length = transforms.get('length', 100)
    raw_selected = selections.get(varname, [])
    if namespace is None:
        ns = get_ipython().user_ns
    else:
        ns = namespace
    data = ns[varname]
    data['_counts'] = np.ones(len(data))
    data['_selected'] = np.zeros(len(data))
    data.ix[raw_selected, '_selected'] = 1
    if group and agg:
        groupobj = data.groupby(group)
        data = getattr(groupobj, agg)()
    else:
        groupobj = None
    if sort:
        columns = [x['column'] for x in sort]
        ascending = [x['ascending'] for x in sort]
        data = data.sort(
            columns=columns,
            ascending=ascending
            )
    unsliced = data
    if np.sum(data._selected) > 1 and not groupobj:
        # in the non group by case, we filter on selection
        # otherwise we output the # of selected items
        data = data.ix[data._selected==1, :]
    totallength = len(data)
    data = data[offset:offset + length]
    if groupobj:
        stats = groupobj.sum()
        counts = stats['_counts']
        selected = stats['_selected']
        data['_counts'] = counts
        data['_selected'] = selected
    return groupobj, data

def jsonify(df):
    column_names = df.columns.tolist()
    data = {}
    for k in column_names:
        data[k] = df[k].tolist()
    data['_index'] = df.index.tolist()
    return dict(data=data, column_names=column_names)

@app.route("/array/<varname>")
def get(varname):
    if request.data:
        transforms = json.loads(request.data)
    else:
        transforms = {}
    groupobj, data = get_data(varname, transforms)
    return make_json(protocol.serialize_json(jsonify(data)))

def compute_selection(varname):
    if request.data:
        transforms = json.loads(request.data)
    else:
        transforms = {}
    groupobj, data = get_data(varname, transforms)
    selected = transforms.get('selected', [])    
    if groupobj:
        raw_selected = []
        for rownum in selected:
            raw_selected.extend(groupobj.groups[data.index[rownum]])
    else:
        raw_selected = np.array(selected) + transforms.get('offset')
    return raw_selected
    
@app.route("/array/<varname>/setselect", methods=["POST"])
def set_selection(varname):
    raw_selected = compute_selection(varname)
    selections[varname] = raw_selected
    print selections[varname]
    return make_json(json.dumps(selections[varname]))

@app.route("/array/<varname>/select", methods=["POST"])
def select(varname):
    raw_selected = compute_selection(varname)
    selections[varname] = np.union1d(raw_selected,
                                     selections.get(varname, [])).tolist()
    print selections[varname]
    return make_json(json.dumps(selections[varname]))    

@app.route("/array/<varname>/deselect", methods=["POST"])
def deselect(varname):
    raw_selected = compute_selection(varname)
    selections[varname] = np.setdiff1d(selections.get(varname, []),
                                       raw_selected).tolist()
    print selections[varname]
    return make_json(json.dumps(selections[varname]))    


@app.route("/test")
def test():
    return "TEST"

def _run(server):
    server.serve_forever()
    
def run():
    import werkzeug.serving
    server = werkzeug.serving.make_server("localhost", 10020, app=app)
    import signal
    import os
    def shutdown():
        print 'QUITTING'
        server.shutdown_signal = True
        # python 2.7
        server._BaseServer__shutdown_request = True
        # python 2.6
        server._BaseServer__serving = False
        
    exit_func = get_ipython().exit
    def new_exit():
        shutdown()
        exit_func()
    get_ipython().exit = new_exit
    import threading
    t = threading.Thread(target=_run, args=(server,))
    t.start()

def run_test():
    import werkzeug.serving
    data = pd.read_csv("auto-mpg.csv")
    global namespace
    namespace = {}
    namespace['data'] = data
    app.debug = True
    @werkzeug.serving.run_with_reloader
    def helper():
        server = werkzeug.serving.make_server("localhost", 10020, app=app)
        _run(server)
    
if __name__ == "__main__":
    run_test()
    
