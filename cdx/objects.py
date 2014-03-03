import os
import json
import cPickle as pickle

import requests

from pandas import DataFrame

from bokeh.properties import (HasProps, MetaHasProps,
        Any, Dict, Enum, Float, Instance, Int, Bool, List, String,
        Color, Percent, Size)

#loading dependencies
import bokeh.objects
import bokeh.glyphs

from bokeh.objects import PlotObject, PlotContext, Plot, PlotList
from bokeh import protocol

class RemoteDataSource(PlotObject):
    host = String("localhost")
    port = Int(10020)
    varname = String()
    computed_columns = List()
    metadata = Dict()

    #hack... we're just using this field right now to trigger events
    selected = Int(0)
    data = Int(0)

    # from IPython.kernel import KernelManager
    # kernel = KernelManager(connection_file="kernel-1.json")
    # kernel.load_connection_file()
    # client = kernel.client()
    # client.start_channels()
    # client.shell_channel.execute("x = 1", store_history=False)

    def _url(self, func=None):
        remotedata = self
        func = "/" + func if func is not None else ""
        url = "http://%s:%s/array/%s%s" % \
            (remotedata.host, remotedata.port, remotedata.varname, func)
        return url

    def _is_ok(self, response):
        response.raise_for_status()

    def _trigger_events(self):
        self.selected = self.selected + 1

    def setselect(self, select, transform):
        data = transform
        data['selected'] = select
        json = protocol.serialize_json(data)
        requests.post(self._url("setselect"), data=json)
        self._trigger_events()

    def search(self, search):
        requests.post(self._url("search"), data=search)
        self._trigger_events()

    def select(self, select, transform):
        data = transform
        data['selected'] = select
        json = protocol.serialize_json(data)
        requests.post(self._url("select"), data=json)
        self._trigger_events()

    def deselect(self, deselect, transform):
        data = transform
        data['selected'] = deselect
        requests.post(self._url("selected"), data=protocol.serialize_json(data))
        self._trigger_events()

    def pivot(self, transform):
        json = protocol.serialize_json(transform)
        response = requests.post(self._url("pivot"), data=json)
        self._is_ok(response)
        data = response.json()
        self._trigger_events()
        return data

    def fields(self):
        json = protocol.serialize_json({})
        response = requests.get(self._url("fields"), data=json)
        self._is_ok(response)
        data = response.json()
        self._trigger_events()
        return data

    def get_data(self, transform):
        json = protocol.serialize_json(transform)
        response = requests.get(self._url(), data=json)
        self._is_ok(response)
        data = response.json()
        self.metadata = data.pop('metadata', {})
        return data

    def set_computed_columns(self, computed_columns):
        json = protocol.serialize_json(computed_columns)
        response = requests.get(self._url("computed"), data=json)
        self._is_ok(response)
        data = response.json()
        self.computed_columns = computed_columns
        self.data += 1
        return data

class DataTable(PlotObject):
    source = Instance(has_ref=True)
    sort = List()
    group = List()
    offset = Int(default=0)
    length = Int(default=100)
    maxlength = Int()
    totallength = Int()
    tabledata = Dict()
    filterselected = Bool(default=False)

    def setup_events(self):
        self.on_change('sort', self, 'get_data')
        self.on_change('group', self, 'get_data')
        self.on_change('length', self, 'get_data')
        self.on_change('offset', self, 'get_data')
        self.on_change('filterselected', self, 'get_data')
        self.source.on_change('selected', self, 'get_data')
        self.source.on_change('data', self, 'get_data')
        self.source.on_change('computed_columns', self, 'get_data')
        if not self.tabledata:
            self.get_data()

    def transform(self):
        return dict(sort=self.sort,
                    group=self.group,
                    offset=self.offset,
                    length=self.length,
                    filterselected=self.filterselected,
                    )

    def setselect(self, select):
        self.source.setselect(select, self.transform())
        self.get_data()

    def select(self, select):
        self.source.select(select, self.transform())
        self.get_data()

    def deselect(self, deselect):
        self.source.deselect(deselect, self.transform())
        self.get_data()

    def get_data(self, obj=None, attrname=None, old=None, new=None):
        data = self.source.get_data(self.transform())
        self.maxlength = data.pop('maxlength')
        self.totallength = data.pop('totallength')
        self.tabledata = data

class PivotTable(PlotObject):
    title = String("Pivot Table")
    description = String("")
    source = Instance(has_ref=True)
    data = Dict()
    fields = List() # List[{name: String, dtype: String}]
    rows = List()
    columns = List()
    values = List()
    filters = List()
    manual_update = Bool(True)

    def setup_events(self):
        self.on_change('rows', self, 'get_data')
        self.on_change('columns', self, 'get_data')
        self.on_change('values', self, 'get_data')
        self.on_change('filters', self, 'get_data')

        if not self.fields:
            self.fields = self.source.fields()

        if not self.data:
            self.get_data()

    def get_data(self, obj=None, attrname=None, old=None, new=None):
        self.data = self.source.pivot(dict(
            rows=self.rows,
            columns=self.columns,
            values=self.values,
            filters=self.filters,
        ))

class Namespace(PlotObject):
    datasets = Dict()
    name = String()

    def __str__(self):
        return "Namespace(name=%r, datasets=%s)" % (self.name, sorted(self.datasets.keys()))

    __repr__ = __str__

    def _namespace(self):
        return get_ipython().user_ns

    def statsmodels(self):
        """Populate namespace with statsmodels' datasets. """
        from statsmodels import datasets

        ns = self._namespace()

        for name, dataset in datasets.__dict__.iteritems():
            if hasattr(dataset, "load_pandas"):
                ns[name] = dataset.load_pandas().data

    def populate(self, to_disk=True):
        """Scan global namespace for pandas' datasets. """
        ns = self._namespace()
        datasets = {}

        for name, dataset in ns.iteritems():
            if isinstance(dataset, DataFrame) and not name.startswith("_"):
                datasets[name] = list(dataset.columns)

        if datasets == self.datasets:
            return

        self.datasets = datasets
        self.session.store_obj(self)

        if not to_disk:
            return

        to_write = dict([ (name, ns[name]) for name in datasets.keys() ])

        with open(self.filename, "w+") as file:
            pickle.dump(to_write, file, protocol=-1)

    def clean(self):
        """Remove all pandas' datasets from global namespace. """
        ns = self._namespace()

        for name, dataset in dict(ns).iteritems():
            if isinstance(dataset, DataFrame) and not name.startswith("_"):
                del ns[name]

    @property
    def filename(self):
        return self.name + ".pickle"

    def load(self):
        ns = self._namespace()
        if os.path.exists(self.filename):
            fname = self.filename
            with open(fname) as f:
                data = pickle.load(f)
            for k,v in data.iteritems():
                ns[k] = v

class Workspace(PlotObject):
    varname = String()
    data_table = Instance(DataTable, has_ref=True)
    pivot_tables = List(Instance(PivotTable, has_ref=True), has_ref=True)
    plots = List(Instance(Plot, has_ref=True), has_ref=True)
    plot_context = Instance(PlotContext, has_ref=True)
    active_tab = Int(0)

class CDX(PlotObject):
    namespace = Instance(Namespace, has_ref=True)
    workspaces = List(Instance(Workspace, has_ref=True), has_ref=True)
    active_workspace = Instance(Workspace, has_ref=True)

    activeplot = Instance(Plot, has_ref=True)
    plotlist = Instance(PlotList, has_ref=True)
    plotcontext = Instance(PlotContext, has_ref=True) # list of to level UI elems
