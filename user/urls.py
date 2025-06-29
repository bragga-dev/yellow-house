# user/urls.py

from django.urls import path
from .views import update_profile, create_address, update_address

urlpatterns = [
  
    path('<slug:slug>/<uuid:pk>/', update_profile, name='update_profile'),
    path('create_address/', create_address, name='create_address'),
    path('update_address/<slug:slug>/<uuid:pk>/', update_address, name='update_address'),
]
    