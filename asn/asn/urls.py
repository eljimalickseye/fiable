from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('nac.urls')),
    path('', include('pretups.urls')),
    path('', include('naf.urls')),
    path('', include('nce.urls')),
    path('', include('ussd_osn.urls')),
    path('', include('zoom.urls')),
    path('', include('groupe_ad.urls')),
    path('', include('zsmart.urls')),
    path('', include('ams.urls')),
]