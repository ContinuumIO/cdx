
from numpy import pi, arange, sin, cos
import numpy as np
import os.path

from bokeh.objects import (
    Plot, DataRange1d, LinearAxis, Rule,
    ColumnDataSource, GlyphRenderer, ObjectArrayDataSource,
    PanTool, ZoomTool)
from bokeh.glyphs import Circle
from bokeh import session

x = arange(-2*pi, 2*pi, 0.1)
y = sin(x)
z = cos(x)
widths = np.ones_like(x) * 0.02
heights = np.ones_like(x) * 0.2


source = ColumnDataSource(data=dict(x=x,y=y,z=z,widths=widths,
            heights=heights))
#source = ObjectArrayDataSource(
#    data = [
#        {'x' : 1, 'y' : 5, 'z':3},
#        {'x' : 2, 'y' : 4, 'z':3, 'radius':10},
#        {'x' : 3, 'y' : 3, 'z':3, 'fill':"blue"},
#        {'x' : 4, 'y' : 2, 'z':3},
#        {'x' : 5, 'y' : 1, 'z':3},
#        ])

xdr = DataRange1d(sources=[source.columns("x")])
ydr = DataRange1d(sources=[source.columns("y")])

circle = Circle(x="x", y="y", fill="red", radius=5, line_color="black")

glyph_renderer = GlyphRenderer(
        data_source = source,
        xdata_range = xdr,
        ydata_range = ydr,
        glyph = circle,
        )


pantool = PanTool(dataranges = [xdr, ydr], dimensions=["width","height"])
zoomtool = ZoomTool(dataranges=[xdr,ydr], dimensions=("width","height"))

plot = Plot(x_range=xdr, y_range=ydr, data_sources=[source],
        border= 80)
xaxis = LinearAxis(plot=plot, dimension=0)
yaxis = LinearAxis(plot=plot, dimension=1)
xgrid = Rule(plot=plot, dimension=0)
ygrid = Rule(plot=plot, dimension=1)

plot.renderers.append(glyph_renderer)
plot.tools = [pantool,zoomtool]

sess = session.PlotServerSession(username="defaultuser",
        serverloc="http://localhost:5006", userapikey="nokey")
sess.use_doc("glyph2")
sess.add(plot, glyph_renderer, xaxis, yaxis, xgrid, ygrid, source, xdr, ydr, pantool, zoomtool)
sess.plotcontext.children.append(plot)
sess.plotcontext._dirty = True
# not so nice.. but set the model doens't know
# that we appended to children
sess.store_all()


