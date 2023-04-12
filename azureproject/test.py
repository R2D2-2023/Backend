import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# DBNAME: postgres
#             DBHOST: localhost
#             DBUSER: postgres
#             DBPASS: postgres

DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser="postgres",
    dbpass="postgres",
    dbhost="localhost",
    dbname="postgres"
)

TIME_ZONE = 'Amsterdam'

STATICFILES_DIRS = (str(BASE_DIR.joinpath('static')),)
STATIC_URL = 'static/'

