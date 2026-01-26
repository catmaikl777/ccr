#!/usr/bin/env bash
pip install -r requirements.txt
cd CATVID
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py create_superuser_auto
