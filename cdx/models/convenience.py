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
        dbsession = session if session else app.Session() 
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

