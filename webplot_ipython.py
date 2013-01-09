from cdxlib import mpl
import numpy as np
import datetime
import time
p = mpl.PlotClient()
x = np.arange(100) / 6.0
y = np.sin(x)
z = np.cos(x)
data_source = p.make_source(idx=range(100), x=x, y=y, z=z)
plot = p.plot('x', 'y', 'orange', data_source=data_source)
html = plot.notebook()
plot.htmldump("foo2.html")



