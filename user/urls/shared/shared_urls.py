from django.urls import path
from user.views.shared.create_accounts import ClientSignupView, ArtistSignupView
from user.views.shared.profile_redirect import (profile_redirect)
from user.views.shared.add_address import update_address, delete_address, create_address


app_name = 'shared'

urlpatterns = [
    path('signup/client/', ClientSignupView.as_view(), name='account_signup_client'),
    path('signup/artist/', ArtistSignupView.as_view(), name='account_signup_artist'),
    path('create_address/', create_address, name='create_address'),
    path('update_address/<uuid:pk>/', update_address, name='update_address'),
    path('delete_address/<uuid:pk>/', delete_address, name='delete_address'),
    path('<slug:slug>/<uuid:pk>/', profile_redirect, name='profile_redirect'),  # último da lista
]
