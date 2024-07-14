from django.urls import path
from . import views

urlpatterns = [
    path('extraction_naf/', views.extraction_naf, name='extraction_naf'),
    path('export_naf_disabled/', views.export_naf_disabled, name='export_naf_disabled'),
    path('export_naf_actif/', views.export_naf_actif, name='export_naf_actif'),
    path('insert_extract_naf/', views.insert_extract_naf, name='insert_extract_naf'),
 
    path('update_NAf_tmp/', views.update_NAf_tmp, name='update_NAf_tmp'),
    path('update_naf/', views.update_naf, name='update_naf'),
    path('supprimer_naf_data/', views.supprimer_naf_data, name='supprimer_naf_data'),

    path('export_data_to_csv/', views.export_data_to_csv, name='export_data_to_csv'),
    path('export_tmp_naf/', views.export_tmp_naf, name='export_tmp_naf'),
    path('export_desc_naf/', views.export_desc_naf, name='export_desc_naf'),
    path('export_naf_fiable/', views.export_naf_fiable, name='export_naf_fiable'),
    
    
]