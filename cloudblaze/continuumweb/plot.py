import bbmodel
import protocol

class ScatterPlot(object):
    def __init__(self, client, plot, data_source, screen_xrange,
                 screen_yrange, data_xrange, data_yrange,
                 xmapper, ymapper, renderer,
                 pantool, zoomtool, selectiontool, selectionoverlay,
                 parent):
        self.plot = plot
        self.data_source = data_source
        self.screen_xrange = screen_xrange
        self.screen_yrange = screen_yrange
        self.data_xrange = data_xrange
        self.data_yrange = data_yrange
        self.xmapper = xmapper
        self.ymapper = ymapper
        self.renderer = renderer
        self.pantool = pantool
        self.zoomtool = zoomtool
        self.selectiontool = selectiontool
        self.selectionoverlay = selectionoverlay
        self.parent = parent

class LinePlot(object):
    def __init__(self, client, plot, data_source, screen_xrange,
                 screen_yrange, data_xrange, data_yrange,
                 xmapper, ymapper, renderer, pantool, zoomtool, parent):
        self.plot = plot
        self.data_source = data_source
        self.screen_xrange = screen_xrange
        self.screen_yrange = screen_yrange
        self.data_xrange = data_xrange
        self.data_yrange = data_yrange
        self.xmapper = xmapper
        self.ymapper = ymapper
        self.renderer = renderer
        self.pantool = pantool
        self.zoomtool = zoomtool
        self.parent = parent

