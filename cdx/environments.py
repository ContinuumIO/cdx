import os
from os.path import join, dirname
from sqlalchemy.engine import create_engine

class BASE_ENV(object):
    pass

class DEV(BASE_ENV):
    DEBUG = True
    USE_CHMOD = False
    @staticmethod
    def get_sqlalchemy_engine():
        import wakariserver
        sqlitepath = join(dirname(dirname(wakariserver.__file__)),
                          'usermgmt',
                          'data.db')
        connstring = "sqlite:///" + sqlitepath
        engine = create_engine(connstring)
        return engine
    
class PROD(BASE_ENV):
    DEBUG = False
    USE_CHMOD = True
    def get_sqlalchemy_engine():
        import wakariserver
        """need to change this"""
        sqlitepath = join(dirname(dirname(wakariserver.__file__)),
                          'usermgmt',
                          'data.db')
        connstring = "sqlite:///" + sqlitepath
        engine = create_engine(connstring)
        return engine
        
Envies = dict(DEV=DEV, PROD=PROD)

import sys
CSHOP_ENV = os.environ.get("WAKARI_ENV", "DEV")
ENV =  Envies[CSHOP_ENV]()
