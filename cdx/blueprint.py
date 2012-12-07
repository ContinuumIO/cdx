import flask
import logging
from logging import Formatter
cdx_blueprint = flask.Blueprint('cdx', 'cdx', static_folder='static', static_url_path='/cdx/static')
#file_handler = logging.FileHandler(lConfig.settings['LOG_FILE'])
