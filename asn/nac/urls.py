from django.urls import path
from . import views

urlpatterns = [
    path('extraction_nac/', views.extraction_nac, name='extraction_nac'),
    path('export_nac_disabled/', views.export_nac_disabled, name='export_nac_disabled'),
    path('export_nac_actif/', views.export_nac_actif, name='export_nac_actif'),
    path('insert_extract_nac/', views.insert_extract_nac, name='insert_extract_nac'),
 
    path('update_NAC_tmp/', views.update_NAC_tmp, name='update_NAC_tmp'),
    path('update_nac/', views.update_nac, name='update_nac'),
    path('supprimer_nac_data/', views.supprimer_nac_data, name='supprimer_nac_data'),

    path('export_data_to_csv/', views.export_data_to_csv, name='export_data_to_csv'),
    path('export_tmp_nac/', views.export_tmp_nac, name='export_tmp_nac'),
    path('export_desc_nac/', views.export_desc_nac, name='export_desc_nac'),
    path('export_nac_fiable/', views.export_nac_fiable, name='export_nac_fiable'),
    path('update_test_nac/', views.update_test_nac, name='update_test_nac'),
]