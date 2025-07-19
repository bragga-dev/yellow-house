from django.urls import path, include

urlpatterns = [
    path('artist/', include('user.urls.artist.artist_urls')),
    path('client/', include('user.urls.client.client_urls')),
    path('shared/', include('user.urls.shared.shared_urls')),
]
