import startprod
from cdx import start
print 'hello'
if __name__ == "__main__":
    import werkzeug.serving
    @werkzeug.serving.run_with_reloader
    def helper ():
        start.start_app()
