from flask import (
    render_template, request,
    send_from_directory, make_response, abort,
    jsonify, current_app
    )
from continuumweb import hemlib
from app import cdx_app
from bokeh.server.app import bokeh_app

@cdx_app.route('/cdx')
def index():
    ipython_ws_addr = "ws://localhost:%s" % cdx_app.ipython_port
    cdx_addr = "http://localhost:%s" % cdx_app.port
    return render_template('cdx.html',
                  ipython_ws_addr=ipython_ws_addr,
                  cdx_addr=cdx_addr,
                  arrayserver_port=cdx_app.arrayserver_port)
