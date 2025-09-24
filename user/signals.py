from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.apps import apps


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

def _delete_files(instance):
    """Remove arquivos de todos os campos ImageField do objeto."""
    for field in instance._meta.get_fields():
        if field.get_internal_type() == "ImageField":
            file = getattr(instance, field.name)
            if file and file.storage.exists(file.name):
                file.delete(save=False)


@receiver(post_delete, sender=Client)
@receiver(post_delete, sender=Artist)
def delete_files_on_delete(sender, instance, **kwargs):
    _delete_files(instance)


@receiver(pre_save, sender=Client)
@receiver(pre_save, sender=Artist)
def delete_old_files_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    for field in instance._meta.get_fields():
        if field.get_internal_type() == "ImageField":
            old_file = getattr(old_instance, field.name)
            new_file = getattr(instance, field.name)
            if old_file and old_file != new_file and old_file.storage.exists(old_file.name):
                old_file.delete(save=False)
