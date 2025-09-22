import qrcode
from io import BytesIO
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from django.urls import reverse
import os


def gerar_pdf_ingresso(compra):
    """
    Gera um PDF com o ingresso contendo:
    - Imagem do evento
    - QR Code apontando para a validação do ingresso
    - Nome do assento
    """

    # Caminho para salvar o PDF
    output_path = os.path.join(settings.MEDIA_ROOT, f"ingresso_{compra.id}.pdf")

    # URL de validação do ingresso
    # 👉 durante desenvolvimento, use o localhost, em produção troque pelo domínio real
    url_validacao = f"http://127.0.0.1:8000{reverse('validar_ingresso', args=[compra.id])}"

    # QR Code apontando para a URL
    qr = qrcode.make(url_validacao)
    qr_buffer = BytesIO()
    qr.save(qr_buffer, format="PNG")

    # Criar PDF
    c = canvas.Canvas(output_path, pagesize=A4)
    largura, altura = A4

    # Adicionar imagem do evento (banner)
    banner_path = os.path.join(settings.BASE_DIR, "ingressos", "static", "ingressos", "evento_banner.png")
    if os.path.exists(banner_path):
        c.drawImage(banner_path, 2*cm, altura - 10*cm, width=16*cm, height=8*cm)

    # Adicionar QR Code
    qr_temp_path = os.path.join(settings.MEDIA_ROOT, f"qrcode_temp_{compra.id}.png")
    with open(qr_temp_path, "wb") as f:
        f.write(qr_buffer.getvalue())
    c.drawImage(qr_temp_path, 7*cm, altura/2 - 2*cm, width=6*cm, height=6*cm)

    # Texto abaixo do QR Code
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(largura/2, altura/2 - 3*cm, f"Assento: {compra.assento.nome}")

    # Finalizar
    c.showPage()
    c.save()

    # Remover QR temporário
    os.remove(qr_temp_path)

    return output_path
