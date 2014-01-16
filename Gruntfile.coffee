module.exports = (grunt) ->
  fs = require("fs")

  # (task: String)(input: String) => Boolean
  hasChanged = (task) -> (input) ->
    cwd  = grunt.config.get("#{task}.cwd")
    dest = grunt.config.get("#{task}.dest")
    ext  = grunt.config.get("#{task}.ext")

    output = input.replace(cwd, dest)
                  .replace(/\..+$/, ext)

    if not fs.existsSync(output)
      true
    else
      fs.statSync(input).mtime > fs.statSync(output).mtime

  # (task: String) => String
  files = (task) -> "<%= #{task}.cwd %>/<%= #{task}.src %>"

  grunt.initConfig
    bokeh: grunt.file.readJSON('bokeh.json')
    bokehjs: "<%= bokeh %>/bokehjs"

    coffee:
      compile:
        expand: true
        cwd: 'src/coffee'
        src: '**/*.coffee'
        dest: 'build/js'
        ext: '.js'
        filter: hasChanged("coffee.compile")
        options:
          sourceMap: true
          sourceRoot: ""
      bokeh:
        expand: true
        cwd: '<%= bokehjs %>/src/coffee'
        src: '**/*.coffee'
        dest: 'build/js'
        ext: '.js'
        filter: hasChanged("coffee.bokeh")
        options:
          sourceMap: true
          sourceRoot: ""

    less:
      compile:
        expand: true
        cwd: 'src/less'
        src: 'cdx.less'
        dest: 'build/css'
        ext: '.css'
        options:
          sourceMap: true
      bokeh:
        expand: true
        cwd: '<%= bokehjs %>/src/less'
        src: '*.less'
        dest: 'build/css'
        ext: '.css'
        options:
          sourceMap: true

    eco:
      compile:
        expand : true
        cwd: 'src/coffee'
        src: '**/*.eco'
        ext: '.js'
        dest: 'build/js'
        filter: hasChanged("eco.compile")
        options:
          amd: true
      bokeh:
        expand : true
        cwd: '<%= bokehjs %>/src/coffee'
        src: '**/*.eco'
        ext: '.js'
        dest: 'build/js'
        filter: hasChanged("eco.bokeh")
        options:
          amd: true

    copy:
      coffee:
        files: [{
          expand: true
          cwd: 'src/coffee'
          src: '**/*'
          dest: 'build/js'
        }, {
          expand: true
          cwd: '<%= bokehjs %>/src/coffee'
          src: '**/*'
          dest: 'build/js'
        }]
      vendor:
        files: [
          expand: true
          cwd: '<%= bokehjs %>/src/vendor'
          src: '**/*'
          dest: 'build/vendor'
        ]
      favicon:
        files: [
          expand: true
          cwd: 'src'
          src: 'favicon.ico'
          dest: 'build'
        ]
      img: # TODO: fix the way Boostrap is included and remove this
        files: [
          expand: true
          cwd: 'build/vendor/bootstrap/img'
          src: '*.*'
          dest: 'build/vendor/img'
        ]

    concat:
      options:
        separator: ""
      ipython_js:
        src:
          ("src/vendor/ipython/js/#{file}" for file in [
            "namespace.js"
            "utils.js"
            "events.js"
            "kernel.js"
            "outputarea.js"
            "cell.js"
            "codecell.js"
            "config.js"
            "completer.js"
            "tooltip.js"
            "celltoolbar.js"
            "contexthint.js"
          ])
        dest: 'build/vendor/ipython/ipython.js'
      ipython_css:
        src:
          ("src/vendor/ipython/css/#{file}" for file in [
            "style.min.css"
            "codemirror-ipython.css"
          ])
        dest: 'build/vendor/ipython/ipython.css'
      css:
        src: [
          "build/vendor/jquery-ui/themes/smoothness/jquery-ui.css"
          "build/vendor/bootstrap/css/bootstrap.css"
          "build/vendor/font-awesome/css/font-awesome.css"
          "build/vendor/codemirror/lib/codemirror.css"
          "build/vendor/ipython/ipython.css"
          "build/css/continuum.css"
          "build/css/bokeh.css"
          "build/css/cdx.css"
        ]
        dest: 'build/cdx.css'

    wrap:
      ipython:
        src: 'build/vendor/ipython/ipython.js'
        dest: 'build/vendor/ipython/ipython-amd.js'
        options:
          wrapper: ["define(['jquery', 'codemirror'], function($, CodeMirror) {\n", "return IPython;\n});\n"]
      codemirror:
        src: 'build/vendor/codemirror/lib/codemirror.js'
        dest: 'build/vendor/codemirror/lib/codemirror-amd.js'
        options:
          wrapper: ["define([], function() {\n", "return CodeMirror;\n});\n"]
      jqueryui:
        src: 'build/vendor/jquery-ui/ui/jquery-ui.js',
        dest: 'build/vendor/jquery-ui/ui/jquery-ui-amd.js',
        options:
          wrapper: ["define(['jquery'], function(jQuery) {\n", "return jQuery;\n});\n"]

    watch:
      compile:
        files: [files("coffee.compile"), files("less.compile"), files("eco.compile")]
        tasks: ["compile"]
        options:
          spawn: false
      bokeh:
        files: [files("coffee.bokeh"), files("less.bokeh"), files("eco.bokeh")]
        tasks: ["bokeh"]
        options:
          spawn: false

    clean: ["build"]

    requirejs:
      options:
        logLevel: 2
        baseUrl: "build/js"
        name: '../vendor/almond/almond'
        paths:
          jquery: "../vendor/jquery/jquery"
          jquery_ui: "../vendor/jquery-ui/ui/jquery-ui-amd"
          jquery_mousewheel: "../vendor/jquery-mousewheel/jquery.mousewheel"
          underscore: "../vendor/underscore-amd/underscore"
          backbone: "../vendor/backbone-amd/backbone"
          timezone: "../vendor/timezone/src/timezone"
          sprintf: "../vendor/sprintf/src/sprintf"
          bootstrap: "../vendor/bootstrap/bootstrap-2.0.4"
          codemirror: "../vendor/codemirror/lib/codemirror-amd"
          ipython: "../vendor/ipython/ipython-amd"
        shim:
          sprintf:
            exports: 'sprintf'
        include: ['cdx/cdxmain', 'underscore']
        fileExclusionRegExp: /^test/
      production:
        options:
          optimize: 'uglify2'
          out: 'build/cdx.min.js'
      development:
        options:
          optimize: 'none'
          out: 'build/cdx.js'

    cssmin:
      minify:
        expand: true
        cwd: "build"
        src: "cdx.css"
        dest: "build"
        ext: '.min.css'

  grunt.loadNpmTasks("grunt-contrib-coffee")
  grunt.loadNpmTasks("grunt-contrib-less")
  grunt.loadNpmTasks("grunt-contrib-copy")
  grunt.loadNpmTasks("grunt-contrib-concat")
  grunt.loadNpmTasks("grunt-contrib-watch")
  grunt.loadNpmTasks("grunt-contrib-clean")
  grunt.loadNpmTasks("grunt-contrib-requirejs")
  grunt.loadNpmTasks("grunt-contrib-cssmin")
  grunt.loadNpmTasks("grunt-wrap")
  grunt.loadNpmTasks("grunt-eco")

  grunt.registerTask("default", ["build"])
  grunt.registerTask("build",   ["compile", "bokeh", "copy", "concat", "wrap"])
  grunt.registerTask("compile", ["coffee:compile", "less:compile", "eco:compile"])
  grunt.registerTask("bokeh",   ["coffee:bokeh", "less:bokeh", "eco:bokeh"])
  grunt.registerTask("rebuild", ["clean", "install", "build"])
  grunt.registerTask("deploy",  ["build", "cssmin", "requirejs"])

  grunt.registerTask("install", () ->
    # XXX: This doesn't work yet in grunt, but works well outside (magic!).
    bower = require('bower')
    bower.commands.install([])
         .on('end', (installed) -> console.log("End"))
         .on('error', (errors) -> console.log("Error"))
  )
