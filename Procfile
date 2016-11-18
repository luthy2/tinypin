web: gunicorn app:app
init: python db_repository/manage.py init
migrate: python db_repository/manage.py migrate
upgrade: python db_repository/manage.py upgrade
worker: celery -A app.celery worker
