#!/usr/bin/env bash
# aborta se der erro
set -o errexit  

echo "=== Rodando collectstatic ==="
python manage.py collectstatic --noinput

echo "=== Rodando migrations ==="
python manage.py migrate --noinput

echo "=== Carregando assentos ==="
python manage.py loaddata assentos_completos.json || true
