from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from openpyxl import Workbook
from django.db import connection
import mysql.connector


from .models import Extraction_nac

from core.models import  AdMPReport, TemporaireDRH
from core.views import export_gnoc,update_from_adm,update_from_temporaireDRH,export_tmp,export_desc,export_all
from zoom.models import Extraction_zoom
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

# Nac modele


def extraction_nac(request):
    # Récupérer tous les enregistrements
    nac_records = Extraction_nac.objects.all()

    # Pagination
    paginator = Paginator(nac_records, 100)  # 10 enregistrements par page
    page_number = request.GET.get('page')
    try:
        nac_records = paginator.page(page_number)
    except PageNotAnInteger:
        # Si le numéro de page n'est pas un entier, afficher la première page
        nac_records = paginator.page(1)
    except EmptyPage:
        # Si la page est vide, afficher la dernière page
        nac_records = paginator.page(paginator.num_pages)

    # Mettre en forme les enregistrements pour les inclure dans le contexte
    all_nac_records = []
    for nac_record in nac_records:
        all_nac_records.append({
            'id': nac_record.id,
            'Name': nac_record.Name,
            'Password':nac_record.Password,
            'Profile':nac_record.Profile,
            'Locale':nac_record.Locale,
            'Description':nac_record.Description,
            'UserType':nac_record.UserType,
            'PasswordUpdateDate':nac_record.PasswordUpdateDate,
            'MailAddress':nac_record.MailAddress,
            'commentaire': nac_record.commentaire,
        })
 

    context = {
        'all_nac_records': all_nac_records,
    }
    

    # Rendre la page d'accueil avec le contexte et les enregistrements paginés
    return render(request, 'nac_extract.html', {**context ,'nac_records': nac_records})


def inserer_extract_nac_data(donnees):
    try:
        for index, row in donnees.iterrows():
            # Gérer les valeurs NaN
            row = row.where(pd.notnull(row), None)
            
            # Créer une nouvelle instance du modèle Extraction_nac
            extraction = Extraction_nac(
                created_at=timezone.now(),
                Name=row['Name'],
                Password=row['Password'],
                Profile=row['Profile'],
                Locale=row['Locale'],
                Description=row['Description'],
                UserType=row['UserType'],
                PasswordUpdateDate=row['PasswordUpdateDate'],
                MailAddress=row['MailAddress']
            )
            extraction.save()  # Enregistrer l'instance dans la base de données
            
            # Voir si le nom existe
            if row['Name']:
                comment = "MAJ non effectue"
            else:
                comment = "A supprimer"
                
            # Mettre à jour le commentaire dans l'instance du modèle
            extraction.commentaire = comment
            extraction.save()  # Enregistrer la mise à jour dans la base de données
        
        print("Données insérées avec succès.")
    except Exception as e:
        raise e

def insert_extract_nac(request):
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
                    inserer_extract_nac_data(donnees)
            except Exception as e:
                return HttpResponse("Une erreur s'est produite lors de l'insertion des données : {}".format(e))
            return redirect('extraction_nac')
    else:
        form = Upload()
    return render(request, 'extract_nac.html', {'form': form})


def supprimer_nac_data(request):
    # Supprimer toutes les données de votre modèle
    Extraction_nac.objects.all().delete()

    return redirect('extraction_nac')


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
            FROM nac_extraction_nac
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
    return Extraction_nac.objects.exclude(commentaire='A garder')

def export_nac_disabled(request):
    # Créez un nouveau classeur Excel
    wb = Workbook()
    # Sélectionnez la première feuille de calcul (feuille active par défaut)
    ws = wb.active

    # Définissez le nom du fichier Excel dans l'en-tête de la réponse HTTP
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="nac_delete_profile.xlsx"'

    # Obtenez les enregistrements à exporter
    unique_ids = get_unique_ids()
    records_to_delete = get_records_to_delete()

    # Écrivez les en-têtes dans la première ligne
    headers = ['ID', 'Name', 'Password', 'Profile', 'Locale', 'Description', 'UserType', 'PasswordUpdateDate', 'MailAddress', 'commentaire']
    ws.append(headers)

    # Parcourez les enregistrements et écrivez-les dans le fichier Excel
    for record_id in unique_ids:
        for record_django in records_to_delete:
            if record_django.id == record_id:
                # Supprimez les informations de fuseau horaire des dates/heure
                password_update_date = record_django.PasswordUpdateDate.replace(tzinfo=None) if record_django.PasswordUpdateDate else None
                record = [record_django.id, record_django.Name, record_django.Password, record_django.Profile, record_django.Locale, record_django.Description, record_django.UserType, password_update_date, record_django.MailAddress, record_django.commentaire]
                ws.append(record)
                break

    # Sauvegardez le classeur Excel dans la réponse HTTP
    wb.save(response)

    return response

