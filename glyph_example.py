from webplot import p
import numpy as np
import datetime
import time

source = p.create('ObjectArrayDataSource',
                  {'data' : [
                      {'x' : 1, 'y' : 5, 'z':3, 'radius':10},
                      {'x' : 2, 'y' : 4, 'z':3},
                      {'x' : 3, 'y' : 3, 'z':3, 'color':"red"},
                      {'x' : 4, 'y' : 2, 'z':3},
                      {'x' : 5, 'y' : 1, 'z':3},
                      ]
                   },
                  defer=True
                  )
plot = p.create('Plot', {}, defer=True)
xdr = p.create('DataRange1d', {
    'sources' : [{'ref' : source.ref(), 'columns' : ['x']}],
    }, defer=True)
ydr = p.create('DataRange1d', {
    'sources' : [{'ref' : source.ref(), 'columns' : ['y']}],
    }, defer=True)
glyph_renderer = p.create('GlyphRenderer',{
    'data_source' : source.ref(),
    'xdata_range' : xdr.ref(),
    'ydata_range' : ydr.ref(),
    'scatter_size' : 10,
    'color' : 'black',
    'x' : 'x',
    'y' : 'y',
    'glyphs' : [
        {'type' : 'circles',
         'color' : 'blue'},
        ]
    }, defer=True)

xaxis = p.create('LinearAxis', {
    'orientation' : 'bottom',
    'parent' : plot.ref(),
    'data_range' : xdr.ref()
    }, defer=True)

yaxis = p.create('LinearAxis', {
    'orientation' : 'left',
    'parent' : plot.ref(),
    'data_range' : ydr.ref()
    }, defer=True)
plot.set('renderers', [glyph_renderer.ref()])
plot.set('axes', [xaxis.ref(), yaxis.ref()])

p.buffer_sync()
p.show(plot)



                   
                                            
