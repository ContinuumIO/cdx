import numpy as np
import logging
import urlparse
import requests

import bbmodel
import protocol

log = logging.getLogger(__name__)
colors = [
      "#1f77b4",
      "#ff7f0e", "#ffbb78",
      "#2ca02c", "#98df8a",
      "#d62728", "#ff9896",
      "#9467bd", "#c5b0d5",
      "#8c564b", "#c49c94",
      "#e377c2", "#f7b6d2",
      "#7f7f7f",
      "#bcbd22", "#dbdb8d",
      "#17becf", "#9edae5"
    ]

class GridPlot(object):
    def __init__(self, client, container, children, title):
        self.plot = container
        self.children = children
        self.title = title
        self.client = client


class XYPlot(object):
    def __init__(self, client, plot, 
                 xdata_range, ydata_range,
                 xaxis, yaxis,
                 pantool, zoomtool, selectiontool, selectionoverlay,
                 parent):
        self.client = client
        self.plotmodel = plot
        self.xdata_range = xdata_range
        self.ydata_range = ydata_range
        self.pantool = pantool
        self.zoomtool = zoomtool
        self.selectiontool = selectiontool
        self.selectionoverlay = selectionoverlay
        self.xaxis = xaxis
        self.yaxis = yaxis
        self.parent = parent
        self.update_cdx()

        self.last_source = None
        self.color_index = 0

    def update_cdx(self):
        self.client.upsert_all(
            [self.plotmodel,
             self.xdata_range,
             self.ydata_range,
             self.pantool,
             self.zoomtool,
             self.selectiontool,
             self.selectionoverlay,
             self.xaxis,
             self.yaxis])


    def iframe_url(self):
        f_str = "%(root_url)s/iframe#plots/%(doc_id)s/%(plot_id)s"
        return f_str % dict(
            root_url=self.client.root_url,
            doc_id=self.client.docid, plot_id=self.plotmodel.id)

    def make_public(self):
        self.plotmodel.attributes['public']=True
        self.update_cdx()

    def scatter(self, *args, **kwargs):
        kwargs['scatter'] = True
        return self.plot(*args, **kwargs)

    def plot(self, x, y=None, color=None, data_source=None,
             scatter=False):
        def source_from_array(x, y):
            if y.ndim == 1:
                source = self.client.make_source(x=x, y=y)
                xfield = 'x'
                yfields = ['y']
            elif y.ndim == 2:
                kwargs = {}
                kwargs['x'] = x
                colnames = []
                for colnum in range(y.shape[1]):
                    colname = 'y' + str(colnum)
                    kwargs[colname] = y[:,colnum]
                    colnames.append(colname)
                source = self.client.make_source(**kwargs)
                xfield = 'x'
                yfields = colnames
            else:
                raise Exception, "too many dims"
            return source, xfield, yfields
        if not isinstance(x, basestring):
            if y is None:
                y = x
                x = range(len(y))
                if isinstance(y, np.ndarray):
                    source, xfield, yfields = source_from_array(x, y)
                else:
                    source = self.client.make_source(x=x, y=y)
                    xfield, yfields = ('x', ['y'])
            else:
                if isinstance(y, np.ndarray):
                    source, xfield, yfields = source_from_array(x, y)
                else:
                    source = self.client.make_source(x=x, y=y)
                    xfield, yfields = ('x', ['y'])
        else:
            xfield = x
            if y is None:
                raise Exception, 'must specify X and Y when calling with strings'
            yfields = [y]
            if data_source:
                source = data_source
            else:
                source = self.last_source
        self.last_source = source
        for yfield in yfields:
            if color is None:
                use_color = colors[self.color_index % len(colors)]
            else:
                use_color = color
            self.color_index += 1
            self.scatter(xfield, yfield, source, use_color)
            if not scatter:
                self.line(xfield, yfield, source, use_color)

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
            self.xdata_range.get('sources'),
            data_source, [x])
        if not existed : update.append(self.xdata_range)
        existed = self.ensure_source_exists(
            self.ydata_range.get('sources'),
            data_source, [y])
        if not existed : update.append(self.ydata_range)
        scatterrenderer = bbmodel.ContinuumModel(
            'ScatterRenderer',
            foreground_color=color,
            data_source=data_source.ref(),
            xfield=x,
            yfield=y,
            xdata_range=self.xdata_range.ref(),
            ydata_range=self.ydata_range.ref(),
            parent=self.plotmodel.ref())
        self.plotmodel.get('renderers').append(scatterrenderer.ref())
        self.selectiontool.get('renderers').append(scatterrenderer.ref())
        self.selectionoverlay.get('renderers').append(scatterrenderer.ref())
        update.append(scatterrenderer)
        update.append(self.plotmodel)
        update.append(self.selectiontool)
        update.append(self.selectionoverlay)
        self.client.upsert_all(update)
        self.client.show(self.plotmodel)

    def line(self, x, y, data_source, color):
        update = []
        existed = self.ensure_source_exists(
            self.xdata_range.get('sources'),
            data_source, [x])
        if not existed : update.append(self.xdata_range)
        existed = self.ensure_source_exists(
            self.ydata_range.get('sources'),
            data_source, [y])
        if not existed : update.append(self.ydata_range)
        linerenderer = bbmodel.ContinuumModel(
            'LineRenderer',
            foreground_color=color,
            data_source=data_source.ref(),
            xfield=x,
            yfield=y,
            xdata_range=self.xdata_range.ref(),
            ydata_range=self.ydata_range.ref(),
            parent=self.plotmodel.ref())
        self.plotmodel.get('renderers').append(linerenderer.ref())
        update.append(linerenderer)
        update.append(self.plotmodel)
        update.append(self.selectiontool)
        update.append(self.selectionoverlay)
        self.client.upsert_all(update)
        self.client.show(self.plotmodel)