def export_nac_actif(request):
    # Créez un nouveau classeur Excel
    wb = Workbook()
    # Sélectionnez la première feuille de calcul (feuille active par défaut)
    ws = wb.active

    # Définissez le nom du fichier Excel dans l'en-tête de la réponse HTTP
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="records_nac_actifs.xlsx"'

    # Récupérer les enregistrements actifs depuis la base de données Django
    records_actifs = Extraction_nac.objects.filter(commentaire='A garder').values_list('id', 'Name', 'Password', 'Profile', 'Locale', 'Description', 'UserType', 'PasswordUpdateDate', 'MailAddress', 'commentaire')

    # Écrire les en-têtes dans la première ligne
    headers = ['ID', 'Name', 'Password', 'Profile', 'Locale', 'Description', 'UserType', 'PasswordUpdateDate', 'MailAddress', 'commentaire']
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




def update_nac(request):
    # Appeler la fonction pour mettre à jour les nac depuis Adm

    extraction_model='Extraction_nac'
    name_field='Name'
    app_label='nac'

    update_from_adm(request,extraction_model, name_field, app_label)

    return redirect("extraction_nac")


def update_extraction_from_temporaireDRH():
    # Récupérer tous les enregistrements du modèle extraction
    extraction_records = Extraction_nac.objects.filter(
        Name__istartswith="tmp"
    ) | Extraction_nac.objects.filter(
        Name__istartswith="ext"
    ) | Extraction_nac.objects.filter(
        Name__istartswith="INT"
    )

    # Récupérer tous les noms des enregistrements du modèle TemporaireDRH
    temporaire_records = TemporaireDRH.objects.values_list('logon_name', flat=True)

    # Parcourir chaque enregistrement de extraction_records
    for extraction_record in extraction_records:
        Name = extraction_record.Name
        commentaire = ""

        # Rechercher une correspondance partielle dans les noms des enregistrements TemporaireDRH avec un score supérieur ou égal à 80%
        match = process.extractOne(Name, temporaire_records, scorer=fuzz.partial_ratio, score_cutoff=90)

        if match:
            # Obtenez l'objet TemporaireDRH correspondant
            temporaire_record = TemporaireDRH.objects.get(logon_name=match[0])
            datefin = temporaire_record.datefin

            # Vérifier si la date de fin du contrat est dépassée
            if datefin < date.today():
                commentaire = "Fin de contrat, à supprimer"
            else:
                commentaire = "A garder"
        else:
            # Aucune correspondance trouvée
            commentaire = "À supprimer, non présent dans L'AD 2024"

        # Mettre à jour le commentaire dans l'enregistrement extraction
        extraction_record.commentaire = commentaire  
        extraction_record.save()
        

def update_NAC_tmp(request):
    # Appeler la fonction pour mettre à jour les nac depuis Adm
    update_from_temporaireDRH(Extraction_nac, 'Name')

    return redirect("extraction_nac")


def export_data_to_csv(request):
    # Définir les champs à exporter et leurs noms
    model_fields = ['created_at', 'Name', 'Password', 'Profile', 'Locale', 'Description', 'UserType', 'PasswordUpdateDate', 'MailAddress']
    
    custom_sql = "SELECT created_at, Name, Password, Profile, Locale, Description, UserType, PasswordUpdateDate, MailAddress FROM fiable.nac_extraction_nac WHERE Name REGEXP '[a-zA-Z]{4}[0-9]{4}'"


    # Appeler la fonction export_gnoc avec les paramètres appropriés
    response = export_gnoc(request, model_name='Extraction_nac', model_fields=model_fields, custom_sql=custom_sql)

    return response

