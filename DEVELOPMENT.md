# Installation

## Bokeh

```
$ git clone https://github.com/ContinuumIO/bokeh.git
$ cd bokeh
$ git remote add mattpap https://github.com/mattpap/bokeh.git
$ git fetch mattpap
$ git chekout mattpap/devel
$ ln -s . ~/.local/lib/python2.7/site-packages/bokeh
```

## CDX

```
$ cd ..
$ git clone https://github.com/ContinuumIO/cdx.git
$ cd cdx
$ git remote add mattpap https://github.com/mattpap/cdx.git
$ git fetch mattpap
$ git chekout mattpap/cdx-pivot
$ npm install && node_modules/.bin/bower install
$ grunt build
$ echo '/work' >> .git/info/exclude
$ ./cdxlocal.py --work-dir=work
```

CDX and Bokeh should belong to the same directory. If this is undesirable,
change `bokeh.json` to a value you prefer. CDX manages build of both its
own and Bokeh's frontend files (coffe, less, etc.), so you have to use
Grunt only once, either issue `grunt build` after changes or `grunt watch`
for dynamic incremental compilation (both in CDX directory).
