from django.contrib import admin
from checkout.models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'total_shipping', 'total_geral')
    search_fields = ('user__username',)
    readonly_fields = ('total_price', 'total_shipping', 'total_geral')
    list_filter = ('user',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'artwork', 'souvenir', 'quantity', 'unit_price', 'shipping_type', 'shipping_value')
    search_fields = ('artwork__name', 'souvenir__name')
    list_filter = ('shipping_type',)
