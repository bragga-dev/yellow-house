


from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Cart
from user.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from checkout.models import CartItem


@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)




@receiver(post_save, sender=CartItem)
def update_cart_totals_on_save(sender, instance, **kwargs):
    instance.cart.update_totals()

@receiver(post_delete, sender=CartItem)
def update_cart_totals_on_delete(sender, instance, **kwargs):
    instance.cart.update_totals()



