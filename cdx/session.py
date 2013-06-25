from bokeh.session import PlotServerSession, PlotList
from objects import CDX, Namespace
from bokeh.objects import (
    Plot, DataRange1d, LinearAxis, Rule,
    ColumnDataSource, GlyphRenderer, ObjectArrayDataSource,
    PanTool, ZoomTool, SelectionTool, BoxSelectionOverlay)
from bokeh.glyphs import Circle
from bokeh.pandasobjects import PandasPlotSource

class CDXSession(PlotServerSession):
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
            ns = Namespace()
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
            
    def reset(self):
        self.cdx.activetable = None
        self.cdx.plotlist.children = []
        self.cdx.plotlist._dirty = True
        self.cdx.namespace.data = {}
        self.store_all()
        
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
        self.add(plot, glyph_renderer, xaxis, yaxis, xgrid, ygrid, plot_source, xdr, ydr, pantool, zoomtool, selecttool, overlay)
        self.cdx.plotlist.children.append(plot)
        self.cdx.plotlist._dirty = True
        stored = self.store_all()
        return stored
