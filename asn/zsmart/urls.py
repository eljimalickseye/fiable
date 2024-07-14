from django.urls import path
from . import views

urlpatterns = [
    path('extraction_zsmart/', views.extraction_zsmart, name='extraction_zsmart'),
    path('export_zsmart_disabled/', views.export_zsmart_disabled, name='export_zsmart_disabled'),
    path('export_zsmart_actif/', views.export_zsmart_actif, name='export_zsmart_actif'),
    path('insert_extract_zsmart/', views.insert_extract_zsmart, name='insert_extract_zsmart'),
 
    path('update_zsmart_tmp/', views.update_zsmart_tmp, name='update_zsmart_tmp'),
    path('update_zsmart/', views.update_zsmart, name='update_zsmart'),
    path('supprimer_zsmart_data/', views.supprimer_zsmart_data, name='supprimer_zsmart_data'),

    path('export_data_to_csv/', views.export_data_to_csv, name='export_data_to_csv'),
    path('export_tmp_zsmart/', views.export_tmp_zsmart, name='export_tmp_zsmart'),
    path('export_desc_zsmart/', views.export_desc_zsmart, name='export_desc_zsmart'),
    path('export_zsmart_fiable/', views.export_zsmart_fiable, name='export_zsmart_fiable'),

    path('fiabilisation_zsmart/', views.fiabilisation_zsmart, name='fiabilisation_zsmart')
]