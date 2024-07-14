from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from openpyxl import Workbook
from django.db import connection
import mysql.connector


from .models import Extraction_zsmart

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

# zsmart modele


def extraction_zsmart(request):
    # Récupérer tous les enregistrements
    zsmart_records = Extraction_zsmart.objects.all()
    total_count = Extraction_zsmart.objects.count()
    active_count = Extraction_zsmart.objects.filter(commentaire="A garder").count()
    desc_count =Extraction_zsmart.objects.filter(commentaire="Fiabilisation DESC").count()

    # Pagination
    paginator = Paginator(zsmart_records, 100)  # 10 enregistrements par page
    page_number = request.GET.get('page')
    try:
        zsmart_records = paginator.page(page_number)
    except PageNotAnInteger:
        # Si le numéro de page n'est pas un entier, afficher la première page
        zsmart_records = paginator.page(1)
    except EmptyPage:
        # Si la page est vide, afficher la dernière page
        zsmart_records = paginator.page(paginator.num_pages)

    # Mettre en forme les enregistrements pour les inclure dans le contexte
    all_zsmart_records = []
    for zsmart_record in zsmart_records:
        all_zsmart_records.append({
            'id': zsmart_record.id,
            'compte': zsmart_record.compte,
            'nom':zsmart_record.nom,
            'statut_compte':zsmart_record.statut_compte,
            'date_creation':zsmart_record.date_creation,
            'verrouille':zsmart_record.verrouille,
            'profil':zsmart_record.profil,
            'commentaire': zsmart_record.commentaire,
        })
 

    context = {
        'all_zsmart_records': all_zsmart_records,
        'total_count':total_count,
        'active_count':active_count,
        'desc_count':desc_count
    }
    

    # Rendre la page d'accueil avec le contexte et les enregistrements paginés
    return render(request, 'zsmart_extract.html', {**context ,'zsmart_records': zsmart_records})


def inserer_extract_zsmart_data(donnees):
    try:
        for index, row in donnees.iterrows():
            # Gérer les valeurs NaN
            row = row.where(pd.notnull(row), None)
            
            # Créer une nouvelle instance du modèle Extraction_zsmart
            extraction = Extraction_zsmart(
                created_at=timezone.now(),
                compte=row['COMPTE'],
                nom=row['NOM'],
                statut_compte=row['STATUT_COMPTE'],
                date_creation=(row['DATE_CREATION']),
                verrouille=row['VERROUILLE'],
                profil=row['PROFIL'],
            )
            extraction.save()  # Enregistrer l'instance dans la base de données
            
            # Voir si le nom existe
            if row['COMPTE']:
                comment = "MAJ non effectue"
            else:
                comment = "A supprimer"
                
            # Mettre à jour le commentaire dans l'instance du modèle
            extraction.commentaire = comment
            extraction.save()  # Enregistrer la mise à jour dans la base de données
        
        print("Données insérées avec succès.")
    except Exception as e:
        raise e

def insert_extract_zsmart(request):
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
                    inserer_extract_zsmart_data(donnees)
            except Exception as e:
                return HttpResponse("Une erreur s'est produite lors de l'insertion des données : {}".format(e))
            return redirect('extraction_zsmart')
    else:
        form = Upload()
    return render(request, 'extract_zsmart.html', {'form': form})


def supprimer_zsmart_data(request):
    # Supprimer toutes les données de votre modèle
    Extraction_zsmart.objects.all().delete()

    return redirect('extraction_zsmart')


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
            FROM zsmart_extraction_zsmart
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
    return Extraction_zsmart.objects.exclude(commentaire='A garder')

def export_zsmart_disabled(request):
    pass


def export_zsmart_actif(request):
    # Créez un nouveau classeur Excel
    wb = Workbook()
    # Sélectionnez la première feuille de calcul (feuille active par défaut)
    ws = wb.active

    # Définissez le nom du fichier Excel dans l'en-tête de la réponse HTTP
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="records_zsmart_actifs.xlsx"'

    # Récupérer les enregistrements actifs depuis la base de données Django
    records_actifs = Extraction_zsmart.objects.filter(commentaire='A garder').values_list('id', 'compte','nom','statut_compte','date_creation','verrouille','profil', 'commentaire')

    # Écrire les en-têtes dans la première ligne
    headers = ['ID', 'compte','nom','statut_compte','date_creation','verrouille','profil', 'commentaire']
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




