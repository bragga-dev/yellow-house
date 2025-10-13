from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from casa_amarela.settings import BASE_DIR
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('user/', include('user.urls')),
    path('', include('vitrine.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=os.path.join(BASE_DIR, 'media'))


handler404 = 'vitrine.views.error_views.custom_404'
handler500 = 'vitrine.views.error_views.custom_500'
