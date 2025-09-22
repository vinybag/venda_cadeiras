#!/usr/bin/env bash
# render-build.sh

# Falhar em caso de erro
set -o errexit  

echo "=== Rodando migrações ==="
python manage.py migrate --noinput

echo "=== Coletando arquivos estáticos ==="
python manage.py collectstatic --noinput

echo "=== Carregando assentos do fixture ==="
python manage.py loaddata ingressos/fixtures/assentos_completos.json || echo "⚠️ Nenhum assento carregado (pode já existir)"

echo "=== Build finalizado com sucesso ==="

