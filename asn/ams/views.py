from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from openpyxl import Workbook
from django.db import connection
import mysql.connector


from .models import Extraction_ams

from core.models import AdMPReport, TemporaireDRH
from core.views import export_gnoc, update_from_adm, update_from_temporaireDRH, export_tmp, export_desc, export_all

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

# ams modele


def extraction_ams(request):
    # Récupérer tous les enregistrements
    ams_records = Extraction_ams.objects.all()

    # Pagination
    paginator = Paginator(ams_records, 100)  # 10 enregistrements par page
    page_number = request.GET.get('page')
    try:
        ams_records = paginator.page(page_number)
    except PageNotAnInteger:
        # Si le numéro de page n'est pas un entier, afficher la première page
        ams_records = paginator.page(1)
    except EmptyPage:
        # Si la page est vide, afficher la dernière page
        ams_records = paginator.page(paginator.num_pages)

    # Mettre en forme les enregistrements pour les inclure dans le contexte
    all_ams_records = []
    for ams_record in ams_records:
        all_ams_records.append({
            'id': ams_record.id,
            'user_id': ams_record.user_id,
            'full_user_name': ams_record.full_user_name,
            'email_address': ams_record.email_address,
            'description': ams_record.description,
            'password': ams_record.password,
            'change_password': ams_record.change_password,
            'bypass_password': ams_record.bypass_password,
            'roles': ams_record.roles,
            'allowed_pap_group': ams_record.allowed_pap_group,
            'use_global_max_number_of_concurrent_sessions': ams_record.use_global_max_number_of_concurrent_sessions,
            'locked': ams_record.locked,
            'commentaire': ams_record.commentaire,

        })

    context = {
        'all_ams_records': all_ams_records,
    }

    # Rendre la page d'accueil avec le contexte et les enregistrements paginés
    return render(request, 'ams_extract.html', {**context, 'ams_records': ams_records})


def inserer_extract_ams_data(donnees):
    try:
        for index, row in donnees.iterrows():
            # Gérer les valeurs NaN
            row = row.where(pd.notnull(row), None)

            # Créer une nouvelle instance du modèle Extraction_ams
            extraction = Extraction_ams(
                created_at=timezone.now(),
                user_id=row['user_id'],
                full_user_name=row['full_user_name'],
                email_address= row['email_address'],
                description=row['description'],
                password=row['password'],
                change_password=row['change_password'],
                bypass_password=row['bypass_password'],
                roles= row['roles'],
                allowed_pap_group=['allowed_pap_group'],
                use_global_max_number_of_concurrent_sessions= row['use_global_max_number_of_concurrent_sessions'],
                locked= row['locked'],
            )
            extraction.save()  # Enregistrer l'instance dans la base de données

            # Voir si le nom existe
            if row['user_id']:
                comment = "MAJ non effectue"
            else:
                comment = "A supprimer"

            # Mettre à jour le commentaire dans l'instance du modèle
            extraction.commentaire = comment
            extraction.save()  # Enregistrer la mise à jour dans la base de données

        print("Données insérées avec succès.")
    except Exception as e:
        raise e


def insert_extract_ams(request):
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
                    inserer_extract_ams_data(donnees)
            except Exception as e:
                return HttpResponse("Une erreur s'est produite lors de l'insertion des données : {}".format(e))
            return redirect('extraction_ams')
    else:
        form = Upload()
    return render(request, 'extract_ams.html', {'form': form})


def supprimer_ams_data(request):
    # Supprimer toutes les données de votre modèle
    Extraction_ams.objects.all().delete()

    return redirect('extraction_ams')


def get_unique_ids():
    """
    Récupère les identifiants uniques à partir de la base de données SQL.
    Returns:
        Un ensemble d'identifiants uniques.
    """
    unique_ids = set()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT user_id
            FROM ams_extraction_ams
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
    return Extraction_ams.objects.exclude(commentaire='A garder')


