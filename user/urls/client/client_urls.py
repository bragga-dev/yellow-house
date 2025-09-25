from django.urls import path
from user.views.client.update_profile_client import update_profile_client
from user.views.client.dashboard_client import dashboard_client
from user.views.client.promote_to_artist import promote_to_artist


app_name = 'client'

urlpatterns = [
    path('<slug:slug>/<uuid:pk>/client/', update_profile_client, name='update_profile_client'),
    path('<slug:slug>/<uuid:pk>/dashboard/', dashboard_client, name='dashboard_client'),
    path('<slug:slug>/<uuid:pk>/promote/', promote_to_artist, name='promote_to_artist'),


]
