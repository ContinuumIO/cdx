import flask
import logging
from logging import Formatter

app = flask.Flask('cdx', static_url_path='/cdx/static')

app.NODE_INSTALLED = False
#file_handler = logging.FileHandler(lConfig.settings['LOG_FILE'])
