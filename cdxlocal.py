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

parser.add_argument("-w", "--work-dir",
                    help="working directory",
                    type=str,
                    default=None
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
app = start.prepare_app(
    username=args.username,
    userapikey=args.userapikey,
    port=args.port,
    ipython_port=args.ipython_port,
    arrayserver_port=args.arrayserver_port,
    redis_port=args.redis_port,
    start_redis=args.start_redis,
    work_dir=args.work_dir,
    debug=args.debug,
    debugjs=args.debugjs)

if __name__ == "__main__":
    def run():
        start.start_app(app)

    #if args.debug:
    #    import werkzeug.serving
    #    werkzeug.serving.run_with_reloader(run)
    #else:
    #    run()
    run()
