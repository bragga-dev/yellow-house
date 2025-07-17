from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.apps import apps


Client = apps.get_model('user', 'Client')
Artist = apps.get_model('user', 'Artist')


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
