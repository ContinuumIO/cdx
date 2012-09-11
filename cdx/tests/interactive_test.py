import cdx.interactive as interactive
clients = interactive.CDXClient(
    'http://localhost:5000/cdx/aedb3711-ee5b-4797-b2c2-42ed9f09d229/')
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
