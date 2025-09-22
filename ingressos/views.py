import json
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from PIL import Image
from django.http import HttpRequest, HttpResponse
from datetime import timedelta
from django.utils.timezone import now
from .models import Assento, Compra
from .forms import CompraForm
from .utils_pix import gerar_pix
from .utils_ingresso import gerar_pdf_ingresso
from django.http import FileResponse, Http404
from django.http import JsonResponse


def mapa_assentos(request: HttpRequest) -> HttpResponse:
    # limpar reservas vencidas
    Compra.objects.filter(status="pendente", reservado_ate__lt=now()).update(status="cancelado")

    json_path = os.path.join(settings.BASE_DIR, 'assentos_completos.json')

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    largura_exibida: int = 800
    img_path = os.path.join(settings.BASE_DIR, 'ingressos', 'static', 'ingressos', 'MAPA.png')

    with Image.open(img_path) as img:
        largura_original = img.width
        escala = largura_exibida / largura_original

    assentos = []
    for item in data:
        fields = item['fields']
        assento_obj = Assento.objects.get(pk=item['pk'])

        # escala das coordenadas
        coords = [int(float(x) * escala) for x in fields['coords'].split(',')]

        # 👇 garante que rect tenha tamanho mínimo
        if len(coords) == 4:
            x1, y1, x2, y2 = coords
            # largura mínima
            if abs(x2 - x1) < 20:
                if x2 > x1:
                    x2 = x1 + 20
                else:
                    x1 = x2 + 20
            # altura mínima
            if abs(y2 - y1) < 20:
                if y2 > y1:
                    y2 = y1 + 20
                else:
                    y1 = y2 + 20
            coords = [x1, y1, x2, y2]

        assentos.append({
            'pk': item['pk'],
            'nome': fields['nome'],
            'coords_esc': ','.join(map(str, coords)),
            'ocupado': assento_obj.ocupado,
        })

    context = {
        'assentos': assentos,
        'largura_exibida': largura_exibida
    }

    return render(request, 'ingressos/mapa_assentos.html', context)


def detalhe_assento(request, pk):
    assento = get_object_or_404(Assento, pk=pk)

    # já existe uma reserva válida?
    reserva_existente = assento.compra_set.filter(status="pendente", reservado_ate__gt=now()).first()
    if reserva_existente:
        compra = reserva_existente
    else:
        # cria a reserva imediatamente
        compra = Compra.objects.create(
            assento=assento,
            nome="",  # ainda não informado
            email="",
            whatsapp="",
            status="pendente",
            reservado_ate=now() + timedelta(minutes=10)
        )

    if request.method == "POST":
        compra.nome = request.POST.get("nome")
        compra.email = request.POST.get("email")
        compra.whatsapp = request.POST.get("whatsapp")
        compra.save()

        return redirect("pagina_pagamento", compra_id=compra.id)

    return render(request, "ingressos/detalhe_assento.html", {
        "assento": assento,
        "compra": compra
    })



def pagina_pagamento(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id)

    if not hasattr(compra, "reservado_ate") or not compra.reservado_ate:
        compra.reservado_ate = compra.criado_em + timedelta(minutes=10)
        compra.save()

    return render(request, "ingressos/pagina_pagamento.html", {"compra": compra})

def confirmar_pagamento(request, compra_id):
    """Confirma o pagamento e gera o ingresso em PDF"""
    compra = get_object_or_404(Compra, pk=compra_id)

    # Se não for POST, volta para a página de pagamento
    if request.method != "POST":
        return redirect("pagina_pagamento", compra_id=compra.id)

    # Se a reserva expirou, cancela
    if compra.reservado_ate and compra.reservado_ate < now():
        compra.status = "cancelado"
        compra.save()
        return redirect("mapa_assentos")

    # Se já estiver pago ou cancelado
    if compra.status == "pago":
        return redirect("ingresso", compra_id=compra.id)
    if compra.status == "cancelado":
        return redirect("mapa_assentos")

    # ✅ Confirma pagamento
    compra.status = "pago"
    compra.save()

    # ✅ Gera o ingresso em PDF
    pdf_path = gerar_pdf_ingresso(compra)

    # (Opcional) se quiser salvar o caminho no banco:
    # compra.pdf_path = pdf_path
    # compra.save()

    return redirect("ingresso", compra_id=compra.id)


def ingresso(request, compra_id):
    """Página de confirmação / sucesso após pagamento."""
    compra = get_object_or_404(Compra, pk=compra_id)

    # Se não estiver paga, volta para pagamento (ou mapa se expirou)
    if compra.status != "pago":
        if compra.reservado_ate and compra.reservado_ate < now():
            compra.status = "cancelado"
            compra.save()
            return redirect("mapa_assentos")
        return redirect("pagina_pagamento", compra_id=compra.id)

    context = {
        "compra": compra,
        "MEDIA_URL": settings.MEDIA_URL,  # 👈 adiciona isso no contexto
    }

    return render(request, "ingressos/ingresso.html", context)

def cancelar_reserva(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id, status="pendente")
    compra.status = "cancelado"
    compra.save()
    return redirect("mapa_assentos")

def pagina_pix(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id)

    # Gera QRCode se ainda não tiver
    if not compra.pix_copia_cola:
        gerar_pix(compra)

    return render(request, "ingressos/pagina_pix.html", {"compra": compra})

def pagamento_pix(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id)

    # Se a reserva expirou, cancela e volta ao mapa
    if compra.reservado_ate and compra.reservado_ate < now():
        compra.status = "cancelado"
        compra.save()
        return redirect("mapa_assentos")

    # Se ainda não gerou PIX, gera agora
    if not compra.pix_qrcode or not compra.pix_copia_cola:
        dados_pix = gerar_pix(compra)
        compra.pix_qrcode.save(f"pix_{compra.id}.png", dados_pix["qrcode"])
        compra.pix_copia_cola = dados_pix["copia_cola"]
        compra.save()

    context = {
        "compra": compra,
    }
    return render(request, "ingressos/pagamento_pix.html", context)

def baixar_ingresso(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id)

    # garante que só pode baixar se estiver pago
    if compra.status != "pago":
        return redirect("pagina_pagamento", compra_id=compra.id)

    pdf_path = os.path.join(settings.MEDIA_ROOT, f"ingresso_{compra.id}.pdf")

    if not os.path.exists(pdf_path):
        # se não existir, gera de novo
        from .utils_ingresso import gerar_pdf_ingresso
        pdf_path = gerar_pdf_ingresso(compra)

    return FileResponse(open(pdf_path, "rb"), as_attachment=True, filename=f"ingresso_{compra.id}.pdf")

def validar_ingresso(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id)

    # Se o ingresso não estiver pago, é inválido
    if compra.status != "pago":
        return render(request, "ingressos/validacao.html", {
            "valido": False,
            "mensagem": "Ingresso inválido ou não pago."
        })

    return render(request, "ingressos/validacao.html", {
        "valido": True,
        "compra": compra,
        "mensagem": f"Ingresso válido! Assento: {compra.assento.nome}"
    })

def check_assentos(request):
    return JsonResponse({"total_assentos": Assento.objects.count()})




