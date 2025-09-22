#!/usr/bin/env bash
# Fail on error
set -o errexit  

echo "===> Rodando collectstatic"
python manage.py collectstatic --noinput

echo "===> Rodando migrations"
python manage.py migrate --noinput
