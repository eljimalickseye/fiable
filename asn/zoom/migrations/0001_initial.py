# Generated by Django 5.0.4 on 2024-05-16 10:39

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Extraction_zoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('username', models.CharField(max_length=50, unique=True)),
                ('commentaire', models.CharField(max_length=200, null=True)),
            ],
            options={
                'verbose_name': 'Extraction_zoom',
                'verbose_name_plural': 'Extraction_zooms',
            },
        ),
    ]
