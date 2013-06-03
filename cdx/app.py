import flask
import logging
from logging import Formatter

cdx_app = flask.Blueprint('cdx', 'cdx',
                          static_folder='static',
                          static_url_path='/cdx/static',
                          template_folder='templates')



