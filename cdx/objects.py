import os
import json
import cPickle as pickle

from pandas import DataFrame

from bokeh.properties import (HasProps, MetaHasProps,
        Any, Dict, Enum, Float, Instance, Int, List, String,
        Color, Pattern, Percent, Size)

#loading dependencies
import bokeh.objects
import bokeh.glyphs

from bokeh.objects import PlotObject, Plot
from bokeh.pandasobjects import PlotObject, Plot, IPythonRemoteData
from bokeh.session import PlotContext, PlotList


global store

# plot object is a bad name
class Table(PlotObject):
    pass

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

        self.populate()

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

        data = [ (name, ns[name]) for name in datasets.keys() ]

        with open(self.filename, "w+") as file:
            pickle.dump(data, file, protocol=-1)

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
    activeplot = Instance(Plot, has_ref=True)
    plotlist = Instance(PlotList, has_ref=True)
    plotcontext = Instance(PlotContext, has_ref=True) # list of to level UI elems
