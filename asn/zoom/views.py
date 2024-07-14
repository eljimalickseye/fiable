from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from openpyxl import Workbook
from django.db import connection
import mysql.connector
from django.apps import apps
from django.db.models import Q
from .models import Extraction_zoom

from core.models import  AdMPReport, TemporaireDRH
from core.views import export_gnoc,update_from_adm,update_from_temporaireDRH,export_tmp,export_desc,export_all

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import xlrd
from django.http import HttpResponse
import csv
from django.db import connection
import mysql.connector
import pandas as pd
from .forms import Upload
import re
from django.utils import timezone
from dateutil import parser
from datetime import date
from django.db import transaction
from django.db import IntegrityError

# zoom modele


def extraction_zoom(request):
    # Récupérer tous les enregistrements
    zoom_records = Extraction_zoom.objects.all()

    # Pagination
    paginator = Paginator(zoom_records, 100)  # 10 enregistrements par page
    page_number = request.GET.get('page')
    try:
        zoom_records = paginator.page(page_number)
    except PageNotAnInteger:
        # Si le numéro de page n'est pas un entier, afficher la première page
        zoom_records = paginator.page(1)
    except EmptyPage:
        # Si la page est vide, afficher la dernière page
        zoom_records = paginator.page(paginator.num_pages)

    # Mettre en forme les enregistrements pour les inclure dans le contexte
    all_zoom_records = []
    for zoom_record in zoom_records:
        all_zoom_records.append({
            'id': zoom_record.id,
            'username': zoom_record.username,
            'commentaire': zoom_record.commentaire,
        })
 

    context = {
        'all_zoom_records': all_zoom_records,
    }
    

    # Rendre la page d'accueil avec le contexte et les enregistrements paginés
    return render(request, 'zoom_extract.html', {**context ,'zoom_records': zoom_records})


def inserer_extract_zoom_data(donnees):
    try:
        for index, row in donnees.iterrows():
            # Gérer les valeurs NaN
            row = row.where(pd.notnull(row), None)
            
            # Créer une nouvelle instance du modèle Extraction_zoom
            extraction = Extraction_zoom(
                created_at=timezone.now(),
                username=row['username']
            )
            extraction.save()  # Enregistrer l'instance dans la base de données
            
            # Voir si le nom existe
            if row['username']:
                comment = "MAJ non effectue"
            else:
                comment = "A supprimer"
                
            # Mettre à jour le commentaire dans l'instance du modèle
            extraction.commentaire = comment
            extraction.save()  # Enregistrer la mise à jour dans la base de données
        
        print("Données insérées avec succès.")
    except Exception as e:
        raise e

