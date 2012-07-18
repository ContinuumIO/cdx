prices = da_hdf5_20100111
GLD_ylds = prices['GLD'][4::4] / prices['GLD'][:-4:4]
GLD_ylds = GLD_ylds.seval() 
GLD = prices['GLD'][4::4]
GLD = GLD.seval()
GLD = GLD / GLD[0]

GDX_ylds = prices['GDX'][4::4] / prices['GDX'][:-4:4]
GDX_ylds = GDX_ylds.seval() 
GDX = prices['GDX'][4::4]
GDX = GDX.seval()
GDX = GDX / GDX[0]

USO_ylds = prices['USO'][4::4] / prices['USO'][:-4:4]
USO_ylds = USO_ylds.seval() 
USO = prices['USO'][4::4]
USO = USO.seval()
USO = USO / USO[0]

timestamp = prices['timestamp'][4::4].seval()

source = p.make_source(GLD_ylds=GLD_ylds, GLD=GLD, GDX_ylds=GDX_ylds, GDX=GDX, USO=USO, USO_ylds=USO_ylds, timestamp=timestamp)

gldgdx = p.scatter(x='GLD_ylds', y='GDX_ylds', title='GLD vs GDX', data_source=source)
glduso = p.scatter(x='GLD_ylds', y='USO_ylds', title='GLD vs USO', data_source=source)
gdxuso = p.scatter(x='GDX_ylds', y='USO_ylds', title='GDX vs USO', data_source=source)

lineplot = p.scatter(x='timestamp', y='GDX', color="#F00", title="timeseries", data_source=source, width=800, height=300,)
p.scatter(x='timestamp', y='GLD', color="#0F0", data_source=source, scatterplot=lineplot)
p.scatter(x='timestamp', y='USO', color="#00F", data_source=source, scatterplot=lineplot)
p.line(x='timestamp', y='GDX', data_source=source, lineplot=lineplot)
p.line(x='timestamp', y='GLD', data_source=source, lineplot=lineplot)
p.line(x='timestamp', y='USO', data_source=source, lineplot=lineplot)

p.updateic()
densities = p.grid([[gldgdx, glduso, gdxuso]], title='densities')
all = p.grid([[densities], [lineplot]], title='all')






