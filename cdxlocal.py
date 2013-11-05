#!/usr/bin/env python

import os
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--username",
                    help="username for bokeh",
                    default="defaultuser"
                    )
parser.add_argument("--userapikey",
                    help="user apikey for bokeh",
                    default="nokey"
                    )
#ports

parser.add_argument("--port",
                    help="port for cdx",
                    type=int,
                    default=5030
                    )
parser.add_argument("--ipython-port",
                    help="port for ipython single cell notebook",
                    type=int,
                    default=10010
                    )
parser.add_argument("--arrayserver-port",
                    help="port for ipython arrayserver",
                    type=int,
                    default=10020
                    )
parser.add_argument("--redis-port",
                    help="port for redis",
                    type=int,
                    default=7000
                    )
parser.add_argument("-r", "--start-redis",
                    help="start redis",
                    action="store_true",
                    default=True
                    )

parser.add_argument("-d", "--debug",
                    help="debug python",
                    action="store_true",
                    default=False
                    )

parser.add_argument("-j", "--debugjs",
                    help="debug js",
                    action="store_true",
                    default=False
                    )

args = parser.parse_args()
from cdx import start
from continuumweb import hemlib
app = start.prepare_app(
    port=args.port,
    username=args.username,
    userapikey=args.userapikey,
    ipython_port=args.ipython_port,
    redis_port=args.redis_port,
    arrayserver_port=args.arrayserver_port,
    debug=args.debug, debugjs=args.debugjs
    )
start.prepare_local()
if args.debugjs:
    print "if you are debugging javascript, you must execute cdx from the same directory as slug.json"
    hemlib.slug_path = os.path.dirname(__file__)

if __name__ == "__main__":
    from cdx import start
    if args.debug:
        import werkzeug.serving
        @werkzeug.serving.run_with_reloader
        def helper ():
            start.start_app(app, verbose=True)
    else:
        start.start_app(app, verbose=True)

