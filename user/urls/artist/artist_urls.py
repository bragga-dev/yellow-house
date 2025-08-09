from django.urls import path
from user.views.artist.update_profile_artist import update_profile_artist
from user.views.artist.dashboard_artist import dashboard_artist

app_name = 'artist'


urlpatterns = [
    path('<slug:slug>/<uuid:pk>/artist/', update_profile_artist, name='update_profile_artist'),
    path('<slug:slug>/<uuid:pk>/dashboard/', dashboard_artist, name='dashboard_artist'),
   
]
