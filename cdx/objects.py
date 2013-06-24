import pandas as pd
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
    def populate(self):
        ns = get_ipython().user_ns
        self.data = {}
        for k,v in ns.iteritems():
            if isinstance(v, pd.DataFrame) and not k.startswith("_"):
                summary = v.describe()
                self.data[k] = summary.to_dict()
        self.session.store_obj(self)
        
class CDX(PlotObject):
    namespace = Instance(Namespace, has_ref=True)
    activetable = Instance(Plot, has_ref=True)
    activeplot = Instance(Plot, has_ref=True)
    plotlist = Instance(PlotList, has_ref=True)
    plotcontext = Instance(PlotContext, has_ref=True) # list of to level UI elems
    def plot(self, xname, yname, source):
        plot_source = PandasPlotSource(source=source)
        xdr = DataRange1d(sources=[plot_source.columns(xname)])
        ydr = DataRange1d(sources=[plot_source.columns(yname)])
        circle = Circle(x=xname, y=yname, fill="blue", alpha=0.6, radius=3,
                        line_color="black")
        nonselection_circle = Circle(x="weight", y="mpg", fill="blue",
                                     fill_alpha=0.1, radius=3,
                                     line_color="black")
        glyph_renderer = GlyphRenderer(
            data_source = plot_source,
            xdata_range = xdr,
            ydata_range = ydr,
            glyph = circle,
            nonselection_glyph = nonselection_circle,
            )
        pantool = PanTool(dataranges = [xdr, ydr],
                          dimensions=["width","height"])
        zoomtool = ZoomTool(dataranges=[xdr, ydr],
                            dimensions=("width","height"))
        selecttool = SelectionTool(renderers=[glyph_renderer])
        overlay = BoxSelectionOverlay(tool=selecttool)
        plot = Plot(x_range=xdr, y_range=ydr, data_sources=[],
                    border= 80)
        xaxis = LinearAxis(plot=plot, dimension=0)
        yaxis = LinearAxis(plot=plot, dimension=1)
        xgrid = Rule(plot=plot, dimension=0)
        ygrid = Rule(plot=plot, dimension=1)
        plot.renderers.append(glyph_renderer)
        plot.tools = [pantool, zoomtool, selecttool]
        plot.renderers.append(overlay)
        self.sess.add(plot, glyph_renderer, xaxis, yaxis, xgrid, ygrid, plot_source, xdr, ydr, pantool, zoomtool, selecttool, overlay)
        self.plotlist.children.append(plot)
        self.plotlist._dirty = True
        stored = self.sess.store_all()
        return stored
