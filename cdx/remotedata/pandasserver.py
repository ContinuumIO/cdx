import pandas as pd
import numpy as np
from flask import Flask, request, current_app
from bokeh import protocol
import json

import logging

logging.basicConfig(level=logging.INFO, filename="pandasserver.log")
logging.captureWarnings(True)

log = logging.getLogger(__name__)

def make_json(jsonstring, status_code=200, headers={}):
    """like jsonify, except accepts string, so we can do our own custom
    json serialization.  should move this to continuumweb later
    """
    return current_app.response_class(response=jsonstring,
                                      status=status_code,
                                      headers=headers,
                                      mimetype='application/json')

app = Flask(__name__)
app.debug = True
selections = {}
computed_columns = {}

# should memoize this
namespace = None

def computed_column(data, column_spec):
    localvars = dict(**data)
    localvars['pd'] = pd
    localvars['np'] = np
    result = eval(column_spec['code'], localvars)
    data[column_spec['name']] = result

def search(varname, code):
    data = namespace[varname]
    localvars = dict(**data)
    localvars['pd'] = pd
    localvars['np'] = np
    result = eval(code, localvars)
    selections[varname] = np.nonzero(result)[0].tolist()

def get_data(varname, transforms):
    # auto = auto.reindex_axis(list(reversed(auto.columns)), axis=1)
    columns = transforms.get('columns', []) # List[String]
    sort = transforms.get('sort', [])       # List[SortBy(column: String, ascending: Boolean)]
    group = transforms.get('group', [])
    agg = transforms.get('agg', 'mean')
    offset = transforms.get('offset', 0)
    length = transforms.get('length', None)
    filterselected = transforms.get('filterselected', False)
    cc = computed_columns.get(varname, [])
    raw_selected = selections.get(varname, [])
    ns = namespace
    data = ns[varname]
    maxlength = len(data)
    originallength = len(data)
    if columns:
        data = data.reindex_axis(columns, axis='columns')
    data['_counts'] = np.ones(len(data))
    data['_selected'] = np.zeros(len(data))
    data.ix[raw_selected, '_selected'] = 1
    for column_spec in cc:
        computed_column(data, column_spec)
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
    if np.sum(data._selected) > 1 and not groupobj and filterselected:
        # in the non group by case, we filter on selection
        # otherwise we output the # of selected items
        data = data.ix[data._selected==1, :]
    totallength = len(data)
    if length:
        data = data[offset:offset + length]
    else:
        data = data[offset:]
    if groupobj:
        stats = groupobj.sum()
        counts = stats['_counts']
        selected = stats['_selected']
        data['_counts'] = counts
        data['_selected'] = selected
    try:
        del ns[varname]['_counts']
    except KeyError:
        pass
    try:
        del ns[varname]['_selected']
    except KeyError:
        pass
    return groupobj, data, maxlength, totallength

def jsonify(df):
    column_names = df.columns.tolist()
    data = {}
    metadata = {}
    for k in column_names:
        if df[k].dtype.type == np.datetime64:
            metadata[k] = {'date' : True}
            data[k] = df[k].astype('datetime64[ms]').astype('int64').tolist()
        else:
            data[k] = df[k].tolist()
    data['index'] = df.index.tolist()
    column_names.insert(0, "index")
    return dict(data=data, column_names=column_names, metadata=metadata)

@app.route("/array/<varname>/computed")
def set_computed(varname):
    cc = json.loads(request.data)
    computed_columns[varname] = cc
    return make_json(protocol.serialize_json(cc))

import logging
@app.route("/array/<varname>")
def get(varname):
    if request.data:
        transforms = json.loads(request.data)
    else:
        transforms = {}
    groupobj, data, maxlength, totallength = get_data(varname, transforms)
    data = jsonify(data)
    data['maxlength'] = maxlength
    data['totallength'] = totallength
    return make_json(protocol.serialize_json(data))

