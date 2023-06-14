#!/bin/bash
# service cron restart

python3 script/init_notification_template.py

python3 manage.py migrate

python3 manage.py runserver 0.0.0.0:8000

