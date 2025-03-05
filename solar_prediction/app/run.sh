#!/bin/sh

source /opt/venv/bin/activate
echo "Starting Hasp Add-on..."
python3 -m flask db init
python3 -m flask db migrate
python3 -m flask db upgrade
nginx -g 'daemon off;' & redis-server & celery -A make_celery worker --loglevel=info & python3 app.py

