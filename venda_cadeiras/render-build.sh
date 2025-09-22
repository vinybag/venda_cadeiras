#!/usr/bin/env bash
# script de build para rodar no Render
set -o errexit  

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate
