import bbmodel

def make_source(**kwargs):
    output = []
    flds = kwargs.keys()
    for idx in range(len(kwargs.values()[0])):
        point = {}
        for f in flds:
            point[f] = kwargs[f][idx]
        output.append(point)
    return bbmodel.ContinuumModel('ObjectArrayDataSource', data=output)

def make_plot(width, height, parent=None):
    plot = bbmodel.ContinuumModel('Plot')
    if parent is not None:
        plot.set('parent', parent.ref())
    return (plot)

def scatter(width, height, data_source, xfield, yfield, container=None):
    if container:
        plot = bbmodel.ContinuumModel('Plot', width=width, height=height,
                                      parent=container.ref())
    else:
        plot = bbmodel.ContinuumModel('Plot', width=width, height=height)
    xr = bbmodel.ContinuumModel('PlotRange1d', plot=plot.ref(), attribute='width')
    yr = bbmodel.ContinuumModel('PlotRange1d', plot=plot.ref(), attribute='height')
    datarange1 = bbmodel.ContinuumModel(
        'DataRange1d', data_source=data_source.ref(),
        columns=[xfield])
    datarange2 = bbmodel.ContinuumModel(
        'DataRange1d', data_source=data_source.ref(), columns=[yfield])
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
    return (plot, xr, yr, datarange1, datarange2,
            xaxis, yaxis, xmapper, ymapper, scatter)
    
