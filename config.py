#!/usr/bin/env python

import os
import pymysql


production = bool(os.environ.get('GAE_INSTANCE'))

# Flask configuration settings
SECRET_KEY = os.urandom(24)
DEBUG = not production

# Google Config stuff
PROJECT_ID = 'ultra-compound-180217'
CLOUDSQL_USER = 'root'
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD') # TODO: set this environment var
CLOUDSQL_DATABASE = 'mrs'
CLOUDSQL_CONNECTION_NAME = 'ultra-compound-180217:us-east1:cloudsql-pls-work'

LOCAL_DB_CONNECTION = {
    'user': CLOUDSQL_USER,
    'password': CLOUDSQL_PASSWORD,
    'database': CLOUDSQL_DATABASE,
    'host': '127.0.0.1',
    'port': 3306,
    'cursorclass': pymysql.cursors.DictCursor
}

LIVE_DB_CONNECTION = {
    'user': CLOUDSQL_USER,
    'password': CLOUDSQL_PASSWORD,
    'database': CLOUDSQL_DATABASE,
    'host': 'localhost',
    'unix_socket': '/cloudsql/{connection_name}'.format(connection_name=CLOUDSQL_CONNECTION_NAME),
    'cursorclass': pymysql.cursors.DictCursor
}

"""# for running
LOCAL_DB_URI = (
    'mysql+pymysql://{user}:{password}@127.0.0.1:3306/{database}').format(
        user=CLOUDSQL_USER, password=CLOUDSQL_PASSWORD,
        database=CLOUDSQL_DATABASE)

LIVE_DB_URI = (
    'mysql+pymysql://{user}:{password}@localhost/{database}'
    '?unix_socket=/cloudsql/{connection_name}').format(
        user=CLOUDSQL_USER, password=CLOUDSQL_PASSWORD,
        database=CLOUDSQL_DATABASE, connection_name=CLOUDSQL_CONNECTION_NAME)
"""

if production:
    DB_CONNECTION = LIVE_DB_CONNECTION
else:
    DB_CONNECTION = LOCAL_DB_CONNECTION
