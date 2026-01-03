#!/bin/bash
pip install --upgrade pip
pip install -r requirements.txt
cd CATVID
python manage.py collectstatic --noinput
python manage.py migrate --noinput