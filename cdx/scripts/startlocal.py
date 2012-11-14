from cdx import start
from cdx.app import app
import cdx.models.user as user
import cdx.models.docs as docs
import uuid

import os
import logging
start.prepare_app()
app.debug = True

#monkeypatching
def current_user(request):
    cdxuser = user.User.load(app.model_redis, "defaultuser")
    if cdxuser is None:
        docid = str(uuid.uuid4())
        doc = docs.new_doc(app, docid, 'main', ["defaultuser"])
        cdxuser = user.new_user(
            app.model_redis,
            "defaultuser",
            str(uuid.uuid4()),
            docs=[doc.docid])
    return cdxuser

def write_plot_file(username, codedata):
    fpath = 'webplot.py'
    with open(fpath, "w+") as f:
        f.write(codedata)
        
app.current_user = current_user
app.write_plot_file = write_plot_file

#database

#logging

if __name__ == "__main__":
    start.start_app()

