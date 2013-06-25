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
parser.add_argument("--start-redis",
                    help="port for redis",
                    type=bool,
                    default=True
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
    arrayserver_port=args.arrayserver_port
                        )
start.prepare_local()
hemlib.slug_path = os.path.dirname(__file__)

if __name__ == "__main__":
    from cdx import start
    start.start_app(app, verbose=True)

