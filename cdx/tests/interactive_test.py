from cdx import plot
p = plot.PlotClient('d6f7f400-06f2-49db-aab9-f7540f04f193', 'https://localhost', 'eb53fc5c-53b5-4e43-a52f-5bbba1bebce4')
import numpy as np

x = np.arange(100) / 6.0
y = np.sin(x)
z = np.cos(x)
data_source = p.make_source(idx=range(100), x=x, y=y, z=z)
scatterplot1 = p.scatter(
    x='x', y='y', color='#F00',
    data_source=data_source, title='paddy_from_py')

scatterplot1 = p.line(
    x='x', y='y', 
    data_source=data_source, lineplot=scatterplot1)

scatterplot2 = p.scatter(
    x='x', y='z', color='#F00',
    data_source=data_source, title='paddy_from_py2')

scatterplot2 = p.line(
    x='x', y='z', 
    data_source=data_source, lineplot=scatterplot2)

tableplot1 = p.table(
    x='idx', y='x', color='#F00',
    data_source=data_source, title='paddy_table_py')
