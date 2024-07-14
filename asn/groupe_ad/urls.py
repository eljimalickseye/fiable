from django.urls import path
from . import views

urlpatterns = [
    path('groupe_ad/', views.groupe_ad, name='groupe_ad'),

    path('insert_extract_groupe_ad/', views.insert_extract_groupe_ad, name='insert_extract_groupe_ad'),
 
    path('export_groupe_ad_fiable/', views.export_groupe_ad_fiable, name='export_groupe_ad_fiable'),

    path('update_groupe_ad_tmp/', views.update_groupe_ad_tmp, name='update_groupe_ad_tmp'),
    path('update_groupe_ad/', views.update_groupe_ad, name='update_groupe_ad'),
    path('supprimer_groupe_ad_data/', views.supprimer_groupe_ad_data, name='supprimer_groupe_ad_data'),
    path('export_tmp_groupe_ad_csv/', views.export_tmp_groupe_ad_csv, name='export_tmp_groupe_ad_csv'),  
]