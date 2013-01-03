Running CDX
-----------
1.  start redis, you can start it anywhere, I usually start it with redis-server &.  I treat this plot data as disposable so I don't care where it is
2.  build the coffeescript, `python build.py build` inside cdx will build bokehjs coffeescript as well as cdx coffeescript
3.  start cdx, `python startlocaldebug.py`
4.  If you run using anaconda, you will have most of your requirements already.

Plotting
--------

1.  You need to have the cdx client libraries installed.  I do this with `python setupcdxlib.py develop`.
2.  from cdx, you should be able to execute `webplot_example.py`, as well as `glyph_example.py`
3.  Use your browser to visit http://localhost:5006 to see CDX

Bokehjs
-------
bokehjs is a subtree of cdx.  To pull in new bokehjs changes, execute the following
`git subtree pull --prefix=subtree/bokehjs --squash git@github.com:ContinuumIO/bokehjs.git master`

To push changes from cdx back into bokehjs, execute the following

`git subtree push --prefix=subtree/bokehjs --squash ../bokehjs cdxsubtree`

I've picked ../bokehjs as my repository, becuase that's where my local bokehjs repo is.  You should specify
the appropriate path on your machine.  After pushing to branch cdxsubtree, I would perform the merge in your
local bokehjs repo, before pushing to github
