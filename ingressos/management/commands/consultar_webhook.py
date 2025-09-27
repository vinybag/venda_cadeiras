# ingressos/management/commands/consultar_webhook.py
from django.core.management.base import BaseCommand
from django.conf import settings
from ingressos.efipay_client import get_efipay_instance

class Command(BaseCommand):
    help = "Consulta o webhook PIX configurado na Efí para a chave Pix"

    def handle(self, *args, **options):
        efipay = get_efipay_instance()
        params = {"chave": settings.EFI_PIX_KEY}

        try:
            resp = efipay.pix_detail_webhook(params=params)
            self.stdout.write(self.style.SUCCESS(f"✅ Webhook encontrado: {resp}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao consultar webhook: {e}"))
