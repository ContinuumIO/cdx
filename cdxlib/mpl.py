import numpy as np
import logging
import urlparse
import requests

import bbmodel
import protocol

log = logging.getLogger(__name__)

class GridPlot(object):
    def __init__(self, client, container, children, title):
        self.plot = container
        self.children = children
        self.title = title
        self.client = client
        
        
class XYPlot(object):
    def __init__(self, client, plot, screen_xrange, screen_yrange,
                 data_xrange, data_yrange, xmapper, ymapper,
                 xaxis, yaxis,
                 pantool, zoomtool, selectiontool, selectionoverlay,
                 parent):
        self.client = client
        self.plotmodel = plot
        self.screen_xrange = screen_xrange
        self.screen_yrange = screen_yrange
        self.data_xrange = data_xrange
        self.data_yrange = data_yrange
        self.xmapper = xmapper
        self.ymapper = ymapper
        self.pantool = pantool
        self.zoomtool = zoomtool
        self.selectiontool = selectiontool
        self.selectionoverlay = selectionoverlay
        self.xaxis = xaxis
        self.yaxis = yaxis
        self.parent = parent
        self.client.upsert_all(
            [self.plotmodel,
            self.screen_xrange,
            self.screen_yrange,
            self.data_xrange,
            self.data_yrange,
            self.xmapper,
            self.ymapper,
            self.pantool,
            self.zoomtool,
            self.selectiontool,
            self.selectionoverlay,
            self.xaxis,
            self.yaxis])
        self.last_source = None
        
    def plot(self, x, y, color='red', data_source=None):
        if data_source is None:
            data_source = self.last_source
        else:
            self.last_source = data_source
        self.scatter(x, y, data_source, color)
    def ensure_source_exists(self, sourcerefs, source, columns):
        sources = [x for x in sourcerefs if x['ref']['id'] == source.get('id')]
        existed = True
        if len(sources) == 0:
            sourcerefs.append({'ref' : source.ref(), 'columns' : columns})
            existed = False
        else:
            for col in columns:
                if col not in sources[0]['columns']:
                    sources[0]['columns'].append(col)
                    existed = False
        return existed
    
    def scatter(self, x, y, data_source, color):
        update = []
        existed = self.ensure_source_exists(
            self.data_xrange.get('sources'),
            data_source, [x])
        import pdb;pdb.set_trace()
        if not existed : update.append(self.data_xrange)
        existed = self.ensure_source_exists(
            self.data_yrange.get('sources'),
            data_source, [y])
        if not existed : update.append(self.data_yrange)
        scatterrenderer = bbmodel.ContinuumModel(
            'ScatterRenderer',
            foreground_color=color,
            data_source=data_source.ref(),
            xfield=x,
            yfield=y,
            xmapper=self.xmapper.ref(),
            ymapper=self.ymapper.ref(),
            parent=self.plotmodel.ref())
        self.plotmodel.get('renderers').append(scatterrenderer.ref())
        update.append(scatterrenderer)
        update.append(self.plotmodel)
        self.client.upsert_all(update)
        self.client.show(self.plotmodel)
        
    def line(self, x, y, data_source):
        pass
        
