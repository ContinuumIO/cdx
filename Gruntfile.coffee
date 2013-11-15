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
      bokeh:
        expand: true
        cwd: '<%= bokehjs %>/src/coffee'
        src: '**/*.coffee'
        dest: 'build/js'
        ext: '.js'
        filter: hasChanged("coffee.bokeh")
        options:
          sourceMap: true

    less:
      compile:
        expand: true
        cwd: 'src/less'
        src: 'cdx.less'
        dest: 'build/css'
        ext: '.css'
      bokeh:
        expand: true
        cwd: '<%= bokehjs %>/src/less'
        src: '*.less'
        dest: 'build/css'
        ext: '.css'

    eco:
      compile:
        expand : true
        cwd: 'src/coffee'
        src: '**/*.eco'
        ext: '.js'
        dest: 'build/js'
        filter: hasChanged("eco.compile")
        options:
          amd: false
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
      vendor:
        files: [
          expand: true
          cwd: 'src/vendor'
          src: '**/*'
          dest: 'build/js/vendor'
        ]

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

  grunt.loadNpmTasks("grunt-contrib-coffee")
  grunt.loadNpmTasks("grunt-contrib-less")
  grunt.loadNpmTasks("grunt-contrib-copy")
  grunt.loadNpmTasks("grunt-contrib-watch")
  grunt.loadNpmTasks("grunt-contrib-clean")
  grunt.loadNpmTasks("grunt-eco")

  grunt.registerTask("default", ["build"])
  grunt.registerTask("build",   ["compile", "bokeh", "copy"])
  grunt.registerTask("compile", ["coffee:compile", "less:compile", "eco:compile"])
  grunt.registerTask("bokeh",   ["coffee:bokeh", "less:bokeh", "eco:bokeh"])
