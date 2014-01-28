# Installation

```bash
$ git clone https://github.com/ContinuumIO/bokeh.git
$ conda install --file bokeh/requirements.txt
$ ln -s $(readlink -f bokeh/bokeh) ~/.local/lib/python2.7/site-packages/bokeh
$ git clone https://github.com/ContinuumIO/cdx.git
$ cd cdx
$ npm install && node_modules/.bin/bower install
$ node_modules/.bin/grunt build
$ ./cdxlocal.py -d --work-dir=cdx-work
```

CDX and Bokeh should belong to the same directory. If this is undesirable,
change `bokeh.json` to a value you prefer. CDX manages build of both its
own and Bokeh's frontend files (coffee, less, etc.), so you have to use
Grunt only once, either issue `grunt build` after changes or `grunt watch`
for dynamic incremental compilation (both in CDX directory).

`npm` and `bower` should be called only once during installation. Later
you should only use `grunt` to build frontend sources, unless you changed
`package.json` or `bower.json`.
