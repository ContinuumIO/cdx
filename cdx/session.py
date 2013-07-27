import pandas as pd
from bokeh.session import PlotServerSession, PlotList
from objects import CDX, Namespace
from bokeh.objects import (
    Plot, DataRange1d, LinearAxis, Rule,
    ColumnDataSource, GlyphRenderer, ObjectArrayDataSource,
    PanTool, ZoomTool, SelectionTool, BoxSelectionOverlay,
    GMapPlot
    )
from bokeh.glyphs import Circle
from bokeh.pandasobjects import PandasPlotSource, IPythonRemoteData
import os
import bokeh.plotting  as plotting
class CDXSession(PlotServerSession):
    def __init__(self, username=None, serverloc=None, userapikey="nokey",
                 arrayserver_port=10020):
        self.arrayserver_port = arrayserver_port
        super(CDXSession, self).__init__(username=username,
                                         serverloc=serverloc,
                                         userapikey=userapikey)
        #hack... ?
        plotting._config["session"] = self
        plotting._config["output_url"] = self.root_url
        plotting._config["output_type"] = "server"
        plotting._config["output_file"] = None
        
    def load_doc(self, docid):
        super(CDXSession, self).load_doc(docid)
        cdx = self.load_type('CDX')
        if len(cdx):
            cdx = cdx[0]
        else:
            cdx = CDX()
            self.add(cdx)
            self.store_obj(cdx)
        self.cdx = cdx
        self.plotcontext.children.append(cdx)
        self.plotcontext._dirty = True
        if not cdx.namespace:
            ns = Namespace(name=self.docname)
            self.add(ns)
            cdx.namespace = ns
            self.store_obj(ns)
            self.store_obj(cdx)
        cdx.namespace.name = self.docname
        cdx.namespace.port = self.arrayserver_port
        if not cdx.plotcontext:
            cdx.plotcontext = self.plotcontext
            self.store_obj(cdx)

        if not cdx.plotlist:
            cdx.plotlist = PlotList()
            self.add(cdx.plotlist)
            self.store_objs([cdx, cdx.plotlist])
        #load namespace
        self.cdx.namespace.load()
        self.cdx.namespace.populate(todisk=False)
            
    @property
    def source(self):
        return self.cdx.activetable.source
    
    def reset(self):
        self.cdx.activetable = None
        self.cdx.plotlist.children = []
        self.cdx.plotlist._dirty = True
        self.cdx.namespace.data = {}
        self.cdx.activeplot = None
        self.store_all()
        
    def _get_plotsource(self, varname):
        plot_source = [m for m in self._models.values() \
                       if isinstance(m, PandasPlotSource) and \
                       m.source.varname == varname]
        if len(plot_source) > 0:
            return plot_source[0]
        remote_source = [m for m in self._models.values() \
                       if isinstance(m, IPythonRemoteData) and \
                       m.varname == varname]
        if len(remote_source) > 0:
            remote_source = remote_source[0]
        else:
            remote_source = IPythonRemoteData(host='localhost',
                                              port=self.arrayserver_port,
                                              varname=varname)
            self.add(remote_source)
        plot_source = PandasPlotSource(source=remote_source)
        self.add(plot_source)
        return plot_source
            
    def plot(self, xname, yname, varname, load=True):
        if load:
            self.load_all()
        plot_source = self._get_plotsource(varname)
        title = "%s %s vs %s" % (varname, xname, yname)        
        plot = plotting.scatter(xname, yname, source=plot_source, title=title,
                                tools="pan,zoom,select"
                                )
        self.cdx.plotlist.children.insert(0, plot)
        self.cdx.activeplot = plot
        self.cdx.plotlist._dirty = True
        stored = self.store_all()
        return stored
    
    def map(self, latitude=35.349, longitude=-116.595, zoom=17):
        plot = GMapPlot(
            center_lat=latitude, center_lng=longitude, zoom_level=17,
            data_sources=[],
            canvas_width=600, canvas_height=600, 
            outer_width=600, outer_height=600
            )
        xgrid = Rule(plot=plot, dimension=0)
        ygrid = Rule(plot=plot, dimension=1)
        self.add(plot, xgrid, ygrid)
        self.cdx.plotlist.children.insert(0, plot)
        self.cdx.activeplot = plot
        self.cdx.plotlist._dirty = True
        stored = self.store_all()
        return stored
