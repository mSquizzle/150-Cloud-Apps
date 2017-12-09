#!/usr/bin/env python

import os, logging


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
    def CONNECT():
        import MySQLdb
        conn = MySQLdb.connect(**LIVE_DB_CONNECTION)
        conn.autocommit(True)
        return conn
else:
    def CONNECT():
        import pymysql, os
        conn = pymysql.connect(
            host='127.0.0.1',
            user=os.environ.get('CLOUDSQL_USER'),
            password=os.environ.get('CLOUDSQL_PASSWORD'),
            database=os.environ.get('CLOUDSQL_DATABASE'),
            autocommit=True
        )
        return conn
