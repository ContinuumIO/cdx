import pandas as pd
from bokeh.session import PlotServerSession
from objects import CDX, Namespace, RemoteDataSource, PlotList
from bokeh.objects import (Range1d, Plot, Grid, PanTool, WheelZoomTool,
    BoxSelectTool, BoxSelectionOverlay, GMapPlot, DataSlider)
from bokeh.glyphs import Circle
from bokeh.pandasobjects import PandasPlotSource
import os
import bokeh.plotting  as plotting

def init_session(title, cdx_addr="http://localhost:5041", arrayserver_port=10020):
    import cdx.remotedata.pandasserver as pds
    pds.run(arrayserver_port)
    sess = CDXSession(serverloc=cdx_addr, arrayserver_port=arrayserver_port)
    get_ipython().register_post_execute(lambda: sess.cdx.namespace.populate())
    sess.use_doc(title)
    return sess

class CDXSession(PlotServerSession):
    def __init__(self, username=None, serverloc=None, userapikey="nokey", arrayserver_port=10020):
        self.arrayserver_port = arrayserver_port
        super(CDXSession, self).__init__(username=username,
                                         serverloc=serverloc,
                                         userapikey=userapikey)
        #hack... ?
        plotting._config["session"] = self
        plotting._config["output_url"] = self.root_url
        plotting._config["output_type"] = "server"
        plotting._config["output_file"] = None
        plotting.hold(False)

    def figure(self):
        plotting.figure()

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

        if cdx.namespace:
            cdx.namespace.name = self.docname
        else:
            ns = Namespace(name=self.docname)
            self.add(ns)
            cdx.namespace = ns
            self.store_obj(ns)
            self.store_obj(cdx)

        if not cdx.plotcontext:
            cdx.plotcontext = self.plotcontext
            self.store_obj(cdx)

        if not cdx.plotlist:
            cdx.plotlist = PlotList()
            self.add(cdx.plotlist)
            self.store_objs([cdx, cdx.plotlist])

        self.cdx.namespace.load()
        self.cdx.namespace.populate(to_disk=False)

    def reset(self):
        self.cdx.namespace.datasets = {}
        self.cdx.plotlist.children = []
        self.cdx.plotlist._dirty = True
        self.cdx.activeplot = None
        self.store_all()

    def _get_plotsource(self, varname):
        plot_source = [m for m in self._models.values() \
                       if isinstance(m, PandasPlotSource) and \
                       m.source.varname == varname]
        if len(plot_source) > 0:
            return plot_source[0]
        remote_source = [m for m in self._models.values() \
                       if isinstance(m, RemoteDataSource) and \
                       m.varname == varname]
        if len(remote_source) > 0:
            remote_source = remote_source[0]
        else:
            remote_source = RemoteDataSource(host='localhost',
                                             port=self.arrayserver_port,
                                             varname=varname)
            self.add(remote_source)
        plot_source = PandasPlotSource(source=remote_source)
        self.add(plot_source)
        return plot_source

    def plot(self, xname, yname, varname, type="scatter", load=True, plot=None,
             alpha=1.0, nonselection_alpha=0.1, slider=None,
             **kwargs):
        if load:
            self.load_all()
        plot_source = self._get_plotsource(varname)
        title = "%s %s vs %s" % (varname, xname, yname)
        kwargs['fill_alpha'] = alpha
        kwargs['line_alpha'] = alpha
        kwargs['nonselection_alpha'] = nonselection_alpha
        if 'tools' not in kwargs:
            kwargs['tools'] = 'pan,wheel_zoom,select'
        if type == "scatter":
            plotfunc = plotting.scatter
        elif type == "line":
            plotfunc = plotting.line
        else:
            raise RuntimeError("Unknown plot function type")
        plot = plotfunc(xname, yname, source=plot_source, title=title,
                        plot=plot, **kwargs)
        if slider:
            slider = DataSlider(plot=plot, data_source=plot_source,
                                field=slider)
            self.add(slider)
            plot.tools.append(slider)
            plot._dirty = True
        if plot not in self.cdx.plotlist.children:
            self.cdx.plotlist.children.insert(0, plot)
        self.cdx.activeplot = plot
        self.cdx.plotlist._dirty = True
        self.plotcontext.children = [self.cdx]
        self.plotcontext._dirty = True
        stored = self.store_all()
        return stored

    def map(self, latitude=35.349, longitude=-116.595, zoom=17, load=True,
            title = "Map"):
        if load:
            self.load_all()
        x_range = Range1d()
        y_range = Range1d()
        plot = GMapPlot(
            x_range=x_range, y_range=y_range,
            center_lat=latitude, center_lng=longitude, zoom_level=zoom,
            data_sources=[],
            canvas_width=600, canvas_height=600,
            outer_width=600, outer_height=600,
            title = title
            )

        select_tool = BoxSelectTool()
        overlay = BoxSelectionOverlay(tool=select_tool)
        plot.renderers.append(overlay)
        plot.tools.append(select_tool)

        xgrid = Grid(plot=plot, dimension=0)
        ygrid = Grid(plot=plot, dimension=1)
        pantool = PanTool(plot=plot)
        zoomtool = ZoomTool(plot=plot)
        plot.tools.extend([pantool, zoomtool])
        self.add(plot, xgrid, ygrid, pantool, zoomtool, x_range, y_range,
                 select_tool, overlay)
        self.cdx.plotlist.children.insert(0, plot)
        self.cdx.activeplot = plot
        self.cdx.plotlist._dirty = True
        stored = self.store_all()
        # print stored
        return stored
