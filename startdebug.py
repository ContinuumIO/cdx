from . import start
start.prepare_app()
import werkzeug.serving
@werkzeug.serving.run_with_reloader
def helper ():
    start.start_app()
