# from wakariserver.. but copy pasted becuase we dont wnat
# wakariserver dependency here.
import shutil
import os
script_paths = [
    'vendor/jquery.1.7.2.min.js',
    'vendor/underscore/underscore.js',
    'vendor/backbone/backbone.js',
    "vendor/jquery/js/jquery.mousewheel.js",
    "vendor/buckets/buckets.js",
    "vendor/d3/d3.v2.js",
    "vendor/bokehjs/js/base.js",
    "vendor/bokehjs/js/view_base.js",
    "vendor/bokehjs/js/model_base.js",
    "vendor/bokehjs/js/ui_view.js",
    "vendor/bokehjs/js/ui_model.js",
    "vendor/bokehjs/js/bokeh_views.js",
    "vendor/bokehjs/js/ticks.js",
    "vendor/bokehjs/js/tools.js",
    "vendor/bokehjs/js/bokeh_model.js",
    "vendor/bokehjs/js/custom.js",
    "js/cdxviews.js",
    "js/cdxmodels.js",
    ]
css_paths = [
    'css/cdx.css',
    'vendor/bokehjs/css/bokeh.css',
    'vendor/bokehjs/css/continuum.css',
    ]

def static_join(*dirs):
    root = os.path.dirname(__file__)
    return os.path.join(root, "static", *dirs)

def css_str(paths):
    retval = ""
    for css_path in paths:
        retval += """
                <link href="%s" rel="stylesheet"/>
                """  % ("./static/" + css_path)
    return retval

def script_str(paths):
    retval = ""
    for script in paths:
        retval += """
           <script type=text/javascript src="%s"></script>
           """ % ("./static/" + script)
    return retval

def concat_scripts(paths):
    output_str = ""
    for script in paths:
        f_name = static_join(script)
        output_str += """
          // BEGIN %s
          """ % f_name

        output_str += open(f_name).read()
        output_str += """
          // END %s
         """ % f_name
    return output_str

def concat_css(paths):
    output_str = ""
    for css_path in paths:
        f_name = static_join(css_path)
        output_str += """
          /* BEGIN %s */
         """ % f_name

        output_str += open(f_name).read().decode("utf-8")
        output_str += """
          /* END %s */
         """ % f_name
    return output_str

def dump_paths(paths, dest):
    for path in paths:
        source = os.path.join("static", path)
        dest = os.path.join(dest, "static", path)
        shutil.copy(source, dest)

    
        
