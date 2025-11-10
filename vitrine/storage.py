from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
from urllib.parse import urlparse


class S3MediaStorage(S3Boto3Storage):
    default_acl = "public-read"
    file_overwrite = False

    def __init__(self, *args, **kwargs):
        kwargs["bucket_name"] = settings.AWS_STORAGE_BUCKET_NAME
        kwargs["endpoint_url"] = settings.AWS_S3_ENDPOINT_URL
        kwargs["region_name"] = None
        super().__init__(*args, **kwargs)

        if not settings.DEBUG:
            # Produção → usa o domínio público / Nginx
            self._base_url = f"http://{settings.AWS_S3_CUSTOM_DOMAIN}/media"
        else:
            # Desenvolvimento → acessa direto o MinIO local
            parsed = urlparse(settings.MINIO_ACCESS_URL)
            self._base_url = f"http://{parsed.netloc}/{settings.AWS_STORAGE_BUCKET_NAME}"

    def url(self, name):
        return f"{self._base_url}/{name.lstrip('/')}"
