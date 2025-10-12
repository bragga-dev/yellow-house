from django.apps import AppConfig
import logging



class VitrineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vitrine'

    def ready(self):
        from .utils import ensure_default_media
        try:
            ensure_default_media()
            logging.info("✅ Arquivos default garantidos no storage.")
        except Exception as e:
            logging.warning(f"⚠️ Não foi possível garantir arquivos default: {e}")


