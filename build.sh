#!/bin/bash
# Install Python dependencies
pip install -r requirements.txt

# Collect static files (manage.py is in root directory)
python manage.py collectstatic --noinput

echo "Build completed successfully!" 