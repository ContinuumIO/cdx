import os
opj = os.path.join
from sqlalchemy.engine import create_engine

_basedir = os.path.abspath(os.path.dirname(__file__))
class BASE_ENV(object):
    def get_sqlalchemy_engine(self):
        import wakariserver
        engine = create_engine(self.DB_CONNSTRING)
        return engine

class DEV(BASE_ENV):
    DEBUG = True
    USE_CHMOD = False

    SQLITE_PATH = opj(_basedir, "../../../usermgmt/data.db")

    @property
    def DB_CONNSTRING(self):
        connstring = "sqlite:///" + self.SQLITE_PATH
        print connstring
        return connstring


class PROD(BASE_ENV):
    DEBUG = False
    USE_CHMOD = True
    DB_CONNSTRING ='postgresql://wakari_pg:wakari@localhost:5432/wakari_dev_db'

Envies = dict(DEV=DEV, PROD=PROD)

import sys
CSHOP_ENV = os.environ.get("WAKARI_ENV", "DEV")
ENV =  Envies[CSHOP_ENV]()