def export_tmp_nac(request):
    custom_sql = "SELECT created_at, Name, Password, Profile, Locale, Description, UserType, PasswordUpdateDate, MailAddress FROM fiable.nac_extraction_nac WHERE ((LOWER(Name) LIKE 'tmp%' OR  LOWER(Name) LIKE 'ext%' OR LOWER(Name) LIKE 'stg%' OR LOWER(Name) LIKE 'Int%') and commentaire='A garder')"
    model_fields = ['created_at', 'Name', 'Password', 'Profile', 'Locale', 'Description', 'UserType', 'PasswordUpdateDate', 'MailAddress','commentaire']
    
    response=export_tmp(request, model_name='Extraction_nac', model_fields=model_fields, custom_sql=custom_sql,app_label='nac')
    
    return response


def export_desc_nac(request):
    custom_sql = "SELECT created_at, Name, Password, Profile, Locale, Description, UserType, PasswordUpdateDate, MailAddress FROM fiable.nac_extraction_nac  WHERE (LOWER(Name) LIKE 'pcci%' OR LOWER(Name) LIKE 'stl%' OR LOWER(Name) LIKE '1431%' OR LOWER(Name) LIKE '1413%' OR LOWER(Name) LIKE 'ksv%' OR LOWER(Name) LIKE 'w2c%' OR LOWER(Name) LIKE 'pop_%' OR LOWER(Name) LIKE 'pdist%' OR LOWER(Name) LIKE 'sitel%' OR LOWER(Name) LIKE 'psup%')"
    model_fields = ['created_at', 'Name', 'Password', 'Profile', 'Locale', 'Description', 'UserType', 'PasswordUpdateDate', 'MailAddress','commentaire']
    model_name='Extraction_nac'
    search_field='Name'
    regex_pattern=r'^[a-zA-Z]{4}\d{4}$'
    
    response=export_desc(request, model_name=model_name, model_fields=model_fields,search_field=search_field, regex_pattern=regex_pattern,custom_sql=custom_sql,app_label='nac')
    
    return response

def export_nac_fiable(request):
    # custom_sql = "SELECT Name, Password, Profile, Locale, Description, UserType, PasswordUpdateDate, MailAddress FROM fiable.nac_extraction_nac"
    model_fields = ['Name', 'Password', 'Profile', 'Locale', 'Description', 'UserType', 'PasswordUpdateDate', 'MailAddress','commentaire']
    model_name='Extraction_nac'

    response=export_all(request, model_name=model_name, model_fields=model_fields,app_label='nac')
    
    return response


from django.db.models import Q

def update_from_user_nac(extraction_model, name_field):
    # Critères de filtrage pour les enregistrements du modèle extraction
    criteres = ["pcci", "stl", "1431", "1413", "ksv", "w2c", "pop_", "pdist", "sitel", "psup"]

    # Initialisation de la requête avec un Q object vide
    query = Q()

    # Boucle sur les critères pour construire la requête
    for critere in criteres:
        query |= Q(**{f"{name_field}__istartswith": critere})

    # Filtrer les enregistrements en utilisant la requête construite
    extraction_records = extraction_model.objects.filter(query)

    # Récupérer tous les noms des enregistrements du modèle Extraction_nac
    temporaire_records = Extraction_nac.objects.values_list('Name', flat=True)

    # Parcourir chaque enregistrement de extraction_records
    for extraction_record in extraction_records:
        name = getattr(extraction_record, name_field)
        traitement_fiabilisation = ""

        # Vérifier s'il y a une correspondance dans temporaire_records
        if name in temporaire_records:
            # Si une correspondance est trouvée, récupérer tous les enregistrements correspondants dans Extraction_nac
            matching_records = Extraction_nac.objects.filter(Name=name)
            # Parcourir chaque enregistrement correspondant et les mettre à jour
            for temporaire_record in matching_records:
                temporaire_record.Password = "*"
                temporaire_record.save()
                traitement_fiabilisation = temporaire_record.Password

        # Mettre à jour le champ traitement_fiabilisation dans l'enregistrement extraction
        extraction_record.traitement_fiabilisation = traitement_fiabilisation
        extraction_record.save()



def update_test_nac(request):
    update_from_user_nac(Extraction_zoom,"username")


    return redirect("extraction_nac")

