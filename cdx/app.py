import flask
import logging
from logging import Formatter

app = flask.Flask('cdx', static_url_path='/cdx/static')

app.NODE_INSTALLED = False
#file_handler = logging.FileHandler(lConfig.settings['LOG_FILE'])
from environments import ENV

file_handler = logging.FileHandler(ENV.LOG_FILE)
file_handler.setLevel(logging.DEBUG)

file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
        ))

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)
app.logger.info('INFO: cdx instatiation')
