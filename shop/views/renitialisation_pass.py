from django.shortcuts import render, redirect

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils.encoding import force_bytes
from django.contrib.auth.hashers import make_password
from django.template.loader import render_to_string  # Ajout de l'import
import re
from django.views.decorators.csrf import csrf_exempt

# Importer le modèle Utilisateur personnalisé
from shop.models import Utilisateur

# Formulaire de réinitialisation du mot de passe
def envoyer_email_reinitialisation(request, email):
    """
    Recherche un utilisateur par son email et lui envoie un e-mail de demande de réinitialisation de mot de passe.
    """
    try:
        user = Utilisateur.objects.get(email=email)
    except Utilisateur.DoesNotExist:
        return False  # L'utilisateur n'existe pas
    
    # Générer le token et l'UID pour l'utilisateur
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    
    # Construire le lien de réinitialisation
    reset_link = f"http://{get_current_site(request).domain}/password_reset_confirm/{uid}/{token}/"
    site_link = f"http://{get_current_site(request).domain}/"
    
    # Préparer et envoyer l'e-mail
    subject = "Réinitialisation de votre mot de passe"
    message = render_to_string("password_reset_email.html", {
        'user': user,
        'reset_link': reset_link,
        'site_link':site_link,
    })
    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=message)
    
    return True

@csrf_exempt  # Désactive la protection CSRF (à utiliser avec prudence)
def demander_reinitialisation(request):
    if request.method == "POST":
        email = request.POST.get("email")  # Récupérer l'email depuis le formulaire
        
        # Vérifier la validité de l'email
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            return render(request, "password_reset_form.html", {"error": "Adresse e-mail invalide."})
        
        success = envoyer_email_reinitialisation(request, email)
        
        if success:
            return redirect('renitialisation_mail')
        else:
                        # Exemple de message d'erreur si l'email ou l'identifiant est introuvable
          messages.error(request, "Erreur : L'identifiant est introuvable ou un problème est survenu lors de l'envoi de l'email. Merci de vérifier votre adresse email et d'essayer à nouveau.")
    
    return render(request, "password_reset_form.html")


# Vue qui affiche un message après l'envoi du mail
def renitialisation_mail(request):
    
    return render(request, 'password_reset_done.html')

# Vue pour la confirmation de la réinitialisation du mot de passe
def reset_password(request, uidb64, token):
    try:
        # Récupérer les données de l'URL
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Utilisateur.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Utilisateur.DoesNotExist):
        messages.error(request, "Lien invalide ou utilisateur non trouvé.")
        return redirect('password_reset')

    # Vérifier la validité du token
    if not default_token_generator.check_token(user, token):
        messages.error(request, "Le lien de réinitialisation est invalide ou a expiré.")
        return redirect('password_reset')

    if request.method == "POST":
        # Récupérer les nouveaux mots de passe
        new_password = request.POST.get("new_password1")
        confirm_password = request.POST.get("new_password2")

        # Vérification des mots de passe
        if not new_password or new_password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'password_reset_confirm.html', {"uidb64": uidb64, "token": token})

        # Vérification de la validité du mot de passe avec une regex
        password_regex = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

        if not re.match(password_regex, new_password):
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères, une lettre, un chiffre et un caractère spécial.")
            return render(request, 'password_reset_confirm.html', {"uidb64": uidb64, "token": token})

        # Mettre à jour le mot de passe de l'utilisateur
        user.password = make_password(new_password)
        user.save()
        return redirect('password_reset_complete')

    return render(request, 'password_reset_confirm.html', {"uidb64": uidb64, "token": token})
# Vue de confirmation après la réinitialisation du mot de passe
def password_reset_complete(request):
    
    return render(request, 'password_reset_complete.html')
