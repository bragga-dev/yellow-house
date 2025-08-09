from django.urls import path
from user.views.client.update_profile_client import update_profile_client
from user.views.client.dashboard_client import dashboard_client

app_name = 'client'

urlpatterns = [
    path('<slug:slug>/<uuid:pk>/client/', update_profile_client, name='update_profile_client'),
    path('<slug:slug>/<uuid:pk>/dashboard/', dashboard_client, name='dashboard_client'),


]
