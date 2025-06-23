#!/bin/bash

# Run migrations
python manage.py migrate

# Start Celery worker in background
celery -A backend worker --loglevel=info --detach

# Start Django
exec gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT 