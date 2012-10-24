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

class TablePlot(object):
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

    def make_arrayserver_source(self, obj):
        ## hack right now we coerce the id based on url,
        ## so that we can link our js
        ## and python objects together
        if hasattr(obj, 'url'):
            url = obj.url
        else:
            _ip = get_ipython()
            url = _ip.tableurls.get(id(obj), None)
            if url is None:
                _ip.kernel.save_temp_table(_ip.user_ns['bc'], obj)
            url = _ip.tableurls[id(obj)]
        return self.create('ArrayServerObjectArrayDataSource',
                           {'url' : url, 'id' : url.replace("/", "_")})

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

    def _xydata(self, x, y, data_source=None):
        """if data_source is provided, then x and y are names of fields in the data_source
        if data_source is not provided, a data_source is constructed from x,y
        """
        if data_source is None:
            data_source = self.make_source(x=x, y=y)
            xfield = 'x'
            yfield = 'y'
        else:
            xfield = x
            yfield = y
        return xfield, yfield, data_source

    def _newxyplot(self, x, y, title=None, width=300, height=300,
                   data_source=None,
                   is_x_date=False, is_y_date=False, container=None):
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

        xfield, yfield, data_source = self._xydata(x, y, data_source=data_source)
        if container:
            plot.set('parent', container.ref())
        else:
            plot.set('parent', self.ic.ref())
        if title is not None: plot.set('title', title)
        datarangex = bbmodel.ContinuumModel(
            'DataRange1d',
            sources=[{'ref' : data_source.ref(),
                      'columns' : [xfield]}])
        datarangey = bbmodel.ContinuumModel(
            'DataRange1d',
            sources=[{'ref' : data_source.ref(),
                      'columns' : [yfield]}])
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
        output = dict(plot=plot, xr=xr, yr=yr, xfield=xfield, yfield=yfield,
                      datarangex=datarangex, datarangey=datarangey,
                      xmapper=xmapper, ymapper=ymapper,
                      xaxis=xaxis, yaxis=yaxis,
                      data_source=data_source)
        return output

    def scatter(self, x, y, title=None, width=300, height=300, color="#000",
                is_x_date=False, is_y_date=False,
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
             scatterplot = self._newscatter(
                 x, y, title=title,
                 width=width, height=height, color=color,
                 is_x_date=is_x_date, is_y_date=is_y_date,
                 data_source=data_source, container=container)
        else:
            scatterplot = self._addscatter(
                scatterplot, x, y, color=color,
                data_source=data_source)
        return scatterplot

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
        children.append(plot.ref())
        self.ic.set('children', children)
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
