import os

REDIS_HOST_NAME = os.getenv('REDIS_URL') or 'localhost'
REDIS_PORT = 6379
ASSETS_DIR = './assets/'

DB_HOST_NAME = os.getenv('MYSQL_URL') or 'localhost'
DB_USER = 'finuser'
DB_PASSWORD = 'fin'
DB_NAME = 'findb'
