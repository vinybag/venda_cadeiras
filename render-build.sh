#!/usr/bin/env bash
# render-build.sh

# Se der qualquer erro, aborta o build
set -o errexit  

echo "=== Rodando migrações ==="
python manage.py migrate --noinput

echo "=== Coletando arquivos estáticos ==="
python manage.py collectstatic --noinput

echo "=== Carregando assentos do fixture ==="
# Tentamos carregar os assentos apenas se o arquivo existir
if [ -f "ingressos/fixtures/assentos_completos.json" ]; then
  python manage.py loaddata ingressos/fixtures/assentos_completos.json || \
  echo "⚠️ Nenhum assento carregado (eles podem já existir no banco)"
else
  echo "⚠️ Arquivo de assentos não encontrado, pulando loaddata"
fi

echo "=== Importando superusuário ==="
python manage.py loaddata superuser.json || echo "⚠️ Nenhum superusuário importado"

echo "=== Build finalizado com sucesso ==="


