# Generated by Django 5.0.4 on 2024-05-05 09:04

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pretups',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('login_id', models.CharField(max_length=50, unique=True)),
                ('user_name', models.CharField(max_length=50)),
                ('msisdn', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=50)),
                ('last_login_on', models.DateTimeField(blank=True, null=True)),
                ('commentaire', models.CharField(max_length=100)),
                ('traitement', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Pretups',
                'verbose_name_plural': 'Pretups',
            },
        ),
    ]
