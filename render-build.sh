#!/usr/bin/env bash
# render-build.sh

set -o errexit  

echo "=== Rodando migrações ==="
python manage.py migrate --noinput

echo "=== Coletando arquivos estáticos ==="
python manage.py collectstatic --noinput

echo "=== Carregando assentos do fixture ==="
if [ -f "ingressos/fixtures/assentos_completos.json" ]; then
  python manage.py loaddata ingressos/fixtures/assentos_completos.json || \
  echo "⚠️ Nenhum assento carregado (eles podem já existir no banco)"
else
  echo "⚠️ Arquivo de assentos não encontrado, pulando loaddata"
fi

echo "=== Importando superusuário ==="
python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); User.objects.filter(is_superuser=True).delete()" || \
echo "⚠️ Nenhum usuário para remover"
python manage.py loaddata ingressos/fixtures/superuser.json || \
echo "⚠️ Nenhum superusuário importado"

echo "=== Registrando webhook PIX ==="
python manage.py registrar_webhook || \
echo "⚠️ Falha ao registrar webhook, continuar mesmo assim"

echo "=== Consultando webhook PIX configurado ==="
python manage.py consultar_webhook || \
echo "⚠️ Não foi possível consultar webhook"

echo "=== Build finalizado com sucesso ==="






