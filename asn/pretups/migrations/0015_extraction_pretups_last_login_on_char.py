# Generated by Django 5.0.4 on 2024-06-11 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pretups', '0014_alter_extraction_pretups_created_on_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='extraction_pretups',
            name='last_login_on_char',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