class PlotClient(bbmodel.ContinuumModelsClient):
    def __init__(self, docid, url):
        self.ph = protocol.ProtocolHelper()
        super(PlotClient, self).__init__(docid, url, self.ph)
        interactive_context = self.fetch(typename='CDXPlotContext')
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

    def scatter(self, x, y, width=300, height=300, color="#000",
                data_source=None, container=None, scatterplot=None):
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
        if scatterplot is None:
            return self._newscatter(x, y, width=width, height=height, color=color,
                                    data_source=data_source, container=container)
        else:
            return self._addscatter(scatterplot, x, y, color=color,
                                    data_source=data_source)

    def _addscatter(self, scatterplot, x, y, color="#000", data_source=None):
        if data_source is None:
            data_source = self.make_source(x=x, y=y)
            xfield, yfield = 'x', 'y'
        else:
            xfield, yfield = x, y
        self._add_source_to_range(data_source, [xfield], scatterplot.data_xrange)
        self.update(scatterplot.data_xrange.typename, scatterplot.data_xrange.attributes)
        self._add_source_to_range(data_source, [yfield], scatterplot.data_yrange)
        self.update(scatterplot.data_yrange.typename, scatterplot.data_yrange.attributes)
        scatter = bbmodel.ContinuumModel(
            'ScatterRenderer', foreground_color=color, data_source=data_source.ref(),
            xfield=xfield, yfield=yfield, xmapper=scatterplot.xmapper.ref(),
            ymapper=scatterplot.ymapper.ref(), parent=scatterplot.plot.ref())
        self.create(scatter.typename, scatter.attributes)

        scatterplot.selectiontool.get('renderers').append(scatter.ref())
        self.update(scatterplot.selectiontool.typename,
                    scatterplot.selectiontool.attributes)
        scatterplot.selectionoverlay.get('renderers').append(scatter.ref())
        self.update(scatterplot.selectionoverlay.typename,
                    scatterplot.selectionoverlay.attributes)
        scatterplot.plot.get('renderers').append(scatter.ref())
        self.update(scatterplot.plot.typename, scatterplot.plot.attributes)
        return scatterplot

    def _newscatter(self, x, y, width=300, height=300, color="#000",
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
            xr = bbmodel.ContinuumModel('Range1d', start=0, end=width)
            yr = bbmodel.ContinuumModel('Range1d', start=0, end=height)
            plot = bbmodel.ContinuumModel('Plot', width=width, height=height,
                                          xrange=xr.ref(), yrange=yr.ref(),
                                          parent=container.ref())
        else:
            xr = bbmodel.ContinuumModel('Range1d', start=0, end=width)
            yr = bbmodel.ContinuumModel('Range1d', start=0, end=height)
            plot = bbmodel.ContinuumModel('Plot', width=width, height=height,
                                          xrange=xr.ref(), yrange=yr.ref(),
                                          parent=self.ic.ref())
        tocreate.append(plot)
        if data_source is None:
            data_source = self.make_source(x=x, y=y)
            xfield = 'x'
            yfield = 'y'
        else:
            xfield = x
            yfield = y
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
        pantool = bbmodel.ContinuumModel(
            'PanTool',
            xmappers=[xmapper.ref()],
            ymappers=[ymapper.ref()])
        zoomtool = bbmodel.ContinuumModel(
            'ZoomTool',
            xmappers=[xmapper.ref()],
            ymappers=[ymapper.ref()])
        scatter = bbmodel.ContinuumModel(
            'ScatterRenderer', foreground_color=color, data_source=data_source.ref(),
            xfield=xfield, yfield=yfield, xmapper=xmapper.ref(),
            ymapper=ymapper.ref(), parent=plot.ref())
        selecttool = bbmodel.ContinuumModel(
            'SelectionTool',
            renderers=[scatter.ref()])
        selectoverlay = bbmodel.ContinuumModel(
            'ScatterSelectionOverlay',
            renderers=[scatter.ref()])
        xaxis = bbmodel.ContinuumModel(
            'D3LinearAxis', orientation='bottom', ticks=3,
            mapper=xmapper.ref(), parent=plot.ref())
        yaxis = bbmodel.ContinuumModel(
            'D3LinearAxis', orientation='left', ticks=3,
            mapper=ymapper.ref(), parent=plot.ref())
        plot.set('renderers', [scatter.ref()])
        plot.set('axes', [xaxis.ref(), yaxis.ref()])
        plot.set('tools', [pantool.ref(), zoomtool.ref(), selecttool.ref()])
        plot.set('overlays', [selectoverlay.ref()])
        tocreate.extend([xr, yr, datarange1, datarange2,
                         xaxis, yaxis, xmapper, ymapper,
                         pantool, zoomtool, selecttool, selectoverlay,
                         scatter])

        self.upsert_all(tocreate)
        if container is None:
            self.show(plot)
            container = self.ic
        return ScatterPlot(self, plot, data_source, xr, yr,
                           datarange1, datarange2,
                           xmapper, ymapper, scatter,
                           pantool, zoomtool, selecttool, selectoverlay,
                           container)

    def _newlineplot(self, x, y, width=300, height=300, lineplot=None,
                     data_source=None, container=None):
        tocreate = []
        if container:
            xr = bbmodel.ContinuumModel('Range1d', start=0, end=width)
            yr = bbmodel.ContinuumModel('Range1d', start=0, end=height)
            plot = bbmodel.ContinuumModel('Plot', width=width, height=height,
                                          xrange=xr.ref(), yrange=yr.ref(),
                                          parent=container.ref())
        else:
            xr = bbmodel.ContinuumModel('Range1d', start=0, end=width)
            yr = bbmodel.ContinuumModel('Range1d', start=0, end=height)
            plot = bbmodel.ContinuumModel('Plot', width=width, height=height,
                                          xrange=xr.ref(), yrange=yr.ref(),
                                          parent=self.ic.ref())
        tocreate.append(plot)
        if data_source is None:
            data_source = self.make_source(x=x, y=y)
            xfield = 'x'
            yfield = 'y'
        else:
            xfield = x
            yfield = y
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
        pantool = bbmodel.ContinuumModel(
            'PanTool',
            xmappers=[xmapper.ref()],
            ymappers=[ymapper.ref()])
        zoomtool = bbmodel.ContinuumModel(
            'ZoomTool',
            xmappers=[xmapper.ref()],
            ymappers=[ymapper.ref()])
        line = bbmodel.ContinuumModel(
            'LineRenderer', data_source=data_source.ref(),
            xfield=xfield, yfield=yfield, xmapper=xmapper.ref(),
            ymapper=ymapper.ref(), parent=plot.ref())
        xaxis = bbmodel.ContinuumModel(
            'D3LinearAxis', orientation='bottom', ticks=3,
            mapper=xmapper.ref(), parent=plot.ref())
        yaxis = bbmodel.ContinuumModel(
            'D3LinearAxis', orientation='left', ticks=3,
            mapper=ymapper.ref(), parent=plot.ref())
        plot.set('renderers', [line.ref()])
        plot.set('axes', [xaxis.ref(), yaxis.ref()])
        plot.set('tools', [pantool.ref(), zoomtool.ref()])
        tocreate.extend([xr, yr, datarange1, datarange2,
                         xaxis, yaxis, xmapper, ymapper,
                         pantool, zoomtool,
                         line])
        self.upsert_all(tocreate)
        if container is None:
            self.show(plot)
            container = self.ic
        return LinePlot(self, plot, data_source, xr, yr,
                        datarange1, datarange2,
                        xmapper, ymapper, line, pantool, zoomtool,
                        container)


    def line(self, x, y, width=300, height=300, lineplot=None,
             data_source=None, container=None):
        """
        Parameters
        ----------
        x : string of fieldname in data_source, or 1d vector
        y : string of fieldname in data_source or 1d_vector
        lineplot : optional, if you want to add a line to an existing plot
        data_source : optional if x,y are not strings,
            backbonemodel of a data source
        container : bbmodel of container viewmodel

        Returns
        ----------
        (plotmodel, data_source)
        """
        if lineplot is None:
            return self._newlineplot(x, y, width=width, height=height,
                                     data_source=data_source, container=container)
        else:
            return self._addline(lineplot, x, y, data_source=data_source)
    def _add_source_to_range(self, data_source, columns, range):
        sources = range.get('sources')
        added = False
        for source in sources:
            if source['ref'] == data_source:
                newcolumns = np.unique1d(columns, source['columns']).tolist()
                source['columns'] = newcolumns
                added = True
        if not added:
            sources.append({'ref' : data_source.ref(), 'columns' : columns})

    def _addline(self, lineplot, x, y, data_source=None):
        if data_source is None:
            data_source = self.make_source(x=x, y=y)
            xfield, yfield = 'x', 'y'
        else:
            xfield, yfield = x, y
        self._add_source_to_range(data_source, [xfield], lineplot.data_xrange)
        self.update(lineplot.data_xrange.typename, lineplot.data_xrange.attributes)
        self._add_source_to_range(data_source, [yfield], lineplot.data_yrange)
        self.update(lineplot.data_yrange.typename, lineplot.data_yrange.attributes)
        line = bbmodel.ContinuumModel(
            'LineRenderer', data_source=data_source.ref(),
            xfield=xfield, yfield=yfield, xmapper=lineplot.xmapper.ref(),
            ymapper=lineplot.ymapper.ref(), parent=lineplot.plot.ref())
        self.create(line.typename, line.attributes)
        lineplot.plot.get('renderers').append(line.ref())
        self.update(lineplot.plot.typename, lineplot.plot.attributes)
        return lineplot

    def _remove_from_ic(self, plots):
        toremove = set()
        for plot in plots:
            toremove.add(plot.get('id'))
        children = [x for x in self.ic.get('children') if x['id'] not in toremove]
        self.ic.set('children', children)
        self.update(self.ic.typename, self.ic.attributes)

    def _remove_all_grid_parents(self, plots):
        for plot in plots:
            if plot.get('parent')['type'] == 'GridPlotContainer':
                parent = plot.get_ref('parent', self)
                if parent:
                    self._remove_from_ic([parent])
                    self.delete(parent.typename, parent.get('id'))

    def grid(self, plots):
        container = bbmodel.ContinuumModel(
            'GridPlotContainer',
            parent=self.ic.ref())
        flatplots = []
        for row in plots:
            for plot in row:
                flatplots.append(plot.plot)
        self._remove_from_ic(flatplots)
        self._remove_all_grid_parents(flatplots)
        for plot in flatplots:
            plot.set('parent', container.ref())
        plotrefs = [[x.plot.ref() for x in row] for row in plots]
        container.set('children', plotrefs)
        to_update = [container]
        to_update.extend(flatplots)
        self.upsert_all(to_update)
        self.show(container)
        return container

    def show(self, plot):
        children = self.ic.get('children')
        if children is None: children = []
        children.append(plot.ref())
        self.ic.set('children', children)
        self.update(self.ic.typename, self.ic.attributes)

if __name__ == "__main__":
    import numpy as np
    docid = 'b25b6c38-5de9-450a-9db9-9905cdb34117'
    client = PlotClient(docid, "http://localhost:5000/bb/")
    x = np.random.random(100)
    y = np.random.random(100)
    data_source = client.make_source(idx=range(100), x=x, y=y)
    scatterplot1 = client.scatter(x='idx', y='x', color='#F00', data_source=data_source)
    client.scatter(x='idx', y='y', color='#0F0', data_source=data_source)#, scatterplot=scatterplot1)
    xdata = np.arange(0, 10, 0.01)
    ydata = np.sin(xdata)
    lineplot = client.line(xdata, ydata)
    xdata = np.arange(0, 15, 0.01)
    ydata = 2 * np.cos(xdata)
    lineplot=client.line(xdata, ydata, lineplot=lineplot)
