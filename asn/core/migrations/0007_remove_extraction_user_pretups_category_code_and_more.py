# Generated by Django 5.0.4 on 2024-07-12 12:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_extraction_user_pretups_msisdn_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='extraction_user_pretups',
            name='category_code',
        ),
        migrations.RemoveField(
            model_name='extraction_user_pretups',
            name='category_name',
        ),
        migrations.RemoveField(
            model_name='extraction_user_pretups',
            name='contact_person',
        ),
        migrations.RemoveField(
            model_name='extraction_user_pretups',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='extraction_user_pretups',
            name='created_on',
        ),
        migrations.RemoveField(
            model_name='extraction_user_pretups',
            name='last_login_on',
        ),
        migrations.RemoveField(
            model_name='extraction_user_pretups',
            name='modified_on',
        ),
        migrations.RemoveField(
            model_name='extraction_user_pretups',
            name='msisdn',
        ),
        migrations.RemoveField(
            model_name='extraction_user_pretups',
            name='pswd_modified',
        ),
        migrations.RemoveField(
            model_name='extraction_user_pretups',
            name='role_code',
        ),
        migrations.RemoveField(
            model_name='extraction_user_pretups',
            name='role_name',
        ),
        migrations.RemoveField(
            model_name='extraction_user_pretups',
            name='status',
        ),
        migrations.RemoveField(
            model_name='extraction_user_pretups',
            name='user_id',
        ),
        migrations.RemoveField(
            model_name='extraction_user_pretups',
            name='user_name',
        ),
        migrations.RemoveField(
            model_name='extraction_user_pretups',
            name='user_type',
        ),
    ]
