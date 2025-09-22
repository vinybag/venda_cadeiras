#!/usr/bin/env bash
# render-build.sh

# Interrompe em caso de erro
set -o errexit  

echo "===> Instalando dependências"
pip install -r requirements.txt

echo "===> Rodando collectstatic"
python manage.py collectstatic --noinput

echo "===> Rodando migrations"
python manage.py migrate --noinput

echo "===> Carregando assentos"
python manage.py loaddata venda_cadeiras/assentos_completos.json || true