from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from openpyxl import Workbook
from django.db import connection
import mysql.connector


from .models import Extraction_ussd_osn

from core.models import  AdMPReport, TemporaireDRH
from core.views import export_gnoc,update_from_adm,update_from_temporaireDRH,export_tmp,export_desc,export_all

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import xlrd
from django.http import HttpResponse
import csv
from django.db import connection
import mysql.connector
import pandas as pd
from core.forms import Upload
import re
from django.utils import timezone
from dateutil import parser
from datetime import date
from django.db import transaction
from django.db import IntegrityError



def extraction_ussd_osn(request):
    # Récupérer tous les enregistrements
    ussd_osn_records = Extraction_ussd_osn.objects.all()

    # Pagination
    paginator = Paginator(ussd_osn_records, 100)  # 10 enregistrements par page
    page_number = request.GET.get('page')
    try:
        ussd_osn_records = paginator.page(page_number)
    except PageNotAnInteger:
        # Si le numéro de page n'est pas un entier, afficher la première page
        ussd_osn_records = paginator.page(1)
    except EmptyPage:
        # Si la page est vide, afficher la dernière page
        ussd_osn_records = paginator.page(paginator.num_pages)

    # Mettre en forme les enregistrements pour les inclure dans le contexte
    all_ussd_osn_records = []
    for ussd_osn_record in ussd_osn_records:
        all_ussd_osn_records.append({
            'id': ussd_osn_record.id,
            'User': ussd_osn_record.User,
            'Groups':ussd_osn_record.Groups,
            'commentaire': ussd_osn_record.commentaire,
        })
 

    context = {
        'all_ussd_osn_records': all_ussd_osn_records,
    }
    

    # Rendre la page d'accueil avec le contexte et les enregistrements paginés
    return render(request, 'ussd_osn_extract.html', {**context ,'ussd_osn_records': ussd_osn_records})



def inserer_extract_ussd_osn_data(donnees):
    try:
        for index, row in donnees.iterrows():
            # Gérer les valeurs NaN
            row = row.where(pd.notnull(row), None)
            
            # Créer une nouvelle instance du modèle Extraction_ussd_osn
            extraction = Extraction_ussd_osn(
                created_at=timezone.now(),
                User=row['User'],
                Groups=row['Groups'],
            )
            extraction.save()  # Enregistre r l'instance dans la base de données
            
            # Voir si le nom existe
            if row['User']:
                comment = "MAJ non effectue"
            else:
                comment = "A supprimer"
                
            # Mettre à jour le commentaire dans l'instance du modèle
            extraction.commentaire = comment
            extraction.save()  # Enregistrer la mise à jour dans la base de données
        
        print("Données insérées avec succès.")
    except Exception as e:
        raise e

def insert_extract_ussd_osn(request):
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
                    inserer_extract_ussd_osn_data(donnees)
            except Exception as e:
                return HttpResponse("Une erreur s'est produite lors de l'insertion des données : {}".format(e))
            return redirect('extraction_ussd_osn')
    else:
        form = Upload()
    return render(request, 'extract_ussd_osn.html', {'form': form})



def export_ussd_osn_fiable(request):
    # custom_sql = "SELECT User FROM fiable.ussd_osn_extraction_ussd_osn"
    model_fields = ['User', 'Groups','commentaire']
    model_name='Extraction_ussd_osn'

    response=export_all(request, model_name=model_name, model_fields=model_fields,app_label='ussd_osn')
    
    return response


def update_ussd_osn(request):
    # Appeler la fonction pour mettre à jour les ussd_osn depuis Adm

    extraction_model='Extraction_ussd_osn'
    name_field='User'
    app_label='ussd_osn'

    update_from_adm(request,extraction_model, name_field, app_label)

    return redirect("extraction_ussd_osn")


def update_extraction_from_temporaireDRH():
    # Récupérer tous les enregistrements du modèle extraction
    extraction_records = Extraction_ussd_osn.objects.filter(
        Name__istartswith="tmp"
    ) | Extraction_ussd_osn.objects.filter(
        Name__istartswith="ext"
    ) | Extraction_ussd_osn.objects.filter(
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
        

def update_ussd_osn_tmp(request):
    # Appeler la fonction pour mettre à jour les ussd_osn depuis Adm
    update_from_temporaireDRH(Extraction_ussd_osn, 'User')

    return redirect("extraction_ussd_osn")


def supprimer_ussd_osn_data(request):
    # Supprimer toutes les données de votre modèle
    Extraction_ussd_osn.objects.all().delete()

    return redirect('extraction_ussd_osn')


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
            FROM ussd_osn_extraction_ussd_osn
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
    return Extraction_ussd_osn.objects.exclude(commentaire='A garder')
