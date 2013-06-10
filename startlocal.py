from cdx import start
from cdx.redisutils import RedisProcess
from continuumweb import hemlib
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
args = parser.parse_args()
app = start.prepare_app(args.username, args.userapikey)
app.start_redis = True
start.prepare_local()
hemlib.slug_path = os.path.dirname(__file__)

if __name__ == "__main__":
    start.start_app(app, verbose=True)

