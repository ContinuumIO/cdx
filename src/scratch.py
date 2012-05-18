import plot
import bbmodel
import protocol
import numpy as np

client = plot.PlotClient('test', "http://yata.in:5000/bb/")
datasource = client.make_source(x=np.random.random(10), y = np.random.random(10))
client.scatter(300, 300, datasource, 'x', 'y')

