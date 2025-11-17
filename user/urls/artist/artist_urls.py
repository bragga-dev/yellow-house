from django.urls import path
from user.views.artist.update_profile_artist import update_profile_artist
from user.views.artist.dashboard_artist import dashboard_artist
from user.views.artist.artists_list import artists_list
from user.views.artist.artist_detail import artist_detail
from user.views.artist.demote_to_client import demote_to_client
from user.views.artist.collection import collection, create_exhibition, update_exhibition, delete_exhibition, exhibition_detail, artworks_partial, exhibitions_partial

app_name = 'artist'


urlpatterns = [

    # profile update
    path('<slug:slug>/<uuid:pk>/update/', update_profile_artist, name='update_profile_artist'),

    # collection and exhibitions
    path('<slug:slug>/<uuid:pk>/collection/', collection, name='collection'),
    path('create_exhibition/', create_exhibition, name='create_exhibition'),
    path('update_exhibition/<slug:slug>/<uuid:exhibition_id>/', update_exhibition, name='update_exhibition'),
    path('delete_exhibition/<slug:slug>/<uuid:exhibition_id>/', delete_exhibition, name='delete_exhibition'),
    path('exhibition/<slug:slug>/<uuid:exhibition_id>/', exhibition_detail, name='exhibition_detail'),

    # dashboard and detail
    path('<slug:slug>/<uuid:pk>/dashboard/', dashboard_artist, name='dashboard_artist'),
    path('<slug:slug>/<uuid:pk>/detail/', artist_detail, name='artist_detail'),
    path('<slug:slug>/<uuid:pk>/demote/', demote_to_client, name='demote_to_client'),

    # list of artists
    path('artists/', artists_list, name='artists_list'),


    # partials
    path('<slug:slug>/<uuid:pk>/artworks/', artworks_partial, name='artworks_partial'),
    path('<slug:slug>/<uuid:pk>/exhibitions/', exhibitions_partial, name='exhibitions_partial'),
   
]
