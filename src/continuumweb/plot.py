import bbmodel
import protocol

class ScatterPlot(object):
    def __init__(self, client, plot, data_source, screen_xrange,
                 screen_yrange, data_xrange, data_yrange,
                 xmapper, ymapper, renderer, parent):
        self.plot = plot
        self.data_source = data_source
        self.screen_xrange = screen_xrange
        self.screen_yrange = screen_yrange
        self.data_xrange = data_xrange
        self.data_yrange = data_yrange
        self.xmapper = xmapper
        self.ymapper = ymapper
        self.renderer = renderer
        self.parent = parent

class PlotClient(bbmodel.ContinuumModels):
    def __init__(self, docid, url):
        self.ph = protocol.ProtocolHelper()
        client = bbmodel.ContinuumModelsClient(docid, url, self.ph)
        storage = bbmodel.ContinuumModelsStorage()
        super(PlotClient, self).__init__(storage, client)
        self.fetch()
        interactive_context = self.get_bulk(typename='InteractiveContext')
        self.ic = interactive_context[0]
        
    def make_source(self, **kwargs):
        output = []
        flds = kwargs.keys()
        for idx in range(len(kwargs.values()[0])):
            point = {}
            for f in flds:
                point[f] = kwargs[f][idx]
            output.append(point)
        model = self.create('ObjectArrayDataSource', {'data' : output})
        return model

    def scatter(self, x, y, width=300, height=300,
                data_source=None, container=None):
        """
        Parameters
        ----------
        x : string of fieldname in data_source, or 1d vector
        y : string of fieldname in data_source or 1d_vector
        data_source : optional if x,y are not strings,
            backbonemodel of a data source
        container : bbmodel of container viewmodel

        Returns
        ----------
        (plotmodel, data_source)
        """
        tocreate = []
        if container:
            plot = bbmodel.ContinuumModel('Plot', width=width, height=height,
                                          parent=container.ref())
        else:
            plot = bbmodel.ContinuumModel('Plot', width=width, height=height,
                                          parent=self.ic.ref())
        tocreate.append(plot)
        if data_source is None:
            data_source = self.make_source(x=x, y=y)
            xfield = 'x'
            yfield = 'y'
        else:
            xfield = x
            yfield = y
        xr = bbmodel.ContinuumModel('PlotRange1d', plot=plot.ref(),
                                    attribute='width')
        yr = bbmodel.ContinuumModel('PlotRange1d', plot=plot.ref(),
                                    attribute='height')
        datarange1 = bbmodel.ContinuumModel(
            'DataRange1d',
            sources=[{'ref' : data_source.ref(),
                      'columns' : [xfield]}])
        datarange2 = bbmodel.ContinuumModel(
            'DataRange1d',
            sources=[{'ref' : data_source.ref(),
                      'columns' : [yfield]}])
        xmapper = bbmodel.ContinuumModel(
            'LinearMapper', data_range=datarange1.ref(),
            screen_range=xr.ref())
        ymapper = bbmodel.ContinuumModel(
            'LinearMapper', data_range=datarange2.ref(),
            screen_range=yr.ref())
        scatter = bbmodel.ContinuumModel(
            'ScatterRenderer', data_source=data_source.ref(),
            xfield=xfield, yfield=yfield, xmapper=xmapper.ref(),
            ymapper=ymapper.ref(), parent=plot.ref())
        xaxis = bbmodel.ContinuumModel(
            'D3LinearAxis', orientation='bottom', ticks=3,
            mapper=xmapper.ref(), parent=plot.ref())
        yaxis = bbmodel.ContinuumModel(
            'D3LinearAxis', orientation='left', ticks=3,
            mapper=ymapper.ref(), parent=plot.ref())
        plot.set('renderers', [scatter.ref()])
        plot.set('axes', [xaxis.ref(), yaxis.ref()])
        tocreate.extend([xr, yr, datarange1, datarange2,
                         xaxis, yaxis, xmapper, ymapper, scatter])
        self.create_all(tocreate)
        if container is None:
            self.show(plot)
            container = self.ic
        return ScatterPlot(self, plot, data_source, xr, yr, datarange1, datarange2,
                           xmapper, ymapper, scatter, container)

    
    def show(self, plot):
        children = self.ic.get('children')
        if children is None: children = []
        children.append(plot.ref())
        self.ic.set('children', children)
        self.update(self.ic.typename, self.ic.attributes)
        
if __name__ == "__main__":
    import numpy as np
    client = PlotClient('test', "http://localhost:5000/bb/")
    scatterplot = client.scatter(np.random.random(100), np.random.random(100))
    #client.scatter('x', 'y', data_source=scatterplot.data_source)
    
