from casa_amarela.settings.base import *
from decouple import config

DEBUG = False
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')]) + ['_']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

# Segurança
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True
X_FRAME_OPTIONS = 'DENY'


STATIC_ROOT = '/vol/static'
MEDIA_ROOT = '/vol/media'

# Configurações MinIO - CORRIGIDAS
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'minio')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'minio123') 
AWS_STORAGE_BUCKET_NAME = 'media'
AWS_S3_ENDPOINT_URL = 'http://minio:9000'
AWS_S3_USE_SSL = False

# DOMÍNIO CORRETO para acesso externo
AWS_S3_CUSTOM_DOMAIN = '3.145.213.53:9000'
AWS_QUERYSTRING_AUTH = False
AWS_DEFAULT_ACL = 'public-read'

# Storage configuration
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f"http://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STORAGE_BUCKET_NAME}/"
