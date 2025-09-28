
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import logging
from django.utils.text import slugify



logger = logging.getLogger(__name__)
# Ensure default media files are present in storage
def ensure_default_media():
    base_path = os.path.join(os.path.dirname(__file__), "default_media")

    for filename in os.listdir(base_path):
        local_path = os.path.join(base_path, filename)
        key = f"default/{filename}"
        logger.info(f"Uploading {key}")

        if not default_storage.exists(key):
            with open(local_path, "rb") as f:
                default_storage.save(key, ContentFile(f.read()))



# Slug generation utility
def generate_unique_slug(instance, *args):
    field_value = "-".join(str(arg) for arg in args if arg)
    base_slug = slugify(field_value, allow_unicode=True)
    
    unique_slug = base_slug
    num = 1
    Klass = instance.__class__
    
    while Klass.objects.filter(slug=unique_slug).exists():
        unique_slug = f"{base_slug}-{num}"
        num += 1

    return unique_slug
