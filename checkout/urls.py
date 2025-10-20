
from django.urls import path
from checkout.views.cart_views import add_item_in_cart, cart_detail, update_item_quantity, remove_item_from_cart

app_name = "checkout"


urlpatterns = [

   path('add_item_in_cart/<slug:slug>/<uuid:item_id>/', add_item_in_cart, name='add_item_in_cart'),
   path('cart_detail/', cart_detail, name='cart_detail'),
   path('update_item_quantity/<uuid:item_id>/', update_item_quantity, name='update_item_quantity'),
   path('remove_item_from_cart/<uuid:item_id>/', remove_item_from_cart, name='remove_item_from_cart'),
   
    
]