class PlotClient(bbmodel.ContinuumModelsClient):
    def __init__(self, docid, serverloc, apikey, ph=None):
        url = urlparse.urljoin(serverloc, "/cdx/bb/")
        print url
        if not ph:
            ph = protocol.ProtocolHelper()
        self.ph = ph
        super(PlotClient, self).__init__(docid, url, apikey, self.ph)
        interactive_context = self.fetch(typename='CDXPlotContext')
        self.ic = interactive_context[0]
        
    def updateic(self):
        self.updateobj(self.ic)

    def updateobj(self, obj):
        newobj = self.fetch(obj.typename, obj.get('id'))
        obj.attributes = newobj.attributes
        return obj

    def make_source(self, **kwargs):
        output = []
        flds = kwargs.keys()
        for idx in range(len(kwargs.values()[0])):
            point = {}
            for f in flds:
                if isinstance(kwargs[f][idx], np.ndarray):
                    val = kwargs[f][idx].tolist()
                else:
                    val = kwargs[f][idx]
                point[f] = val
            output.append(point)
        model = self.create('ObjectArrayDataSource', {'data' : output})
        return model
    
    def _newxyplot(self, title=None, width=300, height=300,
                   is_x_date=False, is_y_date=False,
                   container=None):
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
        """
        xr = bbmodel.ContinuumModel('Range1d', start=0, end=width)
        yr = bbmodel.ContinuumModel('Range1d', start=0, end=height)
        plot = bbmodel.ContinuumModel('Plot', width=width, height=height,
                                      xrange=xr.ref(), yrange=yr.ref())
        if container:
            parent = container
            plot.set('parent', container.ref())
        else:
            parent = self.ic
            plot.set('parent', self.ic.ref())
        if title is not None: plot.set('title', title)
        datarangex = bbmodel.ContinuumModel(
            'DataRange1d',
            sources=[]
            )
                     
        datarangey = bbmodel.ContinuumModel(
            'DataRange1d',
            sources=[]
            )
        xmapper = bbmodel.ContinuumModel(
            'LinearMapper', data_range=datarangex.ref(),
            screen_range=xr.ref())
        ymapper = bbmodel.ContinuumModel(
            'LinearMapper', data_range=datarangey.ref(),
            screen_range=yr.ref())
        axisclass = 'D3LinearAxis'
        if is_x_date: axisclass = 'D3LinearDateAxis'
        xaxis = bbmodel.ContinuumModel(
            axisclass, orientation='bottom', ticks=3,
            mapper=xmapper.ref(), parent=plot.ref())
        axisclass = 'D3LinearAxis'
        if is_y_date: axisclass = 'D3LinearDateAxis'
        yaxis = bbmodel.ContinuumModel(
            axisclass, orientation='left', ticks=3,
            mapper=ymapper.ref(), parent=plot.ref())
        pantool = bbmodel.ContinuumModel(
            'PanTool',
            xmappers=[xmapper.ref()],
            ymappers=[ymapper.ref()])
        zoomtool = bbmodel.ContinuumModel(
            'ZoomTool',
            xmappers=[xmapper.ref()],
            ymappers=[ymapper.ref()])
        selecttool = bbmodel.ContinuumModel(
            'SelectionTool',
            renderers=[])
        selectoverlay = bbmodel.ContinuumModel(
            'ScatterSelectionOverlay',
            renderers=[])
        plot.set('renderers', [])
        plot.set('axes', [xaxis.ref(), yaxis.ref()])
        plot.set('tools', [pantool.ref(), zoomtool.ref(), selecttool.ref()])
        plot.set('overlays', [selectoverlay.ref()])
        output = XYPlot(
            self, plot, xr, yr,
            datarangex, datarangey, xmapper, ymapper,
            xaxis, yaxis, pantool, zoomtool,
            selecttool, selectoverlay, parent)
        return output
    
    def plot(self, x, y, title=None, width=300, height=300, color='red',
             is_x_date=False, is_y_date=False,
             data_source=None, container=None):
        self._plot =self._newxyplot(
            title=title,
            width=width, height=height,
            is_x_date=is_x_date, is_y_date=is_y_date,
            container=container)
        if data_source is None:
            self._source = self.make_source(x=x, y=y)
        else:
            self._source = data_source
        self._plot.plot(x, y, color=color, data_source=self._source)

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
                    is_x_date=False, is_y_date=False,
                    title='None', data_source=None, container=None):
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
        newobjs = self._newxyplot(x, y, width=width, height=height, title=title,
                                  is_x_date=is_x_date, is_y_date=is_y_date,
                                  data_source=data_source, container=container)
        tocreate = []
        tocreate.append(newobjs['plot'])
        datarangex, datarangey = newobjs['datarangex'], newobjs['datarangey']
        xmapper, ymapper = newobjs['xmapper'], newobjs['ymapper']
        xr, yr = newobjs['xr'], newobjs['yr']
        xaxis, yaxis = newobjs['xaxis'], newobjs['yaxis']
        xfield, yfield = newobjs['xfield'], newobjs['yfield']
        data_source = newobjs['data_source']
        plot = newobjs['plot']
        pantool = bbmodel.ContinuumModel(
            'PanTool',
            xmappers=[xmapper.ref()],
            ymappers=[ymapper.ref()])
        zoomtool = bbmodel.ContinuumModel(
            'ZoomTool',
            xmappers=[xmapper.ref()],
            ymappers=[ymapper.ref()])
        scatter = bbmodel.ContinuumModel(
            'ScatterRenderer', foreground_color=color,
            data_source=data_source.ref(),
            xfield=xfield, yfield=yfield, xmapper=xmapper.ref(),
            ymapper=ymapper.ref(), parent=plot.ref())
        selecttool = bbmodel.ContinuumModel(
            'SelectionTool',
            renderers=[scatter.ref()])
        selectoverlay = bbmodel.ContinuumModel(
            'ScatterSelectionOverlay',
            renderers=[scatter.ref()])
        plot.set('renderers', [scatter.ref()])
        plot.set('axes', [xaxis.ref(), yaxis.ref()])
        plot.set('tools', [pantool.ref(), zoomtool.ref(), selecttool.ref()])
        plot.set('overlays', [selectoverlay.ref()])
        tocreate.extend([plot, xr, yr, datarangex, datarangey,
                         xaxis, yaxis, xmapper, ymapper,
                         pantool, zoomtool, selecttool, selectoverlay,
                         scatter])
        self.upsert_all(tocreate)
        if container is None:
            self.show(plot)
            container = self.ic
        return ScatterPlot(self, plot, data_source, xr, yr,
                           datarangex, datarangey,
                           xmapper, ymapper, scatter,
                           pantool, zoomtool, selecttool, selectoverlay,
                           container)

    def table(self, data_source, columns, title=None,
              width=300, height=300, container=None):
        if container is None:
            parent = self.ic
        else:
            parent = container
        table = bbmodel.ContinuumModel(
            'DataTable', data_source=data_source.ref(),
            columns=columns, parent=parent.ref())
        self.update(table.typename, table.attributes)
        if container is None:
            self.show(table)
            
    def _newtable(self, x, y, width=300, height=300, color="#000",
                    is_x_date=False, is_y_date=False,
                    title='None', data_source=None, container=None):
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
        newobjs = self._newxytable(x, y, width=width, height=height, title=title,
                                  is_x_date=is_x_date, is_y_date=is_y_date,
                                  data_source=data_source, container=container)
        tocreate = []
        tocreate.append(newobjs['plot'])
        datarangex, datarangey = newobjs['datarangex'], newobjs['datarangey']
        xmapper, ymapper = newobjs['xmapper'], newobjs['ymapper']
        xr, yr = newobjs['xr'], newobjs['yr']
        xfield, yfield = newobjs['xfield'], newobjs['yfield']
        data_source = newobjs['data_source']
        plot = newobjs['plot']
        plot.set('renderers', [table.ref()])
        tocreate.extend([plot, xr, yr, datarangex, datarangey,
                         xmapper, ymapper, table])
        self.upsert_all(tocreate)
        if container is None:
            self.show(plot)
            container = self.ic
        return TablePlot(self, plot, data_source, xr, yr,
                           datarangex, datarangey,
                           xmapper, ymapper, table,
                           None, None, container)


    def _newlineplot(self, x, y, title=None, width=300, height=300, lineplot=None,
                     is_x_date=False, is_y_date=False,
                     data_source=None, container=None):
        tocreate = []
        newobjs = self._newxyplot(x, y, width=width, height=height, title=title,
                                  is_x_date=is_x_date, is_y_date=is_y_date,
                                  data_source=data_source, container=container)
        tocreate = []
        tocreate.append(newobjs['plot'])
        datarangex, datarangey = newobjs['datarangex'], newobjs['datarangey']
        xmapper, ymapper = newobjs['xmapper'], newobjs['ymapper']
        xr, yr = newobjs['xr'], newobjs['yr']
        xaxis, yaxis = newobjs['xaxis'], newobjs['yaxis']
        xfield, yfield = newobjs['xfield'], newobjs['yfield']
        data_source = newobjs['data_source']
        plot = newobjs['plot']
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
        plot.set('renderers', [line.ref()])
        plot.set('axes', [xaxis.ref(), yaxis.ref()])
        plot.set('tools', [pantool.ref(), zoomtool.ref()])
        tocreate.extend([xr, yr, datarangex, datarangey,
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


    def line(self, x, y, title=None, width=300, height=300, lineplot=None,
             is_x_date=False, is_y_date=False,
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
        title : title of plot, only used for new plots
        Returns
        ----------
        (plotmodel, data_source)
        """
        if lineplot is None:
            lineplot = self._newlineplot(
                x, y, title=title,
                is_x_date=is_x_date, is_y_date=is_y_date,
                width=width, height=height,
                data_source=data_source, container=container)
        else:
            lineplot = self._addline(lineplot, x, y, data_source=data_source)
        return lineplot

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


    def grid(self, plots, title=None):
        container = bbmodel.ContinuumModel(
            'GridPlotContainer',
            parent=self.ic.ref())
        if title is not None:
            container.set('title', title)
        flatplots = []
        for row in plots:
            for plot in row:
                flatplots.append(plot.plot)
        for plot in flatplots:
            plot.set('parent', container.ref())
        plotrefs = [[x.plot.ref() for x in row] for row in plots]
        container.set('children', plotrefs)
        to_update = [self.ic, container]
        to_update.extend(flatplots)
        self.upsert_all(to_update)
        self.show(container)
        return GridPlot(self, container, plots, title)

    def show(self, plot):
        self.updateic()
        children = self.ic.get('children')
        if children is None: children = []
        if plot.get('id') not in [x['id'] for x in children]:
            children.append(plot.ref())
        self.ic.set('children', children)
        self.update(self.ic.typename, self.ic.attributes)
        
    def clearic(self):
        self.ic.set('children', [])
        self.update(self.ic.typename, self.ic.attributes)
        
