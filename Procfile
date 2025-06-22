web: cd backend && python manage.py migrate && python manage.py runserver 0.0.0.0:$PORT
worker: cd backend && celery -A backend worker --loglevel=info 