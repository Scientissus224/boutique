# Generated by Django 5.2 on 2025-04-30 12:24

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0026_alter_supportclient_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='utilisateur',
            name='date_creation_compte',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