if __name__ == "__main__":
    import numpy as np
    import requests
    import json
    userdata = requests.get('http://localhost:5000/userinfo/').content
    userdata = json.loads(userdata)
    docid = userdata['docs'][0]
    client = PlotClient(docid, "http://localhost:5000/bb/")
    x = np.random.random(100)
    y = np.random.random(100)
    data_source = client.make_source(idx=range(100), x=x, y=y)
    scatterplot1 = client.scatter(x='idx', y='x', color='#F00', data_source=data_source, title='scatter1')
    scatterplot2 = client.scatter(x='idx', y='y', color='#0F0', data_source=data_source, title='scatter2')
    xdata = np.arange(0, 10, 0.01)
    ydata = np.sin(xdata)
    lineplot = client.line(xdata, ydata, title='line1')
    xdata = np.arange(0, 15, 0.01)
    ydata = 2 * np.cos(xdata)
    lineplot1=client.line(xdata, ydata, lineplot=lineplot)

    xdata = np.arange(0, 10, 0.01)
    ydata = np.cos(xdata)
    lineplot = client.line(xdata, ydata, title='line2')
    xdata = np.arange(0, 15, 0.01)
    ydata = 2 * np.sin(xdata)
    lineplot2=client.line(xdata, ydata, lineplot=lineplot)
    client.grid([[scatterplot1, scatterplot2],
                 [lineplot1, lineplot2]], title='all')
