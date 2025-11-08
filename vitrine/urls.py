from django.urls import path
from vitrine.views.index_views import index, artworks_partial, souvenirs_partial, search_results
from vitrine.views.artwork_views import create_artwork, update_artwork, delete_artwork, detail_artwork, list_artworks_by_artist, list_artworks
from vitrine.views.souvenir_views import list_souvenirs, souvenir_detail
from vitrine.views.on_views import on_view
from vitrine.views.blog_views import blog_list, blog_detail
from vitrine.views.frenet_views import calcular_frete


app_name = 'vitrine'

urlpatterns = [
    
    # home
    path('', index, name='index'),
    path('partials/artworks/', artworks_partial, name='artworks_partial'),
    path('partials/souvenirs/', souvenirs_partial, name='souvenirs_partial'),

    #sobre
    path('sobre/', on_view, name='on_view'),

    #frete
    path('frete/', calcular_frete, name='calcular_frete'),

    #blog
    path('blog/', blog_list, name='blog_list'),
    path('blog/<slug:slug>/<uuid:blog_id>/', blog_detail, name='blog_detail'),

    # search bar
    path('search/', search_results, name='search_results'),

    # artworks
    path('create-artwork/', create_artwork, name='create_artwork'),
    path('update-artwork/<slug:slug>/<uuid:artwork_id>/', update_artwork, name='update_artwork'),
    path('delete-artwork/<slug:slug>/<uuid:artwork_id>/', delete_artwork, name='delete_artwork'),
    path('artworks/<slug:slug>/<uuid:pk>/', list_artworks_by_artist, name='list_artworks'),
    path('artwork/<slug:slug>/<uuid:artwork_id>/', detail_artwork, name='detail_artwork'),
    path('artworks/', list_artworks, name='list_artworks'),

    # souvenirs
    path('souvenirs/', list_souvenirs, name='list_souvenirs'),
    path('souvenir/<slug:slug>/<uuid:souvenir_id>/', souvenir_detail, name='souvenir_detail'),


]
