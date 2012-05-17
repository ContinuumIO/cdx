import continuumweb.plot as plot
import continuumweb.bbmodel as bbmodel
import blaze.server.rpc.protocol as protocol
import numpy as np
client = plot.PlotClient('test', "http://localhost:5000/bb/")
try:
    datasource = client.get_bulk('ObjectArrayDataSource')[0]
except:
    datasource = client.make_source(x=np.random.random(10), y = np.random.random(10))

datasource = client.make_source(x=np.arange(10.), y = np.arange(0, -9., -1))
client.scatter(300, 300, datasource, 'x', 'y')
