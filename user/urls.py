from django.urls import path
from user.views.accounts_views.create_accounts import ClientSignupView, ArtistSignupView
from user.views.accounts_views.update_profile import (
    update_profile_artist,
    create_address,
    update_address,
    update_profile_redirect,
    update_profile_client,
    request_artist
)

urlpatterns = [
    path('signup/client/', ClientSignupView.as_view(), name='account_signup_client'),
    path('signup/artist/', ArtistSignupView.as_view(), name='account_signup_artist'),

    # ✅ Use apenas a view intermediária aqui
    path('<slug:slug>/<uuid:pk>/', update_profile_redirect, name='update_profile'),

    # ✅ Rotas específicas por tipo
    path('<slug:slug>/<uuid:pk>/artist/', update_profile_artist, name='update_profile_artist'),
    path('<slug:slug>/<uuid:pk>/client/', update_profile_client, name='update_profile_client'),

    path('create_address/', create_address, name='create_address'),
    path('update_address/<slug:slug>/<uuid:pk>/', update_address, name='update_address'),
]
