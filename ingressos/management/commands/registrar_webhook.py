from django.core.management.base import BaseCommand
from django.conf import settings
from ingressos.utils_pix import get_efipay_instance

class Command(BaseCommand):
    help = "Registra/atualiza o webhook PIX na Efí"

    def handle(self, *args, **options):
        efipay = get_efipay_instance()

        params = {"chave": settings.EFI_PIX_KEY}
        body = {"webhookUrl": "https://venda-cadeiras.onrender.com/webhook/pix/"}

        try:
            resp = efipay.pix_config_webhook(params=params, body=body)
            self.stdout.write(self.style.SUCCESS(f"✅ Webhook configurado: {resp}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Falha ao registrar webhook: {e}"))


