from django.urls import path
from . import views

urlpatterns = [
    path('extraction_ussd_osn/', views.extraction_ussd_osn, name='extraction_ussd_osn'),

    path('insert_extract_ussd_osn/', views.insert_extract_ussd_osn, name='insert_extract_ussd_osn'),
 
    path('export_ussd_osn_fiable/', views.export_ussd_osn_fiable, name='export_ussd_osn_fiable'),

    path('update_ussd_osn_tmp/', views.update_ussd_osn_tmp, name='update_ussd_osn_tmp'),
    path('update_ussd_osn/', views.update_ussd_osn, name='update_ussd_osn'),
    path('supprimer_ussd_osn_data/', views.supprimer_ussd_osn_data, name='supprimer_ussd_osn_data'),
]