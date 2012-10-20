from cdx import plot
p = plot.PlotClient('d6f7f400-06f2-49db-aab9-f7540f04f193', 'https://localhost', 'eb53fc5c-53b5-4e43-a52f-5bbba1bebce4')
import numpy as np

x = np.random.random(100)
y = np.random.random(100)
data_source = p.make_source(idx=range(100), x=x, y=y)
scatterplot1 = p.scatter(
    x='idx', y='x', color='#F00',
    data_source=data_source, title='paddy_from_py')
tableplot1 = p.table(
    x='idx', y='x', color='#F00',
    data_source=data_source, title='paddy_table_py')
