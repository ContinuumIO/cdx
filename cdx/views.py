from flask import (
    render_template, request,
    send_from_directory, make_response, abort,
    jsonify, current_app
    )
from continuumweb import hemlib
from app import cdx_app
from bokeh.server.app import bokeh_app

def render(template, **kwargs):
    context = hemlib.flask_template_context(cdx_app, cdx_app.hem_port)
    context.update(kwargs)
    return render_template(template, **context)


@cdx_app.route('/cdx/<path:docname>')
def index(docpath=None):
    u = User.load(bokeh_app.model_redis, 
    return render('cdx.html')

    
