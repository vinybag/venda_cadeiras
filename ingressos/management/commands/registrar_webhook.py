from django.core.management.base import BaseCommand
from django.conf import settings
from efipay import EfiPay

class Command(BaseCommand):
    help = "Registra/atualiza o webhook PIX na Efí"

    def handle(self, *args, **options):
        credentials = {
            "client_id": settings.EFI_CLIENT_ID,
            "client_secret": settings.EFI_CLIENT_SECRET,
            "certificate": settings.EFI_CERT_PATH,
            "sandbox": False,
        }
        efipay = EfiPay(credentials)

        params = {"chave": settings.EFI_PIX_KEY}
        body = {"webhookUrl": "https://venda-cadeiras.onrender.com/webhook/pix/"}

        resp = efipay.pix_config_webhook(params=params, body=body)
        self.stdout.write(self.style.SUCCESS(f"Webhook configurado: {resp}"))
