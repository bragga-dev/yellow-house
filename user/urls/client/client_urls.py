from django.urls import path
from user.views.client.update_profile_client import update_profile_client


urlpatterns = [
    path('<slug:slug>/<uuid:pk>/client/', update_profile_client, name='update_profile_client'),

]
