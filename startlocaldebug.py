from cdx import start
start.prepare_app()
@werkzeug.serving.run_with_reloader
def helper ():
    start.start_app()

