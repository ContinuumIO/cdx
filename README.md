Running CDX
-----------
1.  start redis, you can start it anywhere, I usually start it with redis-server &.  I treat this plot data as disposable so I don't care where it is
2.  build the coffeescript, `python build.py build` inside cdx will build bokehjs coffeescript as well as cdx coffeescript
3.  start cdx, python startlocaldebug.py

To do plotting, you need to have the cdx client libraries installed.  I do this with `python setupcdxlib.py develop`.

4.  from cdx, you should be able to execute `webplot_example.py`, as well as `glyph_example.py`
