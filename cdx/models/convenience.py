import uuid

from . import user
from . import docs
from wakariserver.djangointerface import (
    get_session_data,
    get_user,
    get_current_user,
    login_required
    )

def from_wakari(app, request, session=None):
    """reads django user information, if a user is present,
    we create/ensure an equivalent one lives in our DB.
    We'll call this every time for now.. but we can be more
    efficient about it in the future
    """
    try:
        dbsession = session if session else request.session
        auth_user, wakari_user = get_current_user(dbsession, request)
        if auth_user is None or wakari_user is None:
            return None
        else:
            cdxuser = user.User.load(app.model_redis, auth_user.username)
            if cdxuser is None:
                docid = str(uuid.uuid4())
                doc = docs.new_doc(app, docid, 'main', [auth_user.username])
                cdxuser = user.new_user(
                    app.model_redis,
                    auth_user.username,
                    str(uuid.uuid4()),
                    docs=[doc.docid])
            return cdxuser
    finally:
        #close session if it was not passed  in
        if not session:
            dbsession.close()

def can_read_doc_api(docid, apikey, app):
    doc = docs.Doc.load(app.model_redis, docid)
    return apikey == doc.apikey

def can_write_doc_api(docid, apikey, app):
    doc = docs.Doc.load(app.model_redis, docid)
    return apikey == doc.apikey

def can_read_doc(doc, cdxuser):
    return cdxuser.username in doc.r_users

def can_write_doc(doc, cdxuser):
    return cdxuser.username in doc.rw_users

def can_write_from_request(docid, request, app):
    doc = docs.Doc.load(app.model_redis, docid)
    if request.cookies.get('CDX-api-key'):
        return doc.apikey == request.cookies['CDX-api-key']
    else:
        user = from_wakari(app, request)
        return can_write_doc(doc, user)
