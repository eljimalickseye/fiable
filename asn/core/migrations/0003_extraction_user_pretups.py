# Generated by Django 5.0.4 on 2024-06-10 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_crbt'),
    ]

    operations = [
        migrations.CreateModel(
            name='Extraction_user_pretups',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.CharField(blank=True, max_length=255, null=True)),
                ('last_login_on', models.DateTimeField(blank=True, null=True)),
                ('user_name', models.CharField(blank=True, max_length=255, null=True)),
                ('login_id', models.CharField(blank=True, max_length=255, null=True)),
                ('traitement_fiabilisation', models.CharField(blank=True, max_length=255, null=True)),
                ('category_code', models.CharField(blank=True, max_length=255, null=True)),
                ('category_name', models.CharField(blank=True, max_length=255, null=True)),
                ('contact_person', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(blank=True, max_length=255, null=True)),
                ('msisdn', models.CharField(blank=True, max_length=20, null=True)),
                ('pswd_modified', models.DateTimeField(blank=True, null=True)),
                ('created_on', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.CharField(blank=True, max_length=255, null=True)),
                ('modified_on', models.DateTimeField(blank=True, null=True)),
                ('user_type', models.CharField(blank=True, max_length=255, null=True)),
                ('role_code', models.CharField(blank=True, max_length=255, null=True)),
                ('role_name', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
