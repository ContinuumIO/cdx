
import os.path
import numpy as np

from bokeh.objects import (
    Plot, Range1d, LinearAxis, Rule,
    GlyphRenderer, ColumnDataSource,
    PanTool, ZoomTool)
from bokeh.glyphs import *
from bokeh import session

x = np.arange(1,6)
y = np.arange(5, 0, -1)

source = ColumnDataSource(data=dict(x=x,y=y))

xdr = Range1d(start=0, end=10)
ydr = Range1d(start=0, end=10)

arc = Arc(x="x", y="y", radius=0.4, start_angle=0.8, end_angle=3.8)

def make_plot(name, glyph):
    glyph_renderer = GlyphRenderer(
        data_source = source,
        xdata_range = xdr,
        ydata_range = ydr,
        glyph = glyph,
    )

    pantool = PanTool(dataranges = [xdr, ydr], dimensions=["width","height"])
    zoomtool = ZoomTool(dataranges=[xdr,ydr], dimensions=("width","height"))

    plot = Plot(x_range=xdr, y_range=ydr, data_sources=[source], border=80)
    xaxis = LinearAxis(plot=plot, dimension=0)
    yaxis = LinearAxis(plot=plot, dimension=1)
    xgrid = Rule(plot=plot, dimension=0)
    ygrid = Rule(plot=plot, dimension=1)

    plot.renderers.append(glyph_renderer)
    plot.tools = [pantool,zoomtool]

    sess = session.PlotServerSession(
        username="defaultuser",
        serverloc="http://localhost:5006",
        userapikey="nokey"
    )
    sess.add(plot, glyph_renderer, xaxis, yaxis, xgrid, ygrid, source, xdr, ydr, pantool, zoomtool)
    sess.use_doc(name)
    sess.plotcontext.children.append(plot)
    sess.plotcontext._dirty = True
    sess.store_all()

make_plot('annular_wedge', AnnularWedge(x="x", y="y", inner_radius=0.2, outer_radius=0.5, start_angle=0.8, end_angle=3.8))
make_plot('annulus', Annulus(x="x", y="y", inner_radius=0.2, outer_radius=0.5))
make_plot('arc', Arc(x="x", y="y", radius=0.4, start_angle=0.8, end_angle=3.8))
make_plot('circle', Circle(x="x", y="y", radius=5))
make_plot('oval', Oval(x="x", y="y", width=0.5, height=0.8, angle=-0.6))
make_plot('ray', Ray(x="x", y="y", length=25, angle=0.6))
make_plot('rect', Rect(x="x", y="y", width=0.5, height=0.8, angle=-0.6))
make_plot('text', Text(x="x", y="y", text="foo", angle=0.6))
make_plot('wedge', Wedge(x="x", y="y", radius=0.5, start_angle=0.9, end_angle=3.2))





