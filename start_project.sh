#!/bin/bash

# Setup Procedure
# chmod +x start_project.sh
# ./start_project.sh

source myenv/bin/activate
redis-server --daemonize yes
celery -A animalwellness worker --loglevel=info &
celery -A animalwellness beat --loglevel=info &
daphne -b 0.0.0.0 -p 8001 animalwellness.asgi:application &
python manage.py runserver
