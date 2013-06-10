import argparse, sys

from bokeh.server import start


parser = argparse.ArgumentParser(description="Start the Bokeh plot server")
parser.add_argument("-d", "--debug", action="store_true", default=False)
parser.add_argument("-j", "--debugjs", action="store_true", default=False)
parser.add_argument("-v", "--verbose", action="store_true", default=False)
args = parser.parse_args(sys.argv[1:])

start.prepare_app()
start.prepare_local()

start.app.debugjs = args.debugjs

if args.debug:
    start.app.debug = True
    import werkzeug.serving
    @werkzeug.serving.run_with_reloader
    def helper():
        # Always set to verbose if in debug mode
        start.start_app(verbose=True)
    
else:
    start.start_app(verbose=args.verbose)

