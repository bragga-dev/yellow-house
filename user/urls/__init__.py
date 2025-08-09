from django.urls import path, include

urlpatterns = [
    path('artist/', include(('user.urls.artist.artist_urls', 'artist'), namespace='artist')),
    path('client/', include(('user.urls.client.client_urls', 'client'), namespace='client')),
    path('shared/', include(('user.urls.shared.shared_urls', 'shared'), namespace='shared')),

]
