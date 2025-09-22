import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from efipay import EfiPay


def gerar_pix(compra):
    credentials = {
        "client_id": settings.EFI_CLIENT_ID,
        "client_secret": settings.EFI_CLIENT_SECRET,
        "certificate": str(settings.EFI_CERT_PATH),
        "sandbox": True,  # coloque False em produção
    }

    efipay = EfiPay(credentials)

    txid = f"compra{compra.id}"

    body = {
        "calendario": {"expiracao": 600},
        "devedor": {
            "cpf": "12345678909",  # exemplo, pode trocar por email/telefone
            "nome": compra.nome,
        },
        "valor": {"original": "50.00"},  # aqui idealmente você usa compra.valor
        "chave": settings.EFI_PIX_KEY,
        "solicitacaoPagador": f"Pagamento do assento {compra.assento.nome}",
    }

    # Criar cobrança PIX imediata
    response = efipay.pix_create_immediate_charge(params={"txid": txid}, body=body)

    # Gerar QR Code baseado na cobrança
    qrcode_response = efipay.pix_generate_qrcode(params={"id": response["loc"]["id"]})

    copia_cola = qrcode_response["qrcode"]

    # Criar imagem QR Code
    qr = qrcode.make(copia_cola)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    return {
        "qrcode": ContentFile(buffer.getvalue(), name=f"pix_{compra.id}.png"),
        "copia_cola": copia_cola,
    }
