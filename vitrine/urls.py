from django.urls import path
from vitrine.views.index_views import index
from vitrine.views.artwork_views import create_artwork, update_artwork, delete_artwork




app_name = 'vitrine'

urlpatterns = [
    path('', index, name='index'),

    path('create-artwork/', create_artwork, name='create_artwork'),
    path('update-artwork/<slug:slug>/<uuid:artwork_id>/', update_artwork, name='update_artwork'),
    path('delete-artwork/<slug:slug>/<uuid:artwork_id>/', delete_artwork, name='delete_artwork'),


]