class PlotClient(bbmodel.ContinuumModelsClient):
    def __init__(self, docid, serverloc, apikey="nokey", ph=None):
        #the root url should be just protocol://domain
        self.root_url = serverloc
        url = urlparse.urljoin(serverloc, "/cdx/bb/")
        if not ph:
            ph = protocol.ProtocolHelper()
        self.ph = ph
        super(PlotClient, self).__init__(docid, url, apikey, self.ph)
        interactive_context = self.fetch(typename='CDXPlotContext')
        self.ic = interactive_context[0]
        self.clf()
        self._hold = True

    def hold(self, val):
        if val == 'on':
            self._hold = True
        elif val == 'off':
            self._hold = False
        else:
            self._hold = val

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
                val = kwargs[f][idx]
                if isinstance(val, float) and  np.isnan(val):
                    val = "NaN"
                elif isinstance(val, np.ndarray):
                    val = val.tolist()
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
        plot = bbmodel.ContinuumModel('Plot', width=width, height=height)
        if container:
            parent = container
            plot.set('parent', container.ref())
        else:
            parent = self.ic
            plot.set('parent', self.ic.ref())
        if title is not None: plot.set('title', title)
        xdata_range = bbmodel.ContinuumModel(
            'DataRange1d',
            sources=[]
            )
        ydata_range = bbmodel.ContinuumModel(
            'DataRange1d',
            sources=[]
            )
        axisclass = 'D3LinearAxis'
        if is_x_date: axisclass = 'D3LinearDateAxis'
        xaxis = bbmodel.ContinuumModel(
            axisclass, orientation='bottom', ticks=3,
            data_range=xdata_range.ref(), parent=plot.ref())
        axisclass = 'D3LinearAxis'
        if is_y_date: axisclass = 'D3LinearDateAxis'
        yaxis = bbmodel.ContinuumModel(
            axisclass, orientation='left', ticks=3,
            data_range=ydata_range.ref(), parent=plot.ref())
        pantool = bbmodel.ContinuumModel(
            'PanTool',
            dataranges=[xdata_range.ref(), ydata_range.ref()],
            dimensions=['width', 'height']
            )
        zoomtool = bbmodel.ContinuumModel(
            'ZoomTool',
            dataranges=[xdata_range.ref(), ydata_range.ref()],
            dimensions=['width', 'height']
            )
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
            self, plot, xdata_range, ydata_range,
            xaxis, yaxis, pantool, zoomtool,
            selecttool, selectoverlay, parent)
        return output

    def clf(self):
        self._plot = None
    def clear(self):
        self._plot = None
    def figure(self):
        self._plot = None
    def plot_dates(self, *args, **kwargs):
        kwargs['is_x_date'] = True
        return self.plot(*args, **kwargs)

    def scatter(self, *args, **kwargs):
        kwargs['scatter'] = True
        return self.plot(*args, **kwargs)

    def plot(self, x, y=None, color=None, title=None, width=300, height=300,
             scatter=False, is_x_date=False, is_y_date=False,
             data_source=None, container=None):
        if not self._hold:
            self.figure()
        if not self._plot:
            self._plot =self._newxyplot(
                title=title,
                width=width, height=height,
                is_x_date=is_x_date, is_y_date=is_y_date,
                container=container
                )
        self._plot.plot(x, y=y, color=color,
                        data_source=data_source,
                        scatter=scatter
                        )
        return self._plot

    def table(self, data_source, columns, title=None,
              width=300, height=300, container=None):
        if container is None:
            parent = self.ic
        else:
            parent = container
        table = bbmodel.ContinuumModel(
            'DataTable', data_source=data_source.ref(),
            columns=columns, parent=parent.ref(),
            width=width,
            height=height)
        self.update(table.typename, table.attributes)
        if container is None:
            self.show(table)

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

    def grid(self, plots, title=None):
        container = bbmodel.ContinuumModel(
            'GridPlotContainer',
            parent=self.ic.ref())
        if title is not None:
            container.set('title', title)
        flatplots = []
        for row in plots:
            for plot in row:
                flatplots.append(plot.plotmodel)
        for plot in flatplots:
            plot.set('parent', container.ref())
        plotrefs = [[x.plotmodel.ref() for x in row] for row in plots]
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
            children.insert(0, plot.ref())
        self.ic.set('children', children)
        self.update(self.ic.typename, self.ic.attributes)

    def clearic(self):
        self.ic.set('children', [])
        self.update(self.ic.typename, self.ic.attributes)
