# Generated by Django 5.0.4 on 2024-05-13 12:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ussd_osn', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='extraction_ussd_osn',
            old_name='Group',
            new_name='Groups',
        ),
    ]
