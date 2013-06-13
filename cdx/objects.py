from bokeh.properties import (HasProps, MetaHasProps, 
        Any, Dict, Enum, Float, Instance, Int, List, String,
        Color, Pattern, Percent, Size)
from bokeh.objects import PlotObject
from bokeh.session import PlotContext
# plot object is a bad name
class Table(PlotObject):
    pass

class Namespace(PlotObject):
    data = Dict()

class CDX(PlotObject):
    namespace = Instance(Namespace)
    activetable = Instance
    activeplot = Instance
    plotlist = List
    plotcontext = Instance(PlotContext) # list of to level UI elems
    
    
    
