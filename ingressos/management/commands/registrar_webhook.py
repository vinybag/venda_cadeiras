# ingressos/management/commands/registrar_webhook.py
from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import json
from requests.auth import HTTPBasicAuth


class Command(BaseCommand):
    help = "Registra/atualiza o webhook PIX na Efí (sem mTLS, com x-skip-mtls-checking)"

    def handle(self, *args, **options):
        try:
            # 1. Pega o token de acesso diretamente
            token_url = "https://pix.api.efipay.com.br/oauth/token"
            auth = HTTPBasicAuth(settings.EFI_CLIENT_ID, settings.EFI_CLIENT_SECRET)
            data = {"grant_type": "client_credentials"}

            cert = settings.EFI_CERT  # caminho do certificado .pem
            resp = requests.post(token_url, auth=auth, data=data, cert=cert)

            if resp.status_code != 200:
                self.stdout.write(self.style.ERROR(
                    f"❌ Falha ao obter token (status {resp.status_code}): {resp.text}"
                ))
                return

            access_token = resp.json().get("access_token")
            if not access_token:
                self.stdout.write(self.style.ERROR("❌ Token não retornado pela Efí"))
                return

            # 2. Monta URL e payload do webhook
            url = f"https://pix.api.efipay.com.br/v2/webhook/{settings.EFI_PIX_KEY}"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "x-skip-mtls-checking": "true",  # 👈 ignora mTLS
            }
            body = {
            "webhookUrl": "https://venda-cadeiras.onrender.com/webhook/pix?ignorar="
            }

            # 3. Faz a requisição PUT
            response = requests.put(url, headers=headers, data=json.dumps(body), cert=cert)

            if response.status_code in (200, 201):
                self.stdout.write(self.style.SUCCESS(f"✅ Webhook configurado: {response.json()}"))
            else:
                self.stdout.write(self.style.ERROR(
                    f"❌ Falha ao registrar webhook (status {response.status_code}): {response.text}"
                ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro inesperado: {e}"))





