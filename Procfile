web: cd backend && python manage.py migrate && gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT
worker: cd backend && celery -A backend worker --loglevel=info 