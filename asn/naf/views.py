from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from openpyxl import Workbook
from django.db import connection
import mysql.connector


from .models import Extraction_naf

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

# Naf modele


def extraction_naf(request):
    # Récupérer tous les enregistrements
    naf_records = Extraction_naf.objects.all()

    # Pagination
    paginator = Paginator(naf_records, 100)  # 100 enregistrements par page
    page_number = request.GET.get('page')
    try:
        naf_records = paginator.page(page_number)
    except PageNotAnInteger:
        # Si le numéro de page n'est pas un entier, afficher la première page
        naf_records = paginator.page(1)
    except EmptyPage:
        # Si la page est vide, afficher la dernière page
        naf_records = paginator.page(paginator.num_pages)

    # Mettre en forme les enregistrements pour les inclure dans le contexte
    all_naf_records = []
    for naf_record in naf_records:
        all_naf_records.append({
            'id': naf_record.id,
            'Name': naf_record.Name,
            'Password': naf_record.Password,
            'Profile': naf_record.Profile,
            'Locale': naf_record.Locale,
            'Description': naf_record.Description,
            'UserType': naf_record.UserType,
            'PasswordUpdateDate': naf_record.PasswordUpdateDate,
            'Attempts': naf_record.Attempts,  # Ajout des attributs manquants
            'AccountLocked': naf_record.AccountLocked,  # Ajout des attributs manquants
            'LockedTime': naf_record.LockedTime,  # Ajout des attributs manquants
            'isFirstPasswordChanged': naf_record.isFirstPasswordChanged,  # Ajout des attributs manquants
            'MailAddress': naf_record.MailAddress,
            'commentaire': naf_record.commentaire,
            'EmailNotification': naf_record.EmailNotification  # Ajout des attributs manquants
        })

    context = {
        'all_naf_records': all_naf_records,
    }

    # Rendre la page d'accueil avec le contexte et les enregistrements paginés
    return render(request, 'naf_extract.html', {**context, 'naf_records': naf_records})



def inserer_extract_naf_data(donnees):
    try:
        for index, row in donnees.iterrows():
            # Gérer les valeurs NaN
            row = row.where(pd.notnull(row), None)
            
            # Créer une nouvelle instance du modèle Extraction_naf
            extraction = Extraction_naf(
                created_at=timezone.now(),
                Name=row['Name'],
                Password=row['Password'],
                Profile=row['Profile'],
                Locale=row['Locale'],
                Description=row['Description'],
                UserType=row['UserType'],
                PasswordUpdateDate=parser.parse(row['PasswordUpdateDate']),
                Attempts=row['Attempts'],  # Ajout des attributs manquants
                AccountLocked=row['AccountLocked'],  # Ajout des attributs manquants
                LockedTime=parser.parse(row['LockedTime']),  # Ajout des attributs manquants
                isFirstPasswordChanged=row['isFirstPasswordChanged'],  # Ajout des attributs manquants
                MailAddress=row['MailAddress'],
                EmailNotification=row['EmailNotification'],  # Ajout des attributs manquants
                commentaire=row['commentaire']
            )
            extraction.save()  # Enregistrer l'instance dans la base de données
            
            # Vérifier si le nom existe
            if row['Name']:
                comment = "MAJ non effectuée"
            else:
                comment = "A supprimer"
                
            # Mettre à jour le commentaire dans l'instance du modèle
            extraction.commentaire = comment
            extraction.save()  # Enregistrer la mise à jour dans la base de données
        
        print("Données insérées avec succès.")
    except Exception as e:
        raise e


def insert_extract_naf(request):
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
                    inserer_extract_naf_data(donnees)
            except Exception as e:
                return HttpResponse("Une erreur s'est produite lors de l'insertion des données : {}".format(e))
            return redirect('extraction_naf')
    else:
        form = Upload()
    return render(request, 'extract_naf.html', {'form': form})


def supprimer_naf_data(request):
    # Supprimer toutes les données de votre modèle
    Extraction_naf.objects.all().delete()

    return redirect('extraction_naf')


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
            FROM naf_extraction_naf
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
    return Extraction_naf.objects.exclude(commentaire='A garder')

def export_naf_disabled(request):
    # Créez un nouveau classeur Excel
    wb = Workbook()
    # Sélectionnez la première feuille de calcul (feuille active par défaut)
    ws = wb.active

    # Définissez le nom du fichier Excel dans l'en-tête de la réponse HTTP
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="naf_delete_profile.xlsx"'

    # Obtenez les enregistrements à exporter
    unique_ids = get_unique_ids()
    records_to_delete = get_records_to_delete()

    # Écrivez les en-têtes dans la première ligne
    headers = ['created_at', 'Name', 'Password', 'Profile', 'Locale','UserType', 'PasswordUpdateDate', 'Attempts', 'AccountLocked', 'LockedTime','isFirstPasswordChanged','MailAddress','Description','EmailNotification','commentaire']
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

def export_naf_actif(request):
    # Créez un nouveau classeur Excel
    wb = Workbook()
    # Sélectionnez la première feuille de calcul (feuille active par défaut)
    ws = wb.active

    # Définissez le nom du fichier Excel dans l'en-tête de la réponse HTTP
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="records_naf_actifs.xlsx"'

    # Récupérer les enregistrements actifs depuis la base de données Django
    records_actifs = Extraction_naf.objects.filter(commentaire='A garder').values_list('id', 'Name', 'Password', 'Profile', 'Locale', 'Description', 'UserType', 'PasswordUpdateDate', 'MailAddress', 'commentaire')

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




