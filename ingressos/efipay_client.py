# ingressos/efipay_client.py
from django.conf import settings
from efipay import EfiPay

def get_efipay_instance():
    options = {
        "client_id": settings.EFI_CLIENT_ID,
        "client_secret": settings.EFI_CLIENT_SECRET,
        "sandbox": settings.EFI_SANDBOX,
        "certificate": settings.EFI_CERT,  # caminho para seu .pem
    }
    return EfiPay(options)

