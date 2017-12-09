#!/usr/bin/env python

import os, logging
import MySQLdb


production = bool(os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'))
if production:
    logging.info("Detected production environment")
else:
    logging.info("Detected local environment")

# Flask configuration settings
SECRET_KEY = os.urandom(24)
DEBUG = not production

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

if production:
    logging.info("Database host: {}".format(LIVE_DB_CONNECTION['host']))
    DB_CONNECTION = LIVE_DB_CONNECTION
else:
    logging.info("Database host: {}".format(LOCAL_DB_CONNECTION['host']))
    DB_CONNECTION = LOCAL_DB_CONNECTION
