web: gunicorn app:app
init: python db_repository/manage.py db init
migrate: python db_repository/manage.py db migrate
upgrade: python db_repository/manage.py db upgrade
worker: celery -A app.celery worker
