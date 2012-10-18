from cdx import plot
p = plot.PlotClient('24d603e8-1838-4514-a33b-4f02aaa50c9e', 'https://localhost', 'f3ae0299-b3a9-46f3-adfb-8b21285bf446')
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