def export_ams_disabled(request):
    # Créez un nouveau classeur Excel
    wb = Workbook()
    # Sélectionnez la première feuille de calcul (feuille active par défaut)
    ws = wb.active

    # Définissez le nom du fichier Excel dans l'en-tête de la réponse HTTP
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="ams_delete_profile.xlsx"'

    # Obtenez les enregistrements à exporter
    unique_ids = get_unique_ids()
    records_to_delete = get_records_to_delete()

    # Écrivez les en-têtes dans la première ligne
    headers = ['user_id', 'full_user_name', 'email_address', 'description', 'password', 'change_password','bypass_password', 'roles', 'allowed_path_group', 'use_global_max_number_of_concurrent_sessions','locked','commentaire']
    ws.append(headers)

    # Parcourez les enregistrements et écrivez-les dans le fichier Excel
    for record_id in unique_ids:
        for record_django in records_to_delete:
            if record_django.id == record_id:
                # Supprimez les informations de fuseau horaire des dates/heure
                password_update_date = record_django.PasswordUpdateDate.replace(
                    tzinfo=None) if record_django.PasswordUpdateDate else None
                record = [record_django.id, record_django.Name, record_django.Password, record_django.Profile, record_django.Locale,
                          record_django.Description, record_django.UserType, password_update_date, record_django.MailAddress, record_django.commentaire]
                ws.append(record)
                break

    # Sauvegardez le classeur Excel dans la réponse HTTP
    wb.save(response)

    return response


def export_ams_actif(request):
    # Créez un nouveau classeur Excel
    wb = Workbook()
    # Sélectionnez la première feuille de calcul (feuille active par défaut)
    ws = wb.active

    # Définissez le nom du fichier Excel dans l'en-tête de la réponse HTTP
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="records_ams_actifs.xlsx"'

    # Récupérer les enregistrements actifs depuis la base de données Django
    records_actifs = Extraction_ams.objects.filter(commentaire='A garder').values_list(
        'user_id', 'full_user_name', 'email_address', 'description', 'password', 'change_password','bypass_password', 'roles', 'allowed_path_group', 'use_global_max_number_of_concurrent_sessions','locked','commentaire')

    # Écrire les en-têtes dans la première ligne
    headers = ['user_id', 'full_user_name', 'email_address', 'description', 'password', 'change_password','bypass_password', 'roles', 'allowed_path_group', 'use_global_max_number_of_concurrent_sessions','locked','commentaire']
    ws.append(headers)

    # Écrire les enregistrements dans le fichier Excel
    for record in records_actifs:
        # Supprimez les informations de fuseau horaire des dates/heure
        password_update_date = record[7].replace(
            tzinfo=None) if record[7] else None
        record = list(record)
        record[7] = password_update_date
        ws.append(record)

    # Sauvegardez le classeur Excel dans la réponse HTTP
    wb.save(response)

    return response


def update_ams(request):
    # Appeler la fonction pour mettre à jour les ams depuis Adm

    extraction_model = 'Extraction_ams'
    name_field = 'user_id'
    app_label = 'ams'

    update_from_adm(request, extraction_model, name_field, app_label)

    return redirect("extraction_ams")


def update_extraction_from_temporaireDRH():
    # Récupérer tous les enregistrements du modèle extraction
    extraction_records = Extraction_ams.objects.filter(
        id__istartswith="tmp"
    ) | Extraction_ams.objects.filter(
        id__istartswith="ext"
    ) | Extraction_ams.objects.filter(
        id__istartswith="INT"
    )

    # Récupérer tous les noms des enregistrements du modèle TemporaireDRH
    temporaire_records = TemporaireDRH.objects.values_list(
        'logon_name', flat=True)

    # Parcourir chaque enregistrement de extraction_records
    for extraction_record in extraction_records:
        Name = extraction_record.user_id
        commentaire = ""

        # Rechercher une correspondance partielle dans les noms des enregistrements TemporaireDRH avec un score supérieur ou égal à 80%
        match = process.extractOne(
            Name, temporaire_records, scorer=fuzz.partial_ratio, score_cutoff=100)

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


