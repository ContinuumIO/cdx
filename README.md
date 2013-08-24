Currently the single cell notebook inside CDX only works with IPython < 1.0.  We recommend using this with Anaconda 1.6

we'll port this to 1.0 soon.

cdx
===

### to install

- clone this repo
- clone https://github.com/ContinuumIO/continuumweb
- install continuumweb
- install Bokeh from the cdx subtree `cd subtree/Bokeh; python setup.py install; cd ../../`
- install cdx `python setup.py install`

### to start 

python cdxlocal.py

navigate to http://localhost:5030/cdx#cdx/<docname>. you can just pick a docname.

start populating the IPython session with data!  In the IPython cell, execute:

```

import pandas as pd
auto = pd.read_csv("cdx/remotedata/auto-mpg.csv")
import statsmodels.api as sm
longley = sm.datasets.longley.load_pandas().data
macrodata = sm.datasets.macrodata.load_pandas().data
sess.cdx.namespace.populate()
sess.plot("weight","mpg","auto")
sess.plot("hp","mpg","auto")

```