def insert_extract_zoom(request):
    if request.method == 'POST' and request.FILES.get('file'):
        form = Upload(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            if file.name.endswith('.xls') or file.name.endswith('.xlsx'):
                try:
                    donnees = pd.read_excel(file, engine='openpyxl')
                except Exception as e:
                    return HttpResponse("Erreur lors de la lecture du fichier Excel : {}".format(e))
            elif file.name.endswith('.csv'):
                try:
                    donnees = pd.read_csv(file, encoding='utf-8')
                except Exception as e:
                    return HttpResponse("Erreur lors de la lecture du fichier CSV : {}".format(e))
            else:
                return HttpResponse("Le fichier doit être au format Excel ou CSV.")
            
            try:
                with transaction.atomic():
                    inserer_extract_zoom_data(donnees)
            except Exception as e:
                return HttpResponse("Une erreur s'est produite lors de l'insertion des données : {}".format(e))
            return redirect('extraction_zoom')
    else:
        form = Upload()
    return render(request, 'extract_zoom.html', {'form': form})


def supprimer_zoom_data(request):
    # Supprimer toutes les données de votre modèle
    Extraction_zoom.objects.all().delete()

    return redirect('extraction_zoom')


def get_unique_ids():
    """
    Récupère les identifiants uniques à partir de la base de données SQL.
    Returns:
        Un ensemble d'identifiants uniques.
    """
    unique_ids = set()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id
            FROM zoom_extraction_zoom
            WHERE commentaire != 'A garder'
        """)
        records_sql = cursor.fetchall()

        for record_sql in records_sql:
            unique_ids.add(record_sql[0])

    return unique_ids

def get_records_to_delete():
    """
    Récupère les enregistrements à supprimer depuis la base de données Django.
    Returns:
        QuerySet d'enregistrements à supprimer.
    """
    return Extraction_zoom.objects.exclude(commentaire='A garder')

def export_zoom_disabled(request):
    # Créez un nouveau classeur Excel
    wb = Workbook()
    # Sélectionnez la première feuille de calcul (feuille active par défaut)
    ws = wb.active

    # Définissez le nom du fichier Excel dans l'en-tête de la réponse HTTP
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="zoom_delete_profile.xlsx"'

    # Obtenez les enregistrements à exporter
    unique_ids = get_unique_ids()
    records_to_delete = get_records_to_delete()

    # Écrivez les en-têtes dans la première ligne
    headers = ['ID', 'username', 'commentaire']
    ws.append(headers)

    # Parcourez les enregistrements et écrivez-les dans le fichier Excel
    for record_id in unique_ids:
        for record_django in records_to_delete:
            if record_django.id == record_id:
                # Supprimez les informations de fuseau horaire des dates/heure
                password_update_date = record_django.PasswordUpdateDate.replace(tzinfo=None) if record_django.PasswordUpdateDate else None
                record = [record_django.id, record_django.username, record_django.commentaire]
                ws.append(record)
                break

    # Sauvegardez le classeur Excel dans la réponse HTTP
    wb.save(response)

    return response

def export_zoom_actif(request):
    # Créez un nouveau classeur Excel
    wb = Workbook()
    # Sélectionnez la première feuille de calcul (feuille active par défaut)
    ws = wb.active

    # Définissez le nom du fichier Excel dans l'en-tête de la réponse HTTP
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="records_zoom_actifs.xlsx"'

    # Récupérer les enregistrements actifs depuis la base de données Django
    records_actifs = Extraction_zoom.objects.filter(commentaire='A garder').values_list('id', 'username', 'commentaire')

    # Écrire les en-têtes dans la première ligne
    headers = ['ID', 'username', 'commentaire']
    ws.append(headers)

    # Écrire les enregistrements dans le fichier Excel
    for record in records_actifs:
        # Supprimez les informations de fuseau horaire des dates/heure
        password_update_date = record[7].replace(tzinfo=None) if record[7] else None
        record = list(record)
        record[7] = password_update_date
        ws.append(record)

    # Sauvegardez le classeur Excel dans la réponse HTTP
    wb.save(response)

    return response




def update_zoom(request):
    # Appeler la fonction pour mettre à jour les zoom depuis Adm

    extraction_model='Extraction_zoom'
    name_field='username'
    app_label='zoom'

    update_from_adm(request,extraction_model, name_field, app_label)

    return redirect("extraction_zoom")


def update_extraction_from_temporaireDRH():
    # Récupérer tous les enregistrements du modèle extraction
    extraction_records = Extraction_zoom.objects.filter(
        Name__istartswith="tmp"
    ) | Extraction_zoom.objects.filter(
        Name__istartswith="INT"
    )

    # Récupérer tous les noms des enregistrements du modèle TemporaireDRH
    temporaire_records = TemporaireDRH.objects.values_list('logon_name', flat=True)

    # Parcourir chaque enregistrement de extraction_records
    for extraction_record in extraction_records:
        Name = extraction_record.username
        commentaire = ""

        # Rechercher une correspondance partielle dans les noms des enregistrements TemporaireDRH avec un score supérieur ou égal à 80%
        match = process.extractOne(Name, temporaire_records, scorer=fuzz.partial_ratio, score_cutoff=90)

        if match:
            # Obtenez l'objet TemporaireDRH correspondant
            temporaire_record = TemporaireDRH.objects.get(logon_name=match[0])
            datefin = temporaire_record.datefin

            # Vérifier si la date de fin du contrat est dépassée
            if datefin < date.today():
                print(date.today())
                print(datefin)
                commentaire = "Fin de contrat, à supprimer"
            else:
                commentaire = "A garder"
        else:
            # Aucune correspondance trouvée
            commentaire = "À supprimer, non présent dans L'AD 2024"

        # Mettre à jour le commentaire dans l'enregistrement extraction
        extraction_record.commentaire = commentaire  
        extraction_record.save()
        

def update_zoom_tmp(request):
    # Appeler la fonction pour mettre à jour les zoom depuis Adm
    update_from_temporaireDRH(Extraction_zoom, 'username')

    return redirect("extraction_zoom")


def export_data_to_csv(request):
    # Définir les champs à exporter et leurs noms
    model_fields = ['created_at', 'username']
    
    custom_sql = "SELECT created_at, username FROM fiable.zoom_extraction_zoom WHERE Name REGEXP '[a-zA-Z]{4}[0-9]{4}'"


    # Appeler la fonction export_gnoc avec les paramètres appropriés
    response = export_gnoc(request, model_name='Extraction_zoom', model_fields=model_fields, custom_sql=custom_sql)

    return response

def export_tmp_zoom(request, model_name, model_fields, app_label, custom_sql=None):
    # Créer une réponse HTTP avec le type de contenu CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Fiable.csv"'

    # Récupérer le modèle spécifié à partir du nom du modèle
    model = apps.get_model(app_label, model_name=model_name)

    # Récupérer les enregistrements du modèle spécifié depuis la base de données Django
    records_django = model.objects.filter(
        Q(username__istartswith="tmp") |
        Q(username__istartswith="INT")
    )

    # Si une requête SQL personnalisée est fournie, exécutez-la pour récupérer les enregistrements
    if custom_sql:
        with connection.cursor() as cursor:
            cursor.execute(custom_sql)
            records_sql = cursor.fetchall()
    else:
        records_sql = []

    # Créer une liste pour stocker tous les enregistrements à écrire dans le fichier CSV
    records_to_write = []

    # Ajouter les enregistrements Django à la liste des enregistrements à écrire
    for record_django in records_django:
        records_to_write.append(record_django)

    # Ajouter les enregistrements SQL à la liste des enregistrements à écrire
    for record_sql in records_sql:
        records_to_write.append(record_sql)

    # Écrire les données dans le fichier CSV
    writer = csv.writer(response, delimiter=",")
    writer.writerow(model_fields)  # Écrire les en-têtes de colonne

    for record in records_to_write:
        if isinstance(record, model):
            # Si c'est une instance de modèle Django, extraire les valeurs des champs
            values = [getattr(record, field) for field in model_fields]
        else:
            # Sinon, c'est un tuple, utilisez-le directement
            values = record
        writer.writerow(values)

    return response

def export_tmp_zoom_csv(request):
    model_fields = ['username','commentaire']
    
    response=export_tmp_zoom(request, model_name='Extraction_zoom', model_fields=model_fields,app_label='zoom')
    
    return response


def export_desc_zoom(request):
    custom_sql = "SELECT created_at, username FROM fiable.zoom_extraction_zoom  WHERE (LOWER(username) LIKE 'pcci%' OR LOWER(username) LIKE 'stl%' OR LOWER(username) LIKE '1431%' OR LOWER(username) LIKE '1413%' OR LOWER(username) LIKE 'ksv%' OR LOWER(username) LIKE 'w2c%' OR LOWER(username) LIKE 'pop_%' OR LOWER(username) LIKE 'pdist%' OR LOWER(username) LIKE 'sitel%' OR LOWER(username) LIKE 'psup%')"
    model_fields = ['created_at', 'username','commentaire']
    model_name='Extraction_zoom'
    search_field='username'
    regex_pattern=r'^[a-zA-Z]{4}\d{4}$'
    
    response=export_desc(request, model_name=model_name, model_fields=model_fields,search_field=search_field, regex_pattern=regex_pattern,custom_sql=custom_sql,app_label='zoom')
    
    return response

def export_zoom_fiable(request):
    model_fields = ['username','commentaire']
    model_name='Extraction_zoom'

    response=export_all(request, model_name=model_name, model_fields=model_fields,app_label='zoom')
    
    return response


