import startlocal
from cdx import start
if __name__ == "__main__":
    import werkzeug.serving
    @werkzeug.serving.run_with_reloader
    def helper ():
        start.start_app()
