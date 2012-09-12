import cdx.interactive as interactive
clients = interactive.CDXClient(
    'http://localhost:5000/cdx/a34b134a-2e85-4e22-9cd7-a30f1fd91e7b')
import numpy as np

x = np.random.random(100)
y = np.random.random(100)
data_source = clients.p.make_source(idx=range(100), x=x, y=y)
scatterplot1 = clients.p.scatter(
    x='idx', y='x', color='#F00',
    data_source=data_source, title='paddy_from_py')
tableplot1 = clients.p.table(
    x='idx', y='x', color='#F00',
    data_source=data_source, title='paddy_table_py')
