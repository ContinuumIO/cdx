from cdx import start
from continuumweb import hemlib
import os
app = start.prepare_app()
start.prepare_local()
hemlib.slug_path = os.path.dirname(__file__)
if __name__ == "__main__":
    start.start_app(app, verbose=True)

