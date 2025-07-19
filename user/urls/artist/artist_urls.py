from django.urls import path
from user.views.artist.update_profile_artist import update_profile_artist


urlpatterns = [
    path('<slug:slug>/<uuid:pk>/artist/', update_profile_artist, name='update_profile_artist'),
   
]
