from django.utils.timezone import now
from django.db import models
from datetime import timedelta


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
    nome = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    assento = models.ForeignKey(Assento, on_delete=models.CASCADE)

    # Valor e status da compra
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    status = models.CharField(max_length=20, default="pendente")  # pendente | pago | cancelado
    reservado_ate = models.DateTimeField(default=default_reserva)
    pago = models.BooleanField(default=False)

    # Identificador da cobrança PIX (txid único da Efí)
    txid = models.CharField(max_length=100, blank=True, null=True)

    # 🔑 Campos de PIX
    pix_qrcode = models.ImageField(upload_to="pix", blank=True, null=True)
    pix_copia_cola = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome} - {self.assento.nome} ({self.status})"


class Configuracao(models.Model):
    valor_ingresso = models.DecimalField(max_digits=8, decimal_places=2, default=50.00)

    def __str__(self):
        return f"Configuração (Valor atual: R$ {self.valor_ingresso})"


