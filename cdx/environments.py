import os
from wakariserver.environments import BASE_ENV, DEV, PROD, PROD_DEBUG
BASE_ENV.LOG_FILE_NAME = "cdx.log"
#can customize env hear if you want
Envies = dict(DEV=DEV,
              PROD=PROD,
              PROD_DEBUG=PROD_DEBUG)
ENV =  Envies[os.environ.get("WAKARI_ENV", "DEV")]()

