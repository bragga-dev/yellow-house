from django.urls import path
from user.views.shared.create_accounts import ClientSignupView, ArtistSignupView
from user.views.shared.profile_redirect import (profile_redirect)
from user.views.shared.add_address import add_address

urlpatterns = [
    path('signup/client/', ClientSignupView.as_view(), name='account_signup_client'),
    path('signup/artist/', ArtistSignupView.as_view(), name='account_signup_artist'),
    path('<slug:slug>/<uuid:pk>/', profile_redirect, name='update_profile'),
    path('add_address/', add_address, name='add_address'),
]
