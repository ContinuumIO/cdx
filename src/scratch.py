import continuumweb.plot as plot
import continuumweb.bbmodel as bbmodel
import blaze.server.rpc.protocol as protocol
import numpy as np

ph = protocol.ProtocolHelper()
ctx = bbmodel.ContinuumModels(
    bbmodel.ContinuumModelsStorage(),
    bbmodel.ContinuumModelsClient('test', "http://localhost:5000/bb/", ph))
datasource = plot.make_source(x=np.random.random(10), y = np.random.random(10))
(plotobj, xr, yr,
 datarange1, datarange2,
 xaxis, yaxis,
 xmapper, ymapper,
 scatter) =  plot.scatter(300, 300, datasource, 'x', 'y')

ctx.create_all([datasource, plotobj, xr, yr,
                datarange1, datarange2,
                xaxis, yaxis,
                xmapper, ymapper,
                scatter])
ctx.make_view(plotobj.ref())
