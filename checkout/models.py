# checkout_app/models.py
from django.db import models
from django.conf import settings
from vitrine.models import ArtWork, Souvenir
from user.models import User
import uuid
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, verbose_name=_("Usuário"), on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = _("Carrinho")
        verbose_name_plural = _("Carrinhos")

    def __str__(self):
        return f"Carrinho {self.id} - {self.user}"

    def calculate_total_price(self):
        total = sum(item.subtotal() for item in self.items.all())
        return total

    def save(self, *args, **kwargs):
        if self.pk:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    artwork = models.ForeignKey(ArtWork, verbose_name=_('Obra'), null=True, blank=True, on_delete=models.CASCADE)
    souvenir = models.ForeignKey(Souvenir, verbose_name=_('Souvenir'), null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

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
        return self.unit_price * self.quantity
