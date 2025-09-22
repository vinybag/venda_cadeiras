#!/usr/bin/env bash
# render-build.sh

echo "=== Rodando collectstatic ==="
python manage.py collectstatic --noinput

echo "=== Rodando migrations ==="
python manage.py migrate --noinput

echo "=== Carregando assentos ==="
python manage.py loaddata assentos_completos.json || echo "Fixture não encontrada"
