import json
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from PIL import Image
from django.http import HttpRequest, HttpResponse
from datetime import timedelta
from django.utils.timezone import now
from .models import Assento, Compra, Configuracao
from .forms import CompraForm
from .utils_pix import gerar_pix
from .utils_ingresso import gerar_pdf_ingresso
from django.http import FileResponse, Http404, JsonResponse
from django.core.management import call_command
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST


def mapa_assentos(request: HttpRequest) -> HttpResponse:
    # limpar reservas vencidas
    Compra.objects.filter(status="pendente", reservado_ate__lt=now()).update(status="cancelado")

    # 🔥 se não houver assentos no banco, carrega do fixture
    if Assento.objects.count() == 0:
        try:
            call_command("loaddata", "ingressos/fixtures/assentos_completos.json")
        except Exception as e:
            print("⚠️ Erro ao carregar assentos:", e)

    largura_exibida: int = 800
    img_path = os.path.join(settings.BASE_DIR, 'ingressos', 'static', 'ingressos', 'MAPA.png')

    with Image.open(img_path) as img:
        largura_original = img.width
        escala = largura_exibida / largura_original

    assentos = []
    for assento_obj in Assento.objects.all():
        coords = [int(float(x) * escala) for x in assento_obj.coords.split(',')]

        if len(coords) == 4:
            x1, y1, x2, y2 = coords
            if abs(x2 - x1) < 20:
                if x2 > x1:
                    x2 = x1 + 20
                else:
                    x1 = x2 + 20
            if abs(y2 - y1) < 20:
                if y2 > y1:
                    y2 = y1 + 20
                else:
                    y1 = y2 + 20
            coords = [x1, y1, x2, y2]

        assentos.append({
            'pk': assento_obj.pk,
            'nome': assento_obj.nome,
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

    # valor atual do ingresso
    config = Configuracao.objects.first()
    valor_ingresso = config.valor_ingresso if config else 50.00

    # já existe uma reserva válida?
    reserva_existente = assento.compra_set.filter(status="pendente", reservado_ate__gt=now()).first()
    if reserva_existente:
        compra = reserva_existente
    else:
        # cria a reserva imediatamente com o valor atual
        compra = Compra.objects.create(
            assento=assento,
            nome="",
            email="",
            whatsapp="",
            status="pendente",
            reservado_ate=now() + timedelta(minutes=10),
            valor=valor_ingresso  # 👈 aqui salva o valor
        )

    if request.method == "POST":
        compra.nome = request.POST.get("nome")
        compra.email = request.POST.get("email")
        compra.whatsapp = request.POST.get("whatsapp")
        compra.save()
        return redirect("pagina_pagamento", compra_id=compra.id)

    return render(request, "ingressos/detalhe_assento.html", {
        "assento": assento,
        "compra": compra,
        "valor_ingresso": compra.valor  # sempre o valor salvo
    })


def pagina_pagamento(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id)

    if not hasattr(compra, "reservado_ate") or not compra.reservado_ate:
        compra.reservado_ate = compra.criado_em + timedelta(minutes=10)
        compra.save()

    return render(request, "ingressos/pagina_pagamento.html", {"compra": compra})


def confirmar_pagamento(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id)

    if request.method != "POST":
        return redirect("pagina_pagamento", compra_id=compra.id)

    if compra.reservado_ate and compra.reservado_ate < now():
        compra.status = "cancelado"
        compra.save()
        return redirect("mapa_assentos")

    if compra.status == "pago":
        return redirect("ingresso", compra_id=compra.id)
    if compra.status == "cancelado":
        return redirect("mapa_assentos")

    compra.status = "pago"
    compra.save()

    pdf_path = gerar_pdf_ingresso(compra)

    return redirect("ingresso", compra_id=compra.id)


def ingresso(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id)

    if compra.status != "pago":
        if compra.reservado_ate and compra.reservado_ate < now():
            compra.status = "cancelado"
            compra.save()
            return redirect("mapa_assentos")
        return redirect("pagina_pagamento", compra_id=compra.id)

    context = {"compra": compra, "MEDIA_URL": settings.MEDIA_URL}
    return render(request, "ingressos/ingresso.html", context)


def cancelar_reserva(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id, status="pendente")
    compra.status = "cancelado"
    compra.save()
    return redirect("mapa_assentos")


def pagina_pix(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id)

    if not compra.pix_copia_cola:
        gerar_pix(compra)

    return render(request, "ingressos/pagina_pix.html", {"compra": compra})


def pagamento_pix(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id)

    if compra.reservado_ate and compra.reservado_ate < now():
        compra.status = "cancelado"
        compra.save()
        return redirect("mapa_assentos")

    if not compra.pix_qrcode or not compra.pix_copia_cola:
        dados_pix = gerar_pix(compra)
        compra.pix_qrcode.save(f"pix_{compra.id}.png", dados_pix["qrcode"])
        compra.pix_copia_cola = dados_pix["copia_cola"]
        compra.save()

    context = {"compra": compra}
    return render(request, "ingressos/pagamento_pix.html", context)


def baixar_ingresso(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id)

    if compra.status != "pago":
        return redirect("pagina_pagamento", compra_id=compra.id)

    pdf_path = os.path.join(settings.MEDIA_ROOT, f"ingresso_{compra.id}.pdf")

    if not os.path.exists(pdf_path):
        from .utils_ingresso import gerar_pdf_ingresso
        pdf_path = gerar_pdf_ingresso(compra)

    return FileResponse(open(pdf_path, "rb"), as_attachment=True, filename=f"ingresso_{compra.id}.pdf")


def validar_ingresso(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id)

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

def verificar_status_pagamento(request, compra_id):
    compra = Compra.objects.get(id=compra_id)
    return JsonResponse({"status": compra.status})

@csrf_exempt  # porque o banco não manda CSRF
@require_POST
def webhook_pix(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        pix_list = data.get("pix", [])

        for pix in pix_list:
            txid = pix.get("txid")
            if txid and txid.startswith("compra"):
                compra_id = txid.replace("compra", "")
                try:
                    compra = Compra.objects.get(id=compra_id)
                    compra.status = "pago"
                    compra.save()
                    gerar_pdf_ingresso(compra)  # já gera o ingresso
                except Compra.DoesNotExist:
                    print(f"⚠️ Compra não encontrada para txid={txid}")
        return JsonResponse({"status": "ok"})
    except Exception as e:
        print("❌ Erro no webhook PIX:", str(e))
        return JsonResponse({"status": "erro"}, status=400)





