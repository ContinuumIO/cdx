Continuum Data Explorer (CDX)
=============================

### To install (TODO):

- clone this repo
- clone https://github.com/ContinuumIO/continuumweb
- install continuumweb
- install Bokeh from the cdx subtree `cd subtree/Bokeh; python setup.py install; cd ../../`
- install cdx `python setup.py install`

We recommend using Anaconda 1.6+ to setup Bokeh's and CDX's dependencies.

### To start:

```
$ python cdxlocal.py
```

Navigate to `http://localhost:5030/cdx#cdx/<docname>`. You can pick any document name
for `<docname>`.

Start populating the IPython session with data! In the IPython cell, execute:

```
import pandas as pd
auto = pd.read_csv("cdx/remotedata/auto-mpg.csv")
import statsmodels.api as sm
longley = sm.datasets.longley.load_pandas().data
macrodata = sm.datasets.macrodata.load_pandas().data
sess.cdx.namespace.populate()
sess.plot("weight", "mpg", "auto")
sess.plot("hp", "mpg", "auto")
```

If single cell is insufficient for effective work, you can connect an external IPython
client to CDX session. For example, to start a console client issue (in a new terminal):

```
$ ipython console --existing kernel-1.json
```
