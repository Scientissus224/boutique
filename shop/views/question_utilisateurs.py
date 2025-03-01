from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from shop.models import UtilisateurTemporaire, InformationsSupplementairesTemporaire
from shop.forms import InformationsSupplementairesForm
from django.conf import settings

def informations_supplementaires_view(request, utilisateur_temporaire_id):
    """Vue pour collecter les informations supplémentaires."""
    utilisateur_temporaire = get_object_or_404(UtilisateurTemporaire, id=utilisateur_temporaire_id)

    if request.method == 'POST':
        form = InformationsSupplementairesForm(request.POST)
        
        if form.is_valid():
            # Vérifier si un enregistrement existe déjà pour cet utilisateur
            existing_info = InformationsSupplementairesTemporaire.objects.filter(utilisateur_temporaire=utilisateur_temporaire).first()
            
            if existing_info:
                # Si un enregistrement existe, le supprimer avant d'enregistrer le nouveau
                existing_info.delete()

            # Créer et enregistrer les nouvelles informations supplémentaires
            informations_temporaire = form.save(commit=False)
            informations_temporaire.utilisateur_temporaire = utilisateur_temporaire
            informations_temporaire.save()

            # Tenter d'envoyer les emails et gérer une éventuelle erreur
            try:
                # Envoi de l'email de bienvenue en premier
                send_welcome_email(request, utilisateur_temporaire)
                # Envoi de l'email de confirmation après l'email de bienvenue
                send_confirmation_email(request, utilisateur_temporaire)
            except Exception as e:
                messages.error(request, "Erreur survenu lors de l'inscription ! vérifier votre connexion et réessayer")
                return render(request, 'infos_plus.html', {'form': form, 'utilisateur': utilisateur_temporaire})

            # Affichage du message de succès
            messages.success(request, "Vos informations ont été enregistrées. Un email de bienvenue et un email de confirmation vous ont été envoyés.")
            return redirect('login')
    else:
        form = InformationsSupplementairesForm()

    return render(request, 'infos_plus.html', {'form': form, 'utilisateur': utilisateur_temporaire})

def send_confirmation_email(request, utilisateur_temporaire):
    """Envoi de l'email de confirmation."""
    current_site = get_current_site(request)
    email_subject = 'Validation de l\'email'
    message = render_to_string('emailConfirm.html', {
        'user': utilisateur_temporaire.nom_complet,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(utilisateur_temporaire.pk)),
        'token': utilisateur_temporaire.token
    })
    email = EmailMessage(
        email_subject,
        message,
        settings.EMAIL_HOST_USER,
        [utilisateur_temporaire.email]
    )
    email.content_subtype = "html"
    email.send(fail_silently=False)

def send_welcome_email(request, utilisateur_temporaire):
    """Envoi de l'email de bienvenue après l'enregistrement des informations supplémentaires."""
    current_site = get_current_site(request)
    email_subject = 'Bienvenue sur WarabaShop !'

    # Récupérer les informations supplémentaires de l'utilisateur
    informations_temporaire = InformationsSupplementairesTemporaire.objects.get(utilisateur_temporaire=utilisateur_temporaire)

    # Préparer le message pour l'email de bienvenue
    message = render_to_string('message.html', {
        'user': utilisateur_temporaire.nom_complet,
        'boutique': utilisateur_temporaire.nom_boutique,  # Assurez-vous d'avoir accès au nom de la boutique
        'email': utilisateur_temporaire.email,
        'numero': utilisateur_temporaire.numero,
        'identifiant':utilisateur_temporaire.identifiant_unique,
        'type_boutique': informations_temporaire.type_boutique,
        'produits_vendus': informations_temporaire.produits_vendus,
        'source_decouverte': informations_temporaire.source_decouverte,
        'domain': current_site.domain,
    })

    # Envoi de l'email de bienvenue
    email = EmailMessage(
        email_subject,
        message,
        settings.EMAIL_HOST_USER,
        [utilisateur_temporaire.email]
    )
    email.content_subtype = "html"
    email.send(fail_silently=False)
