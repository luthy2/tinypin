import os
import json

basedir = os.path.abspath(os.path.dirname(__file__))


WTF_CSRF_ENABLED = True
SECRET_KEY = 'secret_key'

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

GOOGLE_ID = "895802829519-q8kk7j0m51cspgqarlt2dftn45lv74hm.apps.googleusercontent.com"
GOOGLE_SECRET = "ERSwX1R1kmLnzabq-IwfF3DQ"

EMBEDLY_KEY = '7cc09b03ae3b48c5b8025541369b22c3'

# SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
# SQLALCHEMY_RECORD_QUERIES = True

CELERY_BROKER = os.environ.get("REDIS_URL")
CELERY_REDIS_MAX_CONNECTIONS = 20
CELERY_TASK_SERIALIZER = json
BROKER_POOL_LIMIT = 1

REDIS_CACHE_URL = os.environ.get("HEROKU_REDIS_AMBER_URL")

DATABASE_QUERY_TIMEOUT = 0.5

# SERVER_NAME = 'localhost:5000'
