from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import Upload
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
import mysql.connector
import pandas as pd
from dateutil.relativedelta import relativedelta
import re
from django.utils import timezone
from dateutil import parser
from django.db import transaction, IntegrityError
from .models import Extraction_pretups
from core.views import export_all

def connect_to_database():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",
        database="fiable"
    )
    return connection

def extraction_pretups(request):
    now = datetime.now().date()
    three_months_ago = now - timedelta(days=3 * 30)
    extract_pretups = Extraction_pretups.objects.all()
    total_count = Extraction_pretups.objects.count()
    active_count = Extraction_pretups.objects.filter(traitement="A garder").count()
    paginator = Paginator(extract_pretups, 100)
    page_number = request.GET.get('page')
    try:
        extract_pretups = paginator.page(page_number)
    except PageNotAnInteger:
        extract_pretups = paginator.page(1)
    except EmptyPage:
        extract_pretups = paginator.page(paginator.num_pages)
    
    context = {
        'three_months_ago': three_months_ago,
        'all_extract_pretups': extract_pretups,
        'total_count': total_count,
        'active_count': active_count,
    }
    return render(request, 'ext_pretups.html', {**context, 'extract_pretups': extract_pretups})

def inserer_extract_pretups_data(donnees):
    try:
        instances = []
        for index, row in donnees.iterrows():
            row = row.where(pd.notnull(row), None)
            row = {k.lower(): v for k, v in row.items()}
            last_login_on = None
            if row['last_login_on']:
                try:
                    last_login_on = datetime.strptime(row['last_login_on'][:10], "%Y-%m-%d").date()
                except ValueError as e:
                    last_login_on = None

            modified_on = row['modified_on']
            created_on = row['created_on']

            ext_pretup = Extraction_pretups(
                created_at=timezone.now(),
                login_id=row['login_id'],
                user_name=row['user_name'],
                msisdn=row['msisdn'],
                status=row['status'],
                last_login_on=last_login_on,
                last_login_on_char=row['last_login_on'],
                employee_code=row['employee_code'],
                user_type=row['user_type'],
                modified_on=modified_on,
                created_on=created_on,
                role_code=row['role_code'],
                group_role_code=row['group_role_code'],
                role_name=row['role_name'],
                parent_user_name=row['parent_user_name'],
                parent_msisdn=row['parent_msisdn']
            )
            ext_pretup.commentaire, ext_pretup.traitement = get_comment_and_treatment(last_login_on, row['login_id'])
            instances.append(ext_pretup)

        with transaction.atomic():
            Extraction_pretups.objects.bulk_create(instances)
    except Exception as e:
        raise e

def get_comment_and_treatment(last_login_on, login_id):
    usernames = ["tmp", "ext", "INT"]
    critere = ["pcci", "stl", "1431", "1413", "ksv", "w2c", "pdist", "pop_", "sitel", "psup", 'W2C']
    username_regex = r'^[a-zA-Z]{4}\d{4}$'

    # Determine the comment interval based on login_id
    if any(login_id.lower().startswith(username) for username in usernames) or re.match(username_regex, login_id.lower()):
        comment_interval = relativedelta(months=1)
    else:
        comment_interval = relativedelta(months=3)

    # Determine the comment and treatment based on last_login_on and login_id
    if last_login_on is not None and last_login_on < timezone.now().date() - comment_interval and not any(login_id.lower().startswith(username) for username in critere):
        comment = f"Utilisateur inactif depuis plus de {comment_interval.months} mois"
        setTraitement = "A supprimer"
    elif any(login_id.lower().startswith(username) for username in critere) or any(login_id.upper().startswith(username) for username in critere):
        comment = 'Fiabilisation DESC'
        setTraitement = "DESC"
    elif last_login_on is None:
        comment = "Utilisateur jamais connecté"
        setTraitement = "A supprimer"
    else:
        comment = "Utilisateur actif"
        setTraitement = "A garder"

    return comment, setTraitement

def insert_pretups(request):
    if request.method == 'POST' and request.FILES.get('file'):
        form = Upload(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            if file.name.endswith('.xls') or file.name.endswith('.xlsx'):
                try:
                    donnees = pd.read_excel(file)
                except Exception as e:
                    return HttpResponse(f"Erreur lors de la lecture du fichier Excel : {e}")
            elif file.name.endswith('.csv'):
                try:
                    donnees = pd.read_csv(file)
                except Exception as e:
                    return HttpResponse(f"Erreur lors de la lecture du fichier CSV : {e}")
            else:
                return HttpResponse("Le fichier doit être au format Excel ou CSV.")

            try:
                connection = connect_to_database()
                if connection.is_connected():
                    inserer_extract_pretups_data(donnees)
                    connection.close()
            except mysql.connector.Error as e:
                return HttpResponse(f"Erreur lors de la connexion à la base de données MySQL : {e}")
            except Exception as e:
                return HttpResponse(f"Une erreur s'est produite lors de l'insertion des données dans la base de données MySQL : {e}")
            return redirect('extraction_pretups')
    else:
        form = Upload()
    return render(request, 'ext_pretups.html', {'form': form})

def supprimer_pretups_data(request):
    Extraction_pretups.objects.all().delete()
    return redirect('extraction_pretups')

def export_pretups_fiable(request):
    model_fields = ["login_id", "user_name", "msisdn", "status", "last_login_on", "last_login_on_char", "employee_code", "user_type", "modified_on", "created_on", "role_code", "group_role_code", "role_name", "parent_user_name", "parent_msisdn", "traitement", "commentaire"]
    response = export_all(request, model_name='Extraction_pretups', model_fields=model_fields, app_label='pretups')
    return response
