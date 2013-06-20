import pandas
import json

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
    def add(self, obj, name=None):
        if not isinstance(obj, pandas.DataFrame):
            raise Exception, "only supported for dataframes"
        if name is None:
            try:
                ns = get_ipython().user_ns
                for k,v in ns.iteritems():
                    if obj is v:
                        name = k
                        break
            except NameError as e:
                raise Exception, "need to pass name if not in ipython"
                
        summary = obj.describe()
        self.data[name] = summary.to_dict()
        self.session.store_obj(self)
        
class CDX(PlotObject):
    namespace = Instance(Namespace, has_ref=True)
    activetable = Instance(Plot, has_ref=True)
    activeplot = Instance(Plot, has_ref=True)
    plotlist = Instance(PlotList, has_ref=True)
    plotcontext = Instance(PlotContext, has_ref=True) # list of to level UI elems
