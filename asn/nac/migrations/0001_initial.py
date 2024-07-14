# Generated by Django 5.0.4 on 2024-05-02 08:16

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Extraction_nac',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('Name', models.CharField(max_length=50, unique=True)),
                ('Password', models.CharField(max_length=50)),
                ('Profile', models.CharField(max_length=50)),
                ('Locale', models.CharField(max_length=50)),
                ('Description', models.CharField(max_length=100)),
                ('UserType', models.CharField(max_length=50)),
                ('PasswordUpdateDate', models.DateTimeField(blank=True, null=True)),
                ('MailAddress', models.CharField(max_length=200, null=True)),
                ('commentaire', models.CharField(max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'Extraction_nac',
                'verbose_name_plural': 'Extraction_nacs',
            },
        ),
    ]