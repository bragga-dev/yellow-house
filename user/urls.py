# user/urls.py

from django.urls import path
from .views import update_profile_artist, create_address, update_address, ClientSignupView, ArtistSignupView


urlpatterns = [

    path('signup/client/', ClientSignupView.as_view(), name='account_signup_client'),
    path('signup/artist/', ArtistSignupView.as_view(), name='account_signup_artist'),
    path('<slug:slug>/<uuid:pk>/', update_profile_artist, name='update_profile'),
    path('create_address/', create_address, name='create_address'),
    path('update_address/<slug:slug>/<uuid:pk>/', update_address, name='update_address'),
]
    