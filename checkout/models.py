# checkout_app/models.py
from django.db import models
from django.conf import settings
from vitrine.models import ArtWork, Souvenir
from user.models import User
import uuid
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from checkout.utils import generate_order_code, value_greater_than_zero

# ======================================================
# Carrinho
# ======================================================

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, verbose_name=_("Usuário"), on_delete=models.CASCADE)
    total_price = models.DecimalField(_("Subtotal"), max_digits=10, decimal_places=2, default=0)
    total_shipping = models.DecimalField(_("Preço total de frete"), max_digits=10, decimal_places=2, default=0)
    total_geral = models.DecimalField(_("Total geral"), max_digits=10, decimal_places=2, default=0)

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
        self.total_geral = self.total_price + self.total_shipping
        self.save(update_fields=['total_price', 'total_shipping', 'total_geral'])

    

# ======================================================
# Itens do Carrinho
# ======================================================

class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    artwork = models.ForeignKey(ArtWork, verbose_name=_('Obra'), null=True, blank=True, on_delete=models.CASCADE)
    souvenir = models.ForeignKey(Souvenir, verbose_name=_('Souvenir'), null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(_("Quantidade"), default=1, validators=[MinValueValidator(1)], null=False, blank=False)
    unit_price = models.DecimalField(_("Preço unitário"), max_digits=10, decimal_places=2, default=0)
    shipping_type = models.CharField(_("Tipo de frete"), max_length=255, null=True, blank=True)
    shipping_value = models.DecimalField(_("Preço unitário de frete"), max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = _("Item do carrinho")
        verbose_name_plural = _("Itens do carrinho")
    def clean(self):
        if not self.artwork and not self.souvenir:
            raise ValidationError("O item deve estar vinculado a uma obra ou a um souvenir.")
        value_greater_than_zero(self.quantity)

    def __str__(self):
        if self.artwork:
            return f"{self.quantity} x {self.artwork.name}"
        elif self.souvenir:
            return f"{self.quantity} x {self.souvenir.name}"
        return f"Item {self.id}"

    def subtotal(self):
        return (self.unit_price * self.quantity).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        

    def save(self, *args, **kwargs):
        if not self.unit_price:
            if self.artwork:
                self.unit_price = self.artwork.price
            elif self.souvenir:
                self.unit_price = self.souvenir.price
        self.full_clean()
        super().save(*args, **kwargs)




# ======================================================
#  Pedido
# ======================================================

class Order(models.Model):
    class OrderPaymentMethods(models.TextChoices):
        PIX = "pix", _("PIX")
        CARTAO = "cartão", _("Cartão")
        BOLETO = "boleto", _("Boleto")

    class Status(models.TextChoices):
        PENDING = "pending", _("Pendente")
        PROCESSING = "processing", _("Processando")
        COMPLETED = "completed", _("Completo")
        CANCELLED = "cancelled", _("Cancelado")
        REFUNDED = "refunded", _("Reembolsado")
        FAILED = "failed", _("Falhou")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_code = models.CharField(_("Código"), max_length=12, default=generate_order_code, editable=False, unique=True)
    order_status = models.CharField(_("Status"), max_length=15, choices=Status.choices, default=Status.PENDING)
    order_payment_method = models.CharField(_("Método de Pagamento"), max_length=10, choices=OrderPaymentMethods.choices)
    order_user = models.ForeignKey(User,   verbose_name=_("Usuário"), on_delete=models.CASCADE, related_name="orders")
    order_total_geral = models.DecimalField(_("Preço total"), max_digits=10, decimal_places=2, default=0)
    order_subtotal = models.DecimalField(_("Subtotal"), max_digits=10, decimal_places=2, default=0)
    order_shipping_total = models.DecimalField(_("Preço total de frete"), max_digits=10, decimal_places=2, default=0)
    order_date_created = models.DateTimeField(_("Data da compra"), auto_now_add=True)

    class Meta:
        verbose_name = _("Pedido")
        verbose_name_plural = _("Pedidos")
    
    def __str__(self):
        return f"Pedido {self.order_code} - {self.order_user.email}"


# ======================================================
# Itens do Pedido
# ======================================================

class OrderItem(models.Model):
    order = models.ForeignKey(Order,verbose_name=_("Pedido"), on_delete=models.CASCADE, related_name="order_item")
    order_item_quantity = models.PositiveIntegerField((_("Quantidade")), default=1, validators=[MinValueValidator(1)], null=False, blank=False)
    order_item_price = models.DecimalField(_("Preço unitário"), max_digits=10, decimal_places=2, default=0)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        verbose_name = _("Item do pedido")
        verbose_name_plural = _("Itens do pedido")

    def subtotal(self):
        return (self.order_item_price * self.order_item_quantity).quantize(Decimal("0.01"), ROUND_HALF_UP)

    def __str__(self):
        return f"{self.order_item_quantity} x {self.content_object}"


# ======================================================
# Pagamentos
# ======================================================

class Payment(models.Model):
    class PaymentMethods(models.TextChoices):
        PIX = "pix", _("PIX")
        CARTAO = "cartão", _("Cartão")
        BOLETO = "boleto", _("Boleto")

    class Status(models.TextChoices):
        PENDENTE = "pendente", _("Pendente")
        APROVADO = "aprovado", _("Aprovado")
        CANCELADO = "cancelado", _("Cancelado")
        REJEITADO = "rejeitado", _("Rejeitado")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payment")
    mp_payment_id = models.CharField(_("ID do Pagamento"), max_length=30)
    date_approved = models.DateTimeField(_("Data de Aprovação"), null=True, blank=True)
    date_created = models.DateTimeField(_("Data de Criação"), auto_now_add=True)
    date_of_expiration = models.DateTimeField(_("Data de Expiração"), null=True, blank=True)
    date_last_updated = models.DateTimeField(_("Data de Atualização"), null=True, blank=True)
    payment_method = models.CharField(_("Método de Pagamento"), max_length=30, choices=PaymentMethods.choices)
    payment_status = models.CharField(_("Status"), max_length=12, choices=Status.choices)
    payment_amount = models.DecimalField(_("Valor"), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("Pagamento")
        verbose_name_plural = _("Pagamentos")
        ordering = ["-date_created"]

    def __str__(self):
        return f"{self.payment_order.order_user.email} - {self.mp_payment_id} - {self.payment_status}"
