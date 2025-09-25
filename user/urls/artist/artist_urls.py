from django.urls import path
from user.views.artist.update_profile_artist import update_profile_artist
from user.views.artist.dashboard_artist import dashboard_artist
from user.views.artist.artists_list import artists_list
from user.views.artist.artist_detail import artist_detail
from user.views.artist.demote_to_client import demote_to_client

app_name = 'artist'


urlpatterns = [
    path('<slug:slug>/<uuid:pk>/update/', update_profile_artist, name='update_profile_artist'),
    path('<slug:slug>/<uuid:pk>/dashboard/', dashboard_artist, name='dashboard_artist'),
    path('<slug:slug>/<uuid:pk>/detail/', artist_detail, name='artist_detail'),
    path('<slug:slug>/<uuid:pk>/demote/', demote_to_client, name='demote_to_client'),
    path('artists/', artists_list, name='artists_list'),
   
]
