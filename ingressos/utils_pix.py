import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from efipay import EfiPay
from .utils_pix import get_efipay_instance


def get_efipay_instance():
    credentials = {
        "client_id": settings.EFI_CLIENT_ID,
        "client_secret": settings.EFI_CLIENT_SECRET,
        "certificate": settings.EFI_CERT,   # agora é só uma string (caminho do .pem)
        "sandbox": settings.EFI_SANDBOX,
    }
    return EfiPay(credentials)



def gerar_pix(compra):
    """
    Cria uma cobrança PIX imediata para a compra e retorna o QRCode + copia e cola.
    """
    efipay = get_efipay_instance()

    txid = f"compra{compra.id}"

    # Valor definido na compra ou fallback
    valor = str(compra.valor) if hasattr(compra, "valor") else "50.00"

    body = {
        "calendario": {"expiracao": 600},
        "devedor": {
            "cpf": "12345678909",  # exemplo. Se não quiser coletar CPF, pode manter fixo
            "nome": compra.nome or "Cliente",
        },
        "valor": {"original": valor},
        "chave": settings.EFI_PIX_KEY,
        "solicitacaoPagador": f"Pagamento do assento {compra.assento.nome}",
    }

    try:
        # Criar cobrança PIX imediata
        response = efipay.pix_create_immediate_charge(
            params={"txid": txid}, body=body
        )

        # Gerar QR Code baseado na cobrança
        qrcode_response = efipay.pix_generate_qrcode(
            params={"id": response["loc"]["id"]}
        )

        copia_cola = qrcode_response["qrcode"]

        # Criar imagem QR Code
        qr = qrcode.make(copia_cola)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        return {
            "qrcode": ContentFile(buffer.getvalue(), name=f"pix_{compra.id}.png"),
            "copia_cola": copia_cola,
        }

    except Exception as e:
        # log no console (Render mostra no log)
        print("❌ Erro ao gerar PIX:", str(e))
        raise