def update_ams_tmp(request):
    # Appeler la fonction pour mettre à jour les ams depuis Adm
    update_from_temporaireDRH(Extraction_ams, 'user_id')

    return redirect("extraction_ams")


def export_data_to_csv(request):
    # Définir les champs à exporter et leurs noms
    model_fields = ['created_at', 'user_id', 'full_user_name', 'email_address', 'description', 'password', 'change_password','bypass_password', 'roles', 'allowed_path_group', 'use_global_max_number_of_concurrent_sessions','locked','commentaire']

    custom_sql = "SELECT created_at, user_id, full_user_name, email_address, description, password, change_password,bypass_password, roles, allowed_path_group, use_global_max_number_of_concurrent_sessions,locked FROM fiable.ams_extraction_ams WHERE Name REGEXP '[a-zA-Z]{4}[0-9]{4}'"

    # Appeler la fonction export_gnoc avec les paramètres appropriés
    response = export_gnoc(request, model_name='Extraction_ams',
                           model_fields=model_fields, custom_sql=custom_sql)

    return response


def export_tmp_ams(request):
    # custom_sql = "SELECT created_at, Name, Password, Profile, Locale, Description, UserType, PasswordUpdateDate, MailAddress FROM fiable.ams_extraction_ams WHERE ((LOWER(Name) LIKE 'tmp%' OR  LOWER(Name) LIKE 'ext%' OR LOWER(Name) LIKE 'stg%' OR LOWER(Name) LIKE 'Int%') and commentaire='A garder')"
    model_fields = ['created_at', 'user_id', 'full_user_name', 'email_address', 'description', 'password', 'change_password','bypass_password', 'roles', 'allowed_path_group', 'use_global_max_number_of_concurrent_sessions','locked','commentaire']

    response = export_tmp(request, model_name='Extraction_ams',
                          model_fields=model_fields, app_label='ams')

    return response


def export_desc_ams(request):
    # custom_sql = "SELECT created_at, Name, Password, Profile, Locale, Description, UserType, PasswordUpdateDate, MailAddress FROM fiable.ams_extraction_ams  WHERE (LOWER(Name) LIKE 'pcci%' OR LOWER(Name) LIKE 'stl%' OR LOWER(Name) LIKE '1431%' OR LOWER(Name) LIKE '1413%' OR LOWER(Name) LIKE 'ksv%' OR LOWER(Name) LIKE 'w2c%' OR LOWER(Name) LIKE 'pop_%' OR LOWER(Name) LIKE 'pdist%' OR LOWER(Name) LIKE 'sitel%' OR LOWER(Name) LIKE 'psup%')"
    model_fields = ['created_at', 'user_id', 'full_user_name', 'email_address', 'description', 'password', 'change_password','bypass_password', 'roles', 'allowed_path_group', 'use_global_max_number_of_concurrent_sessions','locked','commentaire']

    model_name = 'Extraction_ams'
    search_field = 'user_id'
    regex_pattern = r'^[a-zA-Z]{4}\d{4}$'

    response = export_desc(request, model_name=model_name, model_fields=model_fields,
                           search_field=search_field, regex_pattern=regex_pattern, app_label='ams')

    return response


def export_ams_fiable(request):
    # custom_sql = "SELECT Name, Password, Profile, Locale, Description, UserType, PasswordUpdateDate, MailAddress FROM fiable.ams_extraction_ams"
    model_fields = ['created_at', 'user_id', 'full_user_name', 'email_address', 'description', 'password', 'change_password','bypass_password', 'roles', 'allowed_path_group', 'use_global_max_number_of_concurrent_sessions','locked','commentaire']

    model_name = 'Extraction_ams'

    response = export_all(request, model_name=model_name,
                          model_fields=model_fields, app_label='ams')

    return response
