import pandas as pd
import os
import json
import cPickle as pickle

from bokeh.properties import (HasProps, MetaHasProps, 
        Any, Dict, Enum, Float, Instance, Int, List, String,
        Color, Pattern, Percent, Size)

#loading dependencies
import bokeh.objects
import bokeh.glyphs

from bokeh.objects import PlotObject, Plot
from bokeh.session import PlotContext, PlotList



# plot object is a bad name
class Table(PlotObject):
    pass

class Namespace(PlotObject):
    data = Dict()
    name = String()
    
    def populate(self, todisk=True):
        ns = get_ipython().user_ns
        self.data = {}
        for k,v in ns.iteritems():
            if isinstance(v, pd.DataFrame) and not k.startswith("_"):
                summary = v.describe()
                self.data[k] = summary.to_dict()
        self.session.store_obj(self)
        if not todisk:
            return
        fname = self.filename
        store = pd.HDFStore(fname)
        for k,v in ns.iteritems():
            if k in self.data:
                store[k] = v
        store.close()
        
    @property
    def filename(self):
        return self.name + ".hdf5"

    def load(self):
        ns = get_ipython().user_ns
        if os.path.exists(self.filename):
            store = pd.HDFStore(self.filename)
            for k,v in store.iteritems():
                k = k.strip("/")
                ns[k] = store.select(k)

class CDX(PlotObject):
    namespace = Instance(Namespace, has_ref=True)
    activetable = Instance(Plot, has_ref=True)
    activeplot = Instance(Plot, has_ref=True)
    plotlist = Instance(PlotList, has_ref=True)
    plotcontext = Instance(PlotContext, has_ref=True) # list of to level UI elems
