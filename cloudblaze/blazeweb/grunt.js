/*global module:false*/
module.exports = function(grunt) {
    grunt.loadTasks('tasks');
    //grunt.loadNpmTasks('grunt-coffee');
    // Project configuration.
    grunt.initConfig({
        meta: {
            version: '0.1.0',
            banner: '/*! PROJECT_NAME - v<%= meta.version %> - ' +
                '<%= grunt.template.today("yyyy-mm-dd") %>\n' +
                '* http://PROJECT_WEBSITE/\n' +
                '* Copyright (c) <%= grunt.template.today("yyyy") %> ' +
                'YOUR_NAME; Licensed MIT */'
        },
        lint: {
            files: ['grunt.js', 'lib/**/*.js', 'test/**/*.js']
        },
        qunit: {
            files: ['test/**/*.html']
        },
        concat: {
            dist: {
                src: ['<banner:meta.banner>', '<file_strip_banner:lib/FILE_NAME.js>'],
                dest: 'dist/FILE_NAME.js'
            }
        },
        min: {
            dist: {
                src: ['<banner:meta.banner>', '<config:concat.dist.dest>'],
                dest: 'dist/FILE_NAME.min.js'
            }
        },

        jshint: {
            options: {
                curly: true,
                eqeqeq: true,
                immed: true,
                latedef: true,
                newcap: true,
                noarg: true,
                sub: true,
                undef: true,
                boss: true,
                eqnull: true,
                browser: true
            },
            globals: {
                jQuery: true
            }
        },

        uglify: {},

        coffee: {

            bokeh: {
                dir: 'lib/bokehjs/src/coffee',
                dest: 'lib/bokehjs/lib/js',
                bare: true,
            },
            cdx: {
                dir:  'static/coffee',
                dest: 'static/js',
                bare: true,
            }

        },
        watch: {
            bokeh: {
                files: 'lib/bokehjs/src/coffee/*.coffee',
                tasks: 'coffee:bokeh ok'
            },
            cdx: {
                files: 'static/coffee/*.coffee',
                tasks: 'coffee:cdx ok'
            }
        }
    });


    grunt.registerTask('default', 'coffee ok');
    //grunt.registerTask('default', 'lint qunit concat min');


};
