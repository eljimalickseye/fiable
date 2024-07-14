from django.urls import path
from . import views

urlpatterns = [
    path('extraction_ams/', views.extraction_ams, name='extraction_ams'),
    path('export_ams_disabled/', views.export_ams_disabled, name='export_ams_disabled'),
    path('export_ams_actif/', views.export_ams_actif, name='export_ams_actif'),
    path('insert_extract_ams/', views.insert_extract_ams, name='insert_extract_ams'),
 
    path('update_ams_tmp/', views.update_ams_tmp, name='update_ams_tmp'),
    path('update_ams/', views.update_ams, name='update_ams'),
    path('supprimer_ams_data/', views.supprimer_ams_data, name='supprimer_ams_data'),

    path('export_data_to_csv/', views.export_data_to_csv, name='export_data_to_csv'),
    path('export_tmp_ams/', views.export_tmp_ams, name='export_tmp_ams'),
    path('export_desc_ams/', views.export_desc_ams, name='export_desc_ams'),
    path('export_ams_fiable/', views.export_ams_fiable, name='export_ams_fiable')
]