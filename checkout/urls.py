
from django.urls import path
from checkout.views.cart_views import add_item_in_cart, cart_detail, \
update_item_quantity, remove_item_from_cart, update_shipping

from checkout.views.webhook_views import mercadopago_webhook

from checkout.views.checkout_views import create_checkout, checkout_view

from checkout.views.payments_views import create_pix_payment,pix_payment_view, payment_success

app_name = "checkout"


urlpatterns = [
   # Cart
   path('add_item_in_cart/<slug:slug>/<uuid:item_id>/', add_item_in_cart, name='add_item_in_cart'),
   path('cart_detail/', cart_detail, name='cart_detail'),
   path('update_item_quantity/<uuid:item_id>/', update_item_quantity, name='update_item_quantity'),
   path('remove_item_from_cart/<uuid:item_id>/', remove_item_from_cart, name='remove_item_from_cart'),
   path('update_shipping/<uuid:item_id>/', update_shipping, name='update_shipping'),


   # Checkout
    path('', checkout_view, name='checkout'),
   path('create/', create_checkout, name='create_checkout'),
    
    # Pagamentos PIX
    path('pix/create/', create_pix_payment, name='create_pix_payment'),
    path('pix/<uuid:order_id>/', pix_payment_view, name='pix_payment'),
    path('success/', payment_success, name='payment_success'),

   # Webhook
   path('webhook/mercadopago/', mercadopago_webhook, name='mercadopago_webhook'),
    
]

