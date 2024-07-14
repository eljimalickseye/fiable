from django.urls import path
from . import views

urlpatterns = [
    path('extraction_pretups/', views.extraction_pretups, name='extraction_pretups'),
    path('insert_pretups/', views.insert_pretups, name='insert_pretups'),
    path('supprimer_pretups_data/', views.supprimer_pretups_data, name='supprimer_pretups_data'),
    path('export_pretups_fiable/', views.export_pretups_fiable, name='export_pretups_fiable'),
]