def update_naf(request):
    # Appeler la fonction pour mettre à jour les naf depuis Adm

    extraction_model='Extraction_naf'
    name_field='Name'
    app_label='naf'

    update_from_adm(request,extraction_model, name_field, app_label)

    return redirect("extraction_naf")


def update_extraction_from_temporaireDRH():
    # Récupérer tous les enregistrements du modèle extraction
    extraction_records = Extraction_naf.objects.filter(
        Name__istartswith="tmp"
    ) | Extraction_naf.objects.filter(
        Name__istartswith="ext"
    ) | Extraction_naf.objects.filter(
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
                commentaire = commentaire
        else:
            # Aucune correspondance trouvée
            commentaire = commentaire

        # Mettre à jour le commentaire dans l'enregistrement extraction
        extraction_record.commentaire = commentaire  
        extraction_record.save()
        

def update_NAf_tmp(request):
    # Appeler la fonction pour mettre à jour les naf depuis Adm
    update_from_temporaireDRH(Extraction_naf, 'Name')

    return redirect("extraction_naf")


def export_data_to_csv(request):
    # Définir les champs à exporter et leurs noms
    model_fields = ['created_at', 'Name', 'Password', 'Profile', 'Locale','UserType', 'PasswordUpdateDate', 'Attempts', 'AccountLocked', 'LockedTime','isFirstPasswordChanged','MailAddress','Description','EmailNotification','commentaire']
    
    custom_sql = "SELECT created_at, Name, Password, Profile, Locale, UserType, PasswordUpdateDate, NULL AS Attempts, NULL AS AccountLocked, NULL AS LockedTime, NULL AS isFirstPasswordChanged, MailAddress, Description, NULL AS EmailNotification, commentaire FROM fiable.naf_extraction_naf WHERE Name REGEXP '[a-zA-Z]{4}[0-9]{4}'"


    # Appeler la fonction export_gnoc avec les paramètres appropriés
    response = export_gnoc(request, model_name='Extraction_naf', model_fields=model_fields, custom_sql=custom_sql)

    return response

def export_tmp_naf(request):
    custom_sql = "SELECT created_at, Name, Password, Profile, Locale, UserType, PasswordUpdateDate, NULL AS Attempts, NULL AS AccountLocked, NULL AS LockedTime, NULL AS isFirstPasswordChanged, MailAddress, Description, NULL AS EmailNotification, commentaire FROM fiable.naf_extraction_naf WHERE ((LOWER(Name) LIKE 'tmp%' OR  LOWER(Name) LIKE 'ext%' OR LOWER(Name) LIKE 'stg%' OR LOWER(Name) LIKE 'Int%') and commentaire='A garder')"
    model_fields = ['created_at', 'Name', 'Password', 'Profile', 'Locale','UserType', 'PasswordUpdateDate', 'Attempts', 'AccountLocked', 'LockedTime','isFirstPasswordChanged','MailAddress','Description','EmailNotification','commentaire']
    
    response=export_tmp(request, model_name='Extraction_naf', model_fields=model_fields, custom_sql=custom_sql,app_label='naf')
    
    return response


def export_desc_naf(request):
    custom_sql = "SELECT created_at, Name, Password, Profile, Locale, UserType, PasswordUpdateDate, NULL AS Attempts, NULL AS AccountLocked, NULL AS LockedTime, NULL AS isFirstPasswordChanged, MailAddress, Description, NULL AS EmailNotification, commentaire FROM fiable.naf_extraction_naf  WHERE (LOWER(Name) LIKE 'pcci%' OR LOWER(Name) LIKE 'stl%' OR LOWER(Name) LIKE '1431%' OR LOWER(Name) LIKE '1413%' OR LOWER(Name) LIKE 'ksv%' OR LOWER(Name) LIKE 'w2c%' OR LOWER(Name) LIKE 'pop_%' OR LOWER(Name) LIKE 'pdist%' OR LOWER(Name) LIKE 'sitel%' OR LOWER(Name) LIKE 'psup%')"
    model_fields = ['created_at', 'Name', 'Password', 'Profile', 'Locale','UserType', 'PasswordUpdateDate', 'Attempts', 'AccountLocked', 'LockedTime','isFirstPasswordChanged','MailAddress','Description','EmailNotification','commentaire']
    model_name='Extraction_naf'
    search_field='Name'
    regex_pattern=r'^[a-zA-Z]{4}\d{4}$'
    
    response=export_desc(request, model_name=model_name, model_fields=model_fields,search_field=search_field, regex_pattern=regex_pattern,custom_sql=custom_sql,app_label='naf')
    
    return response

def export_naf_fiable(request):
    custom_sql = "SELECT Name, Password, Profile, Locale, UserType, PasswordUpdateDate,  Attempts,  AccountLocked,  LockedTime,  isFirstPasswordChanged, MailAddress, Description,  EmailNotification, commentaire FROM fiable.naf_extraction_naf"
    model_fields = ['Name', 'Password', 'Profile', 'Locale','UserType', 'PasswordUpdateDate', 'Attempts', 'AccountLocked', 'LockedTime','isFirstPasswordChanged','MailAddress','Description','EmailNotification','commentaire']
    model_name='Extraction_naf'

    response=export_all(request, model_name=model_name, model_fields=model_fields, custom_sql=custom_sql,app_label='naf')
    
    return response


