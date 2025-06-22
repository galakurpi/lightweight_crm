#!/bin/bash
# Install Python dependencies
pip install -r requirements.txt

# Navigate to backend directory and collect static files
cd backend
python manage.py collectstatic --noinput

echo "Build completed successfully!" 