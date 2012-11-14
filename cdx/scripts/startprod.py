from cdx import start
from cdx.app import app
from wakariserver import djangointerface, cdxlib
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from wakariserver.flasklib import RequestSession
import os
import logging
from logging import Formatter
from wakariserver.environments import BASE_ENV, DEV, PROD, PROD_DEBUG
BASE_ENV.LOG_FILE_NAME = "cdx.log"
#can customize env hear if you want
Envies = dict(DEV=DEV,
              PROD=PROD,
              PROD_DEBUG=PROD_DEBUG)
ENV =  Envies[os.environ.get("WAKARI_ENV", "DEV")]()

start.prepare_app()
app.debug = ENV.DEBUG
#monkeypatching
def current_user(request):
    return cdxlib.cdx_from_wakari(app, request)

def write_plot_file(username, codedata):
    homedir = ENV.homedir(username)
    fpath = os.path.join(homedir, 'wakaripython', 'webplot.py')
    with open(fpath, "w+") as f:
        f.write(codedata)
    if ENV.USE_CHMOD:
        os.system("sudo chown %s  %s " % (username, fpath))
        
app.current_user = current_user
app.write_plot_file = write_plot_file

#database
app.dbengine = create_engine(ENV.DB_CONNSTRING)
app.Session = sessionmaker(bind=app.dbengine)
rs = RequestSession(app)
rs.setup_app()

#logging
file_handler = logging.FileHandler(ENV.LOG_FILE)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
        ))
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)
app.logger.info('INFO: cdx instatiation')

if __name__ == "__main__":
    start.start_app()

