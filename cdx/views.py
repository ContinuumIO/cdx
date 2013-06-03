from flask import (
    render_template, request,
    send_from_directory, make_response, abort,
    jsonify
    )

from continuumweb import hemlib

from app import cdx_app

@cdx_app.route('/cdx/')
def index(*unused_all, **kwargs):
    if getattr(cdx_app, "debugjs", False):
        slug = hemlib.slug_json()
        static_js = hemlib.slug_libs(cdx_app, slug['libs'])
        cssfiles =  [
            "http://localhost:%s/css/application.css" % cdx_app.hem_port
            ]
        hem_js = hemlib.all_coffee_assets("localhost", cdx_app.hem_port)
    else:
        static_js = ['/cdx/static/js/application.js']
        cssfiles =  ["/cdx/static/css/application.css"]
        hem_js = []
    return render_template(
        'cdx.html',
        jsfiles=static_js,
        hemfiles=hem_js,
        cssfiles=cssfiles
        )


    
