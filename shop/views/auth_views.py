from django.shortcuts import redirect
from django.utils import timezone
from django.db import transaction
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from shop.token import generator_token
from django.contrib import messages
from shop.models import Utilisateur, UtilisateurTemporaire, InformationsSupplementairesTemporaire, InformationsSupplementaires

def activate(request, uidb64, token):
    try:
        # Décoder l'UID et récupérer l'utilisateur temporaire
        uid = force_str(urlsafe_base64_decode(uidb64))
        utilisateur_temporaire = UtilisateurTemporaire.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UtilisateurTemporaire.DoesNotExist):
        utilisateur_temporaire = None
        messages.error(request, 'Le lien d\'activation est invalide ou a expiré.')
        return redirect('inscription')

    # Vérifier le token de l'utilisateur temporaire
    if utilisateur_temporaire and generator_token.check_token(utilisateur_temporaire, token):
        # La vérification de l'expiration est gérée dans check_token

        # Sécuriser la création et supprimer les doublons
        try:
            with transaction.atomic():
                # Vérifier si l'email est déjà utilisé dans la table Utilisateur
                if Utilisateur.objects.filter(email=utilisateur_temporaire.email).exists():
                    messages.error(request, 'Cet email est déjà associé à un compte actif. Veuillez vous connecter.')
                    utilisateur_temporaire.delete()
                    return redirect('login')

                # Supprimer les utilisateurs avec le même email ou username dans Utilisateur
                Utilisateur.objects.filter(email=utilisateur_temporaire.email).delete()
                
                # Récupérer les informations supplémentaires de l'utilisateur temporaire
                informations_temporaire = InformationsSupplementairesTemporaire.objects.get(utilisateur_temporaire=utilisateur_temporaire)

                # Créer l'utilisateur final
                utilisateur = Utilisateur.objects.create_user(
                    identifiant_unique=utilisateur_temporaire.identifiant_unique,
                    email=utilisateur_temporaire.email,
                    password=utilisateur_temporaire.password,
                    nom_complet=utilisateur_temporaire.nom_complet,
                    numero=utilisateur_temporaire.numero,
                    nom_boutique=utilisateur_temporaire.nom_boutique,
                    username=utilisateur_temporaire.email,  # Utilise l'email comme username si nécessaire
                    produits_vendus=informations_temporaire.produits_vendus
                )
                utilisateur.is_active = True
                utilisateur.save()

                # Créer un objet InformationsSupplementaires et l'associer à l'utilisateur
                informations = InformationsSupplementaires(
                    utilisateur=utilisateur,
                    type_boutique=informations_temporaire.type_boutique,
                    source_decouverte=informations_temporaire.source_decouverte,
                    produits_vendus=informations_temporaire.produits_vendus
                )
                informations.save()

            # Supprimer l'utilisateur temporaire et ses informations associées
            utilisateur_temporaire.delete()
            informations_temporaire.delete()  # Supprimer les informations temporaires après transfert

            messages.success(request, "Votre compte a été activé avec succès. Bienvenue parmi nous !")
            return redirect('login')

        except Exception as e:
            # En cas d'erreur, loguer l'erreur pour des fins de debug
            print(f"Erreur lors de l'activation de l'utilisateur : {e}")
            messages.error(request, 'Une erreur est survenue pendant l\'activation de votre compte. Veuillez réessayer.')
            return redirect('inscription')

    else:
        if utilisateur_temporaire:
            utilisateur_temporaire.delete()
        messages.error(request, 'L\'activation a échoué. Le lien peut avoir expiré ou le token est invalide. Veuillez réessayer.')
        return redirect('inscription')
