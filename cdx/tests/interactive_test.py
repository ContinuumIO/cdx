from cdxlib import mpl
import datetime
import time
p = mpl.PlotClient('d6f7f400-06f2-49db-aab9-f7540f04f193', 'https://localhost', 'eb53fc5c-53b5-4e43-a52f-5bbba1bebce4')
p.clearic()
import numpy as np
x = np.arange(100) / 6.0
y = np.sin(x)
z = np.cos(x)
y2 = np.sin(2*x)
z2 = (np.sin(x)/np.cos(x))
data_source = p.make_source(idx=range(100), x=x, y=y, z=z, y2=y2, z2=z2)

def basic():
    p.clf()
    p.plot('x', 'y', color='blue', data_source=data_source, title='sincos')
    p.plot('x', 'z', color='green', data_source=data_source)

#def GetCurrentMicroSeconds(dt=None):
def to_unix_time(dt=None):
    # Ensure the type matches
    if not dt:
        dt = datetime.datetime.now()

    elif type(dt) == type(datetime.datetime.now()):
        return (time.mktime(dt.timetuple())+float("0.%s"%dt.microsecond))*1000

    elif type(dt) == type(datetime.date.today()):
        return time.mktime(dt.timetuple()) * 1000

    else:
        raise ValueError, "You may only use a datetime.datetime or datetime.date instance with GetCurrentMicroSeconds"
def date_example():
    p.clf()
    now = datetime.datetime.now()
    one_day = datetime.timedelta(.05)
    dates = [to_unix_time(now - one_day*n) for n in range(100)]
    data_source = p.make_source(idx=range(100), x=dates, y=y, z=z, y2=y2, z2=z2)
    scatterplot1 = p.plot('x', 'y', is_x_date=True,
        data_source=data_source, title='sin')


def new_plotting_example():
    p.clf()
    data_source = p.make_source(idx=range(100), x=x, y=y, z=z)
    data_source2 = p.make_source(idx=range(100), x2=x, y2=y, z2=z)
    p.plot('x', 'y', data_source=data_source)
    plot1 = p.plot('x', 'z')
    p.clf()
    p.plot(x, y, color='blue')
    plot2 = p.plot(x, z, color='green')

    p.clf()
    data = np.random.random((100, 3))
    plot3 = p.plot(data)
    
    p.clf()
    plot4 = p.plot(data, scatter=True)
    p.clf()
    plot5 = p.plot(x='x', y='y', data_source=data_source)
    p.clf()
    plot6 =p.plot(x='x', y='z', data_source=data_source)
    p.clf()
    p.grid([[plot1, plot2, plot3],
            [plot4, plot5, plot6]])


def table_example():
    table1 = p.table(
        data_source, columns=['idx', 'x', 'y'], title="table")


# # gridplot = p.grid([[scatterplot1, lineplot2]], title='one row')
# #     gridplot3 = p.grid(
# #     [[scatterplot1, lineplot2], [lineplot1]], title='two row uneven')

# # gridplot4 = p.grid(
# #    [[lineplot2], [lineplot1]], title='one column'

basic()
date_example()
new_plotting_example()
table_example()
