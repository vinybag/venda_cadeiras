from django.urls import path
from . import views

urlpatterns = [
    path("", views.mapa_assentos, name="mapa_assentos"),
    path("assento/<int:pk>/", views.detalhe_assento, name="detalhe_assento"),
    path("pagamento/<int:compra_id>/", views.pagina_pagamento, name="pagina_pagamento"),
    path("pagamento/<int:compra_id>/confirmar/", views.confirmar_pagamento, name="confirmar_pagamento"),  # NOVA
    path("ingresso/<int:compra_id>/", views.ingresso, name="ingresso"),  # NOVA (página de sucesso)
    path("cancelar/<int:compra_id>/", views.cancelar_reserva, name="cancelar_reserva"),
    path("pagamento/<int:compra_id>/pix/", views.pagamento_pix, name="pagamento_pix"),
    path("ingresso/<int:compra_id>/download/", views.baixar_ingresso, name="baixar_ingresso"),
    path("validar/<int:compra_id>/", views.validar_ingresso, name="validar_ingresso"),
    path("check-assentos/", views.check_assentos, name="check_assentos"),
    path("verificar-status/<int:compra_id>/", views.verificar_status_pagamento, name="verificar_status"),
    path("webhook/pix", views.webhook_pix, name="webhook_pix"),
]