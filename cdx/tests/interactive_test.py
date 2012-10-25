from cdxlib import mpl
p = mpl.PlotClient('d6f7f400-06f2-49db-aab9-f7540f04f193', 'https://localhost', 'eb53fc5c-53b5-4e43-a52f-5bbba1bebce4')
p.clearic()
import numpy as np

x = np.arange(100) / 6.0
y = np.sin(x)
z = np.cos(x)
data_source = p.make_source(idx=range(100), x=x, y=y, z=z)
data_source2 = p.make_source(idx=range(100), x2=x, y2=y, z2=z)
p.plot('x', 'y', data_source=data_source)
p.plot('x', 'z', data_source=data_source)
p.clf()
p.plot(x, y)
p.plot(x, z)

# scatterplot1 = p.scatter(
#     x='x', y='y', color='#F00',
#     data_source=data_source, title='paddy_from_py')

# scatterplot1 = p.line(
#     x='x', y='y', 
#     data_source=data_source, lineplot=scatterplot1)

# scatterplot1 = p.scatter(
#     x='x2', y='z2', color='#F00',
#     data_source=data_source2, scatterplot=scatterplot1)

# scatterplot1 = p.line(
#     x='x2', y='z2', 
#     data_source=data_source2, lineplot=scatterplot1)


# scatterplot1 = p.scatter(
#     x='x', y='y', color='#F00',
#     data_source=data_source, title='paddy_from_py')

# scatterplot1 = p.line(
#     x='x', y='y', 
#     data_source=data_source, lineplot=scatterplot1)

# scatterplot1 = p.scatter(
#     x='x2', y='z2', color='#F00',
#     data_source=data_source2, scatterplot=scatterplot1)

# scatterplot1 = p.line(
#     x='x2', y='z2', 
#     data_source=data_source2, lineplot=scatterplot1)
