web: gunicorn app:app
init: python __init__.py db init
migrate: python __init__.py db migrate
upgrade: python __init__.py db upgrade
worker: celery -A app.celery worker
