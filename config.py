#!/usr/bin/env python

import os, logging
import MySQLdb


PRODUCTION = bool(os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'))
if PRODUCTION:
    logging.info("Detected production environment")
else:
    logging.info("Detected local environment")

# Flask configuration settings
SECRET_KEY = os.urandom(24)
DEBUG = not PRODUCTION

LOCAL_DB_CONNECTION = {
    'user': os.environ.get('CLOUDSQL_USER'),
    'passwd': os.environ.get('CLOUDSQL_PASSWORD'),
    'db': os.environ.get('CLOUDSQL_DATABASE'),
    'host': '127.0.0.1',
    'port': 3306,
}

LIVE_DB_CONNECTION = {
    'user': os.environ.get('CLOUDSQL_USER'),
    'passwd': os.environ.get('CLOUDSQL_PASSWORD'),
    'db': os.environ.get('CLOUDSQL_DATABASE'),
    'unix_socket': '/cloudsql/{}'.format(os.environ.get('CLOUDSQL_CONNECTION_NAME')),
}

if PRODUCTION:
    DB_CONNECTION = LIVE_DB_CONNECTION
else:
    DB_CONNECTION = LOCAL_DB_CONNECTION
