from django.core.management.base import BaseCommand
from django.utils import timezone
from ingressos.models import Compra
from ingressos.efipay_client import get_efipay_instance
import datetime

class Command(BaseCommand):
    help = "Verifica pagamentos PIX na Efí e atualiza status das compras"

    def handle(self, *args, **options):
        efipay = get_efipay_instance()

        # Pega as últimas 24h (ajuste se quiser maior intervalo)
        inicio = (timezone.now() - datetime.timedelta(days=1)).isoformat()
        fim = (timezone.now() + datetime.timedelta(minutes=5)).isoformat()

        params = {"inicio": inicio, "fim": fim}

        try:
            response = efipay.pix_list_received(params=params)
            pagamentos = response.get("pix", [])

            for pagamento in pagamentos:
                txid = pagamento.get("txid")
                valor = pagamento.get("valor", {}).get("original")
                status = pagamento.get("status")

                try:
                    compra = Compra.objects.get(txid=txid)
                    if status == "CONCLUIDA" and compra.status != "paga":
                        compra.status = "paga"
                        compra.save()
                        self.stdout.write(self.style.SUCCESS(
                            f"✅ Compra {compra.id} confirmada (valor {valor})"
                        ))
                except Compra.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f"⚠️ PIX recebido sem compra associada (txid {txid})"
                    ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao consultar PIX: {e}"))
