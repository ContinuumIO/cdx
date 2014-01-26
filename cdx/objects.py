import os
import json
import cPickle as pickle

from pandas import DataFrame

from bokeh.properties import (HasProps, MetaHasProps,
        Any, Dict, Enum, Float, Instance, Int, List, String,
        Color, Percent, Size)

#loading dependencies
import bokeh.objects
import bokeh.glyphs

from bokeh.objects import PlotObject, Plot
from bokeh.pandasobjects import PlotObject, Plot, IPythonRemoteData
from bokeh.session import PlotContext, PlotList

class Pivot(PlotObject):
    source = Instance(has_ref=True)
    fields = List()
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
        self.on_change('manual_update', self, 'get_data')

        if not self.fields:
            self.fields = self.source.fields()

    def get_data(self, obj=None, attrname=None, old=None, new=None):
        print "get_data()"

class Namespace(PlotObject):
    data = Dict()
    name = String()
    arrayserver_port = Int()

    def __str__(self):
        return "Namespace(name=%r, datasets=%s)" % (self.name, sorted(self.data.keys()))

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

        if datasets == self.data:
            return

        self.data = datasets
        self.session.store_obj(self)

        if not to_disk:
            return

        data = dict([ (name, ns[name]) for name in datasets.keys() ])

        with open(self.filename, "w+") as file:
            pickle.dump(data, file, protocol=-1)

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

class CDX(PlotObject):
    namespace = Instance(Namespace, has_ref=True)
    activetable = Instance(Plot, has_ref=True)
    activepivot = Instance(Plot, has_ref=True)
    activeplot = Instance(Plot, has_ref=True)
    plotlist = Instance(PlotList, has_ref=True)
    plotcontext = Instance(PlotContext, has_ref=True) # list of to level UI elems
