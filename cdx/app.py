import flask
app = flask.Flask('cdx', static_url_path='/cdx/static')

app.NODE_INSTALLED = False
