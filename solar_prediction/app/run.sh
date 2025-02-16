#!/bin/sh

source venv/bin/activate
echo "Starting Hasp Add-on..."

redis-server & celery -A app.celery worker --loglevel=info & python3 app.py
