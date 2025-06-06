# Generated by Django 5.2 on 2025-04-16 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0019_alter_boutique_logo_alter_commentaire_image_profil_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='boutique',
            name='description',
        ),
        migrations.AddField(
            model_name='boutique',
            name='titre',
            field=models.CharField(blank=True, help_text="Un titre accrocheur pour votre boutique (ex: 'Ma belle boutique de mode')", max_length=100, verbose_name='Titre de la boutique'),
        ),
    ]
