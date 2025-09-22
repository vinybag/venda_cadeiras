from django.utils.timezone import now
from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
from datetime import timedelta
from django.utils.timezone import now

def default_reserva():
    return now() + timedelta(minutes=10)

class Assento(models.Model):
    nome = models.CharField(max_length=100)
    coords = models.CharField(max_length=200)

    def __str__(self):
        return self.nome

    @property
    def ocupado(self):
        # Ocupado se já tiver compra paga
        if self.compra_set.filter(status="pago").exists():
            return True
        # ou se tiver reserva pendente ainda dentro do prazo
        if self.compra_set.filter(status="pendente", reservado_ate__gt=now()).exists():
            return True
        return False


class Compra(models.Model):
    assento = models.ForeignKey(Assento, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    whatsapp = models.CharField(max_length=20)
    criado_em = models.DateTimeField(default=now)
    reservado_ate = models.DateTimeField(default=default_reserva)
    status = models.CharField(
        max_length=20,
        choices=[("pendente", "Pendente"), ("pago", "Pago"), ("cancelado", "Cancelado")],
        default="pendente"
    )
    pix_qrcode = models.ImageField(upload_to="qrcodes", blank=True, null=True)
    pix_copia_cola = models.TextField(blank=True, null=True)