1/0
import cdx.ipython.runnotebook as runnotebook
import tornado.web as tornadoweb
import os
from IPython.nbformat import current
import logging
log = logging.getLogger(__name__)

def ensure_ipython_notebook(app, docid):
    ipython_app = runnotebook.app
    nbm = ipython_app.web_app.notebook_manager
    try:
        nbm.get_notebook(nbm.rev_mapping[docid])
        return nbm.rev_mapping[docid]
    except tornadoweb.HTTPError as e:
        log.exception(e)
    except KeyError as e:
        log.exception(e)
    path = nbm.get_path_by_name(docid)
    notebook_id = nbm.new_notebook_id(docid)
    metadata = current.new_metadata(name=docid)
    nb = current.new_notebook(metadata=metadata)
    print 'CREATE NOTEBOOK', docid, notebook_id
    with open(path,'w') as f:
        current.write(nb, f, u'json')
    return notebook_id

def create_or_load_namespace(app, docid):
    ipython_app = runnotebook.app
    kernel_manager = ipython_app.web_app.kernel_manager
    notebook_id = ensure_ipython_notebook(app, docid)
    kernel_id = kernel_manager.start_kernel(notebook_id)
    return docid, kernel_id, notebook_id

def create_or_load_namespace_for_user(app, user, session, docid):
    return create_or_load_namespace(app, docid)
