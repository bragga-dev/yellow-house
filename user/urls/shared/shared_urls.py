from django.urls import path
from user.views.shared.create_accounts import ClientSignupView, ArtistSignupView
from user.views.shared.update_profile import (update_profile_redirect)

urlpatterns = [
    path('signup/client/', ClientSignupView.as_view(), name='account_signup_client'),
    path('signup/artist/', ArtistSignupView.as_view(), name='account_signup_artist'),
    path('<slug:slug>/<uuid:pk>/', update_profile_redirect, name='update_profile'),
]
