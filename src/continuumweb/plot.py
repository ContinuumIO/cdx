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
    xr = bbmodel.ContinuumModel('Range1d', start=0, end=300)
    yr = bbmodel.ContinuumModel('Range1d', start=0, end=300)
    plot = bbmodel.ContinuumModel(
        'Plot', xrange=xr.ref(), yrange=yr.ref())
    if parent is not None:
        plot.set('parent', parent.ref())
    return (plot, xr, yr)

def scatter(width, height, data_source, xfield, yfield, container=None):
    plot, xr, yr = make_plot(300, 300, parent=container)
    datarange1 = bbmodel.ContinuumModel(
        'DataRange1d', data_source=data_source.ref(),
        columns=[xfield])
    datarange2 = bbmodel.ContinuumModel(
        'DataRange1d', data_source=data_source.ref(), columns=[yfield])
    xmapper = bbmodel.ContinuumModel(
        'LinearMapper', data_range=datarange1.ref(),
        screen_range=plot.get('xrange'))
    ymapper = bbmodel.ContinuumModel(
        'LinearMapper', data_range=datarange2.ref(),
        screen_range=plot.get('yrange'))
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
    
