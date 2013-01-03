from cdx import start
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
import gevent
from cdx.app import app
import cdx.wsmanager as wsmanager
from wakariserver import djangointerface, cdxlib
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from wakariserver.flasklib import RequestSession
import os
import logging
from logging import Formatter
from wakariserver.environments import ENV
import wakariserver.environments as environments
environments.BASE_ENV.LOG_FILE_NAME = "cdx.log"

start.prepare_app()
def userauth(auth, topicusername):
    #auth token should be sessionid
    return True
    # dbsession = current_app.Session()
    # sessiondata = djangointerface.get_session_data(dbsession, auth)
    # auth_user, wakari_user = djangointerface.get_user_from_session(
    #     dbsession, sessiondata
    #     )
    #return auth_user.username == topicusername

def allauth(auth, topic):
    return True
app.wsmanager.register_auth("user", userauth)
app.wsmanager.register_auth("all", allauth)    

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

def start_app():
    http_server = WSGIServer(('', 5006), app,
                             handler_class=WebSocketHandler,
                             keyfile="/etc/nginx/wakari.key",
                             certfile="/etc/nginx/wakari.crt"
                             )
    t = gevent.spawn(wsmanager.pub_from_redis,
                     app.pubsub_redis,
                     app.wsmanager)
    http_server.serve_forever()
    
if __name__ == "__main__":
    start_app()
    
