import startprod
from cdx import start
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer

if __name__ == "__main__":
    import werkzeug.serving
    @werkzeug.serving.run_with_reloader
    def helper ():
        startprod.start_app()
