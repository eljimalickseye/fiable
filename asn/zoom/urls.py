from django.urls import path
from . import views

urlpatterns = [
    path('extraction_zoom/', views.extraction_zoom, name='extraction_zoom'),
    path('export_zoom_disabled/', views.export_zoom_disabled, name='export_zoom_disabled'),
    path('export_zoom_actif/', views.export_zoom_actif, name='export_zoom_actif'),
    path('insert_extract_zoom/', views.insert_extract_zoom, name='insert_extract_zoom'),
 
    path('update_zoom_tmp/', views.update_zoom_tmp, name='update_zoom_tmp'),
    path('update_zoom/', views.update_zoom, name='update_zoom'),
    path('supprimer_zoom_data/', views.supprimer_zoom_data, name='supprimer_zoom_data'),

    path('export_data_to_csv/', views.export_data_to_csv, name='export_data_to_csv'),
    path('export_tmp_zoom/', views.export_tmp_zoom, name='export_tmp_zoom'),
    path('export_desc_zoom/', views.export_desc_zoom, name='export_desc_zoom'),
    path('export_zoom_fiable/', views.export_zoom_fiable, name='export_zoom_fiable'),
    path('export_tmp_zoom_csv/', views.export_tmp_zoom_csv, name='export_tmp_zoom_csv'),   
]
