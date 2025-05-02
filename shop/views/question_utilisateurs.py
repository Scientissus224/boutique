from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
import socket
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from shop.models import UtilisateurTemporaire, InformationsSupplementairesTemporaire
from shop.forms import InformationsSupplementairesForm

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
            messages.success(request, "Vos informations ont été enregistrées.Un email contenant votre identifiant et un lien d'activation vous a été envoyé. Veuillez vérifier votre boîte de réception et activer votre compte en cliquant sur le lien. Tant que votre compte n’est pas activé, vous ne pourrez pas vous connecter.")
            return redirect('login')
    else:
        form = InformationsSupplementairesForm()

    return render(request, 'infos_plus.html', {'form': form, 'utilisateur': utilisateur_temporaire})



def is_connected():
    """Vérifie si la machine est connectée à Internet."""
    try:
        # On essaie de se connecter à un serveur DNS connu (Google)
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def send_welcome_and_confirmation_email(request, utilisateur_temporaire):
    """Envoi de l'email combiné (bienvenue + activation), si connexion Internet active."""
    
    if not is_connected():
        print("Pas de connexion Internet. L'email n'a pas été envoyé.")
        return  # Tu peux aussi lever une exception personnalisée ou logger ça
    
    current_site = get_current_site(request)
    email_subject = f"Bienvenue sur WarabaGuinée ! – {utilisateur_temporaire.identifiant_unique}"

    informations_temporaire = InformationsSupplementairesTemporaire.objects.get(
        utilisateur_temporaire=utilisateur_temporaire
    )

    message = render_to_string('message.html', {
        'user': utilisateur_temporaire.nom_complet,
        'boutique': utilisateur_temporaire.nom_boutique,
        'email': utilisateur_temporaire.email,
        'numero': utilisateur_temporaire.numero,
        'identifiant': utilisateur_temporaire.identifiant_unique,
        'type_boutique': informations_temporaire.type_boutique,
        'produits_vendus': informations_temporaire.produits_vendus,
        'source_decouverte': informations_temporaire.source_decouverte,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(utilisateur_temporaire.id)),
        'token': utilisateur_temporaire.token,
    })

    # Connexion SMTP explicite
    connection = get_connection(fail_silently=False)

    email = EmailMessage(
        subject=email_subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=[utilisateur_temporaire.email],
        connection=connection
    )
    email.content_subtype = "html"
    email.send()
    
    