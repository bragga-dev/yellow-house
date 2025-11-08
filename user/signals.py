from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.apps import apps
from django.db import models


Client = apps.get_model('user', 'Client')
Artist = apps.get_model('user', 'Artist')


# -------------------------------
# Flags de usuário 
# -------------------------------

@receiver(post_save, sender=Client)
def set_user_is_client(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        user.is_client = True
        user.save(update_fields=['is_client'])

@receiver(post_delete, sender=Client)
def unset_user_is_client(sender, instance, **kwargs):
    user = instance.user
    user.is_client = False
    user.save(update_fields=['is_client'])

@receiver(post_save, sender=Artist)
def set_user_is_artist(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        user.is_artist = True
        user.save(update_fields=['is_artist'])

@receiver(post_delete, sender=Artist)
def unset_user_is_artist(sender, instance, **kwargs):
    user = instance.user
    user.is_artist = False
    user.save(update_fields=['is_artist'])



# -------------------------------
# Limpeza de arquivos de mídia
# -------------------------------
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from user.models import User, Artist



def is_default_file(file_field):
    """Retorna True se o arquivo estiver na pasta default/"""
    if not file_field:
        return False
    return file_field.name.startswith("default/")  # ignora qualquer arquivo dentro da pasta default

# --- User ---
@receiver(post_delete, sender=User)
def delete_user_photo_on_delete(sender, instance, **kwargs):
    if instance.photo and not is_default_file(instance.photo):
        instance.photo.delete(save=False)

@receiver(pre_save, sender=User)
def delete_user_photo_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).photo
    except sender.DoesNotExist:
        return False

    new_file = instance.photo
    if old_file and old_file != new_file and not is_default_file(old_file):
        old_file.delete(save=False)

# --- Artist ---
@receiver(post_delete, sender=Artist)
def delete_artist_banner_on_delete(sender, instance, **kwargs):
    if instance.banner and not is_default_file(instance.banner):
        instance.banner.delete(save=False)

@receiver(pre_save, sender=Artist)
def delete_artist_banner_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).banner
    except sender.DoesNotExist:
        return False

    new_file = instance.banner
    if old_file and old_file != new_file and not is_default_file(old_file):
        old_file.delete(save=False)


from django.db.models.signals import post_save
from django.dispatch import receiver
from user.models import User, Client

@receiver(post_save, sender=User)
def create_client_for_user(sender, instance, created, **kwargs):
    if created and instance.is_client and not hasattr(instance, 'client'):
        Client.objects.create(user=instance)
