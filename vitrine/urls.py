from django.urls import path
from vitrine.views.index_views import index
from vitrine.views.artwork_views import create_artwork




app_name = 'vitrine'

urlpatterns = [
    path('', index, name='index'),

    path('create-artwork/', create_artwork, name='create_artwork'),

]
