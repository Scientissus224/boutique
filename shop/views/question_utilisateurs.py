from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from shop.models import UtilisateurTemporaire, InformationsSupplementairesTemporaire
from shop.forms import InformationsSupplementairesForm
from django.templatetags.static import static

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

            # Tenter d'envoyer l'email de bienvenue et confirmation
            try:
                # Envoi de l'email combiné (bienvenue + activation)
                send_welcome_and_confirmation_email(request, utilisateur_temporaire)
            except Exception as e:
                messages.error(request, "Erreur survenue lors de l'inscription ! Vérifiez votre connexion et réessayez.")
                return render(request, 'infos_plus.html', {'form': form, 'utilisateur': utilisateur_temporaire})

            # Affichage du message de succès
            messages.success(request, "Vos informations ont été enregistrées. Un email de bienvenue et de confirmation vous a été envoyé.")
            return redirect('login')
    else:
        form = InformationsSupplementairesForm()

    return render(request, 'infos_plus.html', {'form': form, 'utilisateur': utilisateur_temporaire})

def send_welcome_and_confirmation_email(request, utilisateur_temporaire):
    """Envoi de l'email combiné (bienvenue + activation)."""
    current_site = get_current_site(request)
    email_subject = 'Bienvenue sur WarabaShop !'

    # Récupérer les informations supplémentaires de l'utilisateur
    informations_temporaire = InformationsSupplementairesTemporaire.objects.get(utilisateur_temporaire=utilisateur_temporaire)

    # URL pour le logo stocké dans le dossier static
    logo_url = current_site.domain + static('/static/lo.jpeg')
    

    # Préparer le message pour l'email de bienvenue avec le lien d'activation
    message = render_to_string('message.html', {
        'user': utilisateur_temporaire.nom_complet,
        'boutique': utilisateur_temporaire.nom_boutique,  # Assurez-vous d'avoir accès au nom de la boutique
        'email': utilisateur_temporaire.email,
        'numero': utilisateur_temporaire.numero,
        'identifiant': utilisateur_temporaire.identifiant_unique,
        'type_boutique': informations_temporaire.type_boutique,
        'produits_vendus': informations_temporaire.produits_vendus,
        'source_decouverte': informations_temporaire.source_decouverte,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(utilisateur_temporaire.pk)),
        'token': utilisateur_temporaire.token,
        'logo_url': logo_url,  # Ajout de l'URL du logo
    })

    # Envoi de l'email combiné
    email = EmailMessage(
        email_subject,
        message,
        settings.EMAIL_HOST_USER,
        [utilisateur_temporaire.email]
    )
    email.content_subtype = "html"
    email.send(fail_silently=False)
