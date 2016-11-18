import sys
import logging

from flask import Flask
from config import SECRET_KEY,GOOGLE_ID, GOOGLE_SECRET, EMBEDLY_KEY, CELERY_BROKER, REDIS_CACHE_URL
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_login import LoginManager
from flask_oauthlib.client import OAuth
from embedly import Embedly
from celery import Celery
from config import CELERY_BROKER
import redis


app = Flask(__name__)
app.config.from_object('config')
app.secret_key = SECRET_KEY

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

cli = Embedly(EMBEDLY_KEY)

redis_cache = redis.from_url(HEROKU_REDIS_AMBER_URL)

celery = Celery('app', broker = CELERY_BROKER)

oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=GOOGLE_ID,
    consumer_secret=GOOGLE_SECRET,
    request_token_params={
        'scope': 'email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)



lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.login_message = u'you must login to view this page'

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

from app import views, models
