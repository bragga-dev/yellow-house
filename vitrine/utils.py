# utils.py
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import logging

logger = logging.getLogger(__name__)

def ensure_default_media():
    base_path = os.path.join(os.path.dirname(__file__), "default_media")

    for filename in os.listdir(base_path):
        local_path = os.path.join(base_path, filename)
        key = f"default/{filename}"
        logger.info(f"Uploading {key}")

        if not default_storage.exists(key):
            with open(local_path, "rb") as f:
                default_storage.save(key, ContentFile(f.read()))
