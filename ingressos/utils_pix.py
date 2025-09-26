# ingressos/utils_pix.py
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings          # 👈 faltava isso
from .efipay_client import get_efipay_instance

def gerar_pix(compra):
    efipay = get_efipay_instance()
    txid = f"compra{compra.id}"
    valor = str(compra.valor) if hasattr(compra, "valor") else "50.00"

    body = {
        "calendario": {"expiracao": 600},
        "devedor": {
            "cpf": "12345678909",
            "nome": compra.nome or "Cliente",
        },
        "valor": {"original": valor},
        "chave": settings.EFI_PIX_KEY,  # ✅ agora vai funcionar
        "solicitacaoPagador": f"Pagamento do assento {compra.assento.nome}",
    }

    try:
        response = efipay.pix_create_immediate_charge(
            params={"txid": txid},
            body=body
        )
        qrcode_response = efipay.pix_generate_qrcode(
            params={"id": response["loc"]["id"]}
        )

        copia_cola = qrcode_response["qrcode"]

        qr = qrcode.make(copia_cola)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        return {
            "qrcode": ContentFile(buffer.getvalue(), name=f"pix_{compra.id}.png"),
            "copia_cola": copia_cola,
        }

    except Exception as e:
        print("❌ Erro ao gerar PIX:", str(e))
        raise





