# checkout_app/models.py
from django.db import models
from django.conf import settings
from vitrine.models import ArtWork, Souvenir
from user.models import User
import uuid
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, verbose_name=_("Usuário"), on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = _("Carrinho")
        verbose_name_plural = _("Carrinhos")

    def __str__(self):
        return f"Carrinho {self.id} - {self.user}"

    def calculate_total_price(self):
        # Soma apenas os produtos
        return sum(item.subtotal() for item in self.items.all())

    def calculate_total_shipping(self):
        return sum((item.shipping_value or Decimal('0.00')) for item in self.items.all())


    def update_totals(self):
        self.total_price = self.calculate_total_price()
        self.total_shipping = self.calculate_total_shipping()
        self.save(update_fields=['total_price', 'total_shipping'])

    @property
    def total_geral(self):
        return self.total_price + self.total_shipping


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    artwork = models.ForeignKey(ArtWork, verbose_name=_('Obra'), null=True, blank=True, on_delete=models.CASCADE)
    souvenir = models.ForeignKey(Souvenir, verbose_name=_('Souvenir'), null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_type = models.CharField(max_length=255, null=True, blank=True)
    shipping_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = _("Item do carrinho")
        verbose_name_plural = _("Itens do carrinho")
    def clean(self):
        if not self.artwork and not self.souvenir:
            raise ValidationError("O item deve estar vinculado a uma obra ou a um souvenir.")

    def save(self, *args, **kwargs):
        if not self.unit_price:
            if self.artwork:
                self.unit_price = self.artwork.price
            elif self.souvenir:
                self.unit_price = self.souvenir.price
        super().save(*args, **kwargs)

    def __str__(self):
        if self.artwork:
            return f"{self.quantity} x {self.artwork.name}"
        elif self.souvenir:
            return f"{self.quantity} x {self.souvenir.name}"
        return f"Item {self.id}"

    def subtotal(self):
        return (self.unit_price * self.quantity).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)





class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, verbose_name=_("Usuário"), on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, verbose_name=_("Carrinho"), on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Pedido")
        verbose_name_plural = _("Pedidos")

    def __str__(self):
        return f"Pedido {self.id} - {self.user}"


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_id = models.CharField(max_length=11)
    action = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.data_id + " - " + self.date_created.strftime("%d/%m/%Y %H:%M:%S")


class Payments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, verbose_name=_("Usuário"), on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, verbose_name=_("Carrinho"), on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=11)
    date_approved = models.DateTimeField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_of_expiration = models.DateTimeField(null=True, blank=True)
    date_last_updated = models.DateTimeField(null=True, blank=True)
    payment_method_id = models.CharField(max_length=10)
    status = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return self.user.email + " - " + self.payment_id + " - " + self.status