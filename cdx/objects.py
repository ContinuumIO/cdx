from bokeh.properties import (HasProps, MetaHasProps, 
        Any, Dict, Enum, Float, Instance, Int, List, String,
        Color, Pattern, Percent, Size)
from bokeh.objects import PlotObject
from bokeh.session import PlotContext, PlotList
import pandas

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
    namespace = Instance(Namespace)
    activetable = Instance
    activeplot = Instance
    plotlist = Instance(PlotList)
    plotcontext = Instance(PlotContext) # list of to level UI elems
    
    
    
