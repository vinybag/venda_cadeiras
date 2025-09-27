# ingressos/utils_pix.py
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from .efipay_client import get_efipay_instance


def gerar_pix(compra):
    efipay = get_efipay_instance()

    # 🔑 Gera um identificador único para a cobrança
    txid = f"compra{compra.id}"
    compra.txid = txid
    compra.save(update_fields=["txid"])  # ✅ salva no banco

    valor = str(compra.valor) if hasattr(compra, "valor") else "50.00"

    body = {
        "calendario": {"expiracao": 600},  # expira em 10 minutos
        "devedor": {
            "cpf": "12345678909",  # ⚠️ fictício (só se for obrigatório)
            "nome": compra.nome or "Cliente",
        },
        "valor": {"original": valor},
        "chave": settings.EFI_PIX_KEY,  # sua chave PIX cadastrada na Efí
        "solicitacaoPagador": f"Pagamento do assento {compra.assento.nome}",
    }

    try:
        # cria cobrança imediata
        response = efipay.pix_create_immediate_charge(
            params={"txid": txid},
            body=body
        )

        # gera o QR Code a partir da cobrança
        try:
            qrcode_response = efipay.pix_generate_qrcode(
                params={"id": response["loc"]["id"]}
            )
            if not isinstance(qrcode_response, dict):
                raise Exception(f"Resposta inesperada no QRCode: {qrcode_response}")
        except Exception as e:
            print("❌ Erro no QRCode Efí:", str(e))
            raise

        copia_cola = qrcode_response["qrcode"]

        # cria QR code em imagem PNG
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