def update_zsmart(request):
    # Appeler la fonction pour mettre à jour les zsmart depuis Adm

    extraction_model='Extraction_zsmart'
    name_field='compte'
    app_label='zsmart'

    update_from_adm(request,extraction_model, name_field, app_label)

    return redirect("extraction_zsmart")


def update_extraction_from_temporaireDRH():
    # Récupérer tous les enregistrements du modèle extraction
    extraction_records = Extraction_zsmart.objects.filter(
        Name__istartswith="tmp"
    ) | Extraction_zsmart.objects.filter(
        Name__istartswith="ext"
    ) | Extraction_zsmart.objects.filter(
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
        

def update_zsmart_tmp(request):
    # Appeler la fonction pour mettre à jour les zsmart depuis Adm
    update_from_temporaireDRH(Extraction_zsmart, 'compte')

    return redirect("extraction_zsmart")

def fiabilisation_zsmart(request):
    extraction_model='Extraction_zsmart'
    name_field='compte'
    app_label='zsmart'

    update_from_adm(request,extraction_model, name_field, app_label)
    update_from_temporaireDRH(Extraction_zsmart, 'compte')

    return redirect("extraction_zsmart")



def export_data_to_csv(request):
    # Définir les champs à exporter et leurs noms
    model_fields = ['created_at', 'compte','nom','statut_compte','date_creation','verrouille','profil']
    
    custom_sql = "SELECT created_at, compte,nom,statut_compte,date_creation,verrouille,profil FROM fiable.zsmart_extraction_zsmart WHERE Name REGEXP '[a-zA-Z]{4}[0-9]{4}'"


    # Appeler la fonction export_gnoc avec les paramètres appropriés
    response = export_gnoc(request, model_name='Extraction_zsmart', model_fields=model_fields, custom_sql=custom_sql)

    return response

def export_tmp_zsmart(request):
    custom_sql = "SELECT created_at, compte,nom,statut_compte,date_creation,verrouille,profil FROM fiable.zsmart_extraction_zsmart WHERE ((LOWER(compte) LIKE 'tmp%' OR  LOWER(compte) LIKE 'ext%' OR LOWER(compte) LIKE 'stg%' OR LOWER(compte) LIKE 'Int%') and commentaire='A garder')"
    model_fields = ['created_at', 'compte','nom','statut_compte','date_creation','verrouille','profil','commentaire']
    
    response=export_tmp(request, model_name='Extraction_zsmart', model_fields=model_fields, custom_sql=custom_sql,app_label='zsmart')
    
    return response


def export_desc_zsmart(request):
    custom_sql = "SELECT created_at, compte,nom,statut_compte,date_creation,verrouille,profil FROM fiable.zsmart_extraction_zsmart  WHERE (LOWER(compte) LIKE 'pcci%' OR LOWER(compte) LIKE 'stl%' OR LOWER(compte) LIKE '1431%' OR LOWER(compte) LIKE '1413%' OR LOWER(compte) LIKE 'ksv%' OR LOWER(compte) LIKE 'w2c%' OR LOWER(compte) LIKE 'pop_%' OR LOWER(compte) LIKE 'pdist%' OR LOWER(compte) LIKE 'sitel%' OR LOWER(compte) LIKE 'psup%')"
    model_fields = ['created_at', 'compte','nom','statut_compte','date_creation','verrouille','profil','commentaire']
    model_name='Extraction_zsmart'
    search_field='compte'
    regex_pattern=r'^[a-zA-Z]{4}\d{4}$'
    
    response=export_desc(request, model_name=model_name, model_fields=model_fields,search_field=search_field, regex_pattern=regex_pattern,custom_sql=custom_sql,app_label='zsmart')
    
    return response

def export_zsmart_fiable(request):
    # custom_sql = "SELECT compte,nom,statut_compte,date_creation,verrouille,profil FROM fiable.zsmart_extraction_zsmart"
    model_fields = ['compte','nom','statut_compte','date_creation','verrouille','profil','commentaire']
    model_name='Extraction_zsmart'

    response=export_all(request, model_name=model_name, model_fields=model_fields,app_label='zsmart')
    
    return response


