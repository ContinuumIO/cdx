import cloudblaze.ipython.runnotebook as runnotebook

def create_or_load_namespace(app, docid):
    ipython_app = runnotebook.app
    kernel_manager = ipython_app.web_app.kernel_manager
    kernel_id = kernel_manager.start_kernel(docid)
    return kernel_id

def create_or_load_namespace_for_user(app, user, session, docid=None):
    if docid is None:
        docid = user.docs[0]
        if 'docid' in session:
            docid = session['docid']
    return create_or_load_namespace(app, docid)