def compute_selection(varname):
    if request.data:
        transforms = json.loads(request.data)
    else:
        transforms = {}
    groupobj, data, maxlength, totallength = get_data(varname, transforms)
    selected = transforms.get('selected', [])
    if groupobj:
        raw_selected = []
        for rownum in selected:
            raw_selected.extend(groupobj.groups[data.index[rownum]])
    else:
        raw_selected = np.array(selected) + transforms.get('offset', 0)
    return raw_selected

@app.route("/array/<varname>/search", methods=["POST"])
def searchapi(varname):
    code = request.data
    search(varname, code)
    return make_json(protocol.serialize_json(selections[varname]))

@app.route("/array/<varname>/setselect", methods=["POST"])
def set_selection(varname):
    raw_selected = compute_selection(varname)
    selections[varname] = raw_selected
    return make_json(protocol.serialize_json(selections[varname]))

@app.route("/array/<varname>/select", methods=["POST"])
def select(varname):
    raw_selected = compute_selection(varname)
    selections[varname] = np.union1d(raw_selected,
                                     selections.get(varname, [])).tolist()
    return make_json(protocol.serialize_json(selections[varname]))

@app.route("/array/<varname>/deselect", methods=["POST"])
def deselect(varname):
    raw_selected = compute_selection(varname)
    selections[varname] = np.setdiff1d(selections.get(varname, []),
                                       raw_selected).tolist()
    return make_json(protocol.serialize_json(selections[varname]))

def _pivot_table(dataset, rows, cols, values, aggfunc=None):
    from cdx.pivot import pivot_table

    try:
        if not rows and not cols:
            table = pd.DataFrame()
        else:
            table = pivot_table(dataset, rows=rows, cols=cols, values=values, aggfunc=aggfunc)
    except:
        table = pd.DataFrame()

    if isinstance(table, pd.DataFrame):
        if len(rows) == 1:
            _rows = [ [x] for x in table.index.tolist() ]
        else:
            _rows = table.index.tolist()
        if len(cols) == 1:
            _cols = [ [x] for x in table.columns.tolist() ]
        else:
            _cols = table.columns.tolist()
        _values = table.values.tolist()
        _attrs = dataset.columns.tolist()
    elif isinstance(table, pd.Series):
        raise ValueError("series")
    else:
        raise ValueError("???")

    return table, (_attrs, _rows, _cols, _values)

@app.route("/array/<varname>/fields", methods=["GET"])
def fields(varname):
    df = namespace[varname]
    fields = [ dict(name=column, dtype=dtype.name) for (column, dtype) in zip(df.columns, df.dtypes) ]
    return make_json(protocol.serialize_json(fields))

@app.route("/array/<varname>/pivot", methods=["POST"])
def pivot(varname):
    if request.data:
        options = json.loads(request.data)
    else:
        options = {}

    rows = options.get("rows", [])
    columns = options.get("columns", [])
    values = options.get("values", [])
    filters = options.get("filters", [])

    def fields(items):
       return [ item["field"] for item in items ]

    row_fields = fields(rows)
    column_fields = fields(columns)
    value_fields = fields(values)
    filter_fields = fields(filters)

    if len(values) > 0:
        aggfunc = values[0]["aggregate"]
    else:
        aggfunc = len

    _, (_attrs, _rows, _cols, _values) = _pivot_table(namespace[varname], row_fields, column_fields, value_fields, aggfunc)

    result = {
        "attrs": _attrs,
        "rows": _rows,
        "cols": _cols,
        "values": _values,
    }

    return make_json(protocol.serialize_json(result))

@app.route("/test")
def test():
    return "TEST"

def _run(server):
    server.serve_forever()

server = None
def shutdown():
    print 'QUITTING'
    server.shutdown()
    server.socket.close()

def run(port):
    global namespace
    namespace = get_ipython().user_ns

    global server
    if server:
        shutdown()
    import werkzeug.serving
    server = werkzeug.serving.make_server("localhost", port, app=app)
    import signal
    import os
    if hasattr(get_ipython(), 'exit'):
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

