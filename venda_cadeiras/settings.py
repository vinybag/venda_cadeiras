from pathlib import Path
import os
from urllib.parse import urlparse
import dj_database_url
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

# 🔑 Segurança
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "sua_chave_dev_aqui")
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"
ALLOWED_HOSTS = [
    "venda-cadeiras.onrender.com",
    "localhost",
    "127.0.0.1",
]

# Render define essa variável automaticamente → garante que hostname correto entra no ALLOWED_HOSTS
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")
if RENDER_EXTERNAL_URL:
    ALLOWED_HOSTS.append(urlparse(RENDER_EXTERNAL_URL).hostname)

# Sempre habilitado em produção no Render
CSRF_TRUSTED_ORIGINS = [
    "https://*.onrender.com",
]

# Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ingressos.apps.IngressosConfig',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # para servir staticfiles no Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'venda_cadeiras.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # pode deixar vazio
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'venda_cadeiras.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Se houver DATABASE_URL no ambiente (Render), usa ele
_db_url = os.environ.get("DATABASE_URL")
if _db_url:
    DATABASES["default"] = dj_database_url.parse(
        _db_url,
        conn_max_age=600,
        ssl_require=True,  # ✅ coloque True aqui
    )

# Validação de senha
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {"NAME": 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {"NAME": 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {"NAME": 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Arquivos estáticos e mídia
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuração Efí (Pix)
EFI_CLIENT_ID = os.getenv("EFI_CLIENT_ID", "Client_Id_bb96cf1730689c416ead140de33487918ac8a52e")
EFI_CLIENT_SECRET = os.getenv("EFI_CLIENT_SECRET", "Client_Secret_8a2fb8f04428a7150a6ee62661c913d5949d4436")
EFI_PIX_KEY = os.getenv("EFI_PIX_KEY", "544d62f5-c205-483a-9e98-9fd8e7dac63e")

# Caminho do certificado
EFI_CERT_PATH = os.getenv("EFI_CERT_PATH", str(BASE_DIR / "efipay.pem"))

# Logs no Render
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG" if DEBUG else "INFO",
    },
}





