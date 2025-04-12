from django.shortcuts import redirect
from django.utils import timezone
from django.db import transaction
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from shop.token import generator_token
from django.contrib import messages
from shop.models import Utilisateur, UtilisateurTemporaire, InformationsSupplementairesTemporaire, InformationsSupplementaires
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

def activate(request, uidb64, token):
    try:
        # Décodage sécurisé de l'UID
        uid = force_str(urlsafe_base64_decode(uidb64))
        utilisateur_temporaire = UtilisateurTemporaire.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UtilisateurTemporaire.DoesNotExist) as e:
        logger.warning(f"UID invalide ou utilisateur inexistant : {e}")
        messages.error(request, 'Lien d\'activation invalide.')
        return redirect('inscription')

    # Vérification du token
    if generator_token.check_token(utilisateur_temporaire, token):
        # Expiration à 1 jour
        expiration_time = utilisateur_temporaire.created_at + timedelta(days=1)
        if timezone.now() > expiration_time:
            try:
                utilisateur_temporaire.delete()
            except Exception as e:
                logger.error(f"Erreur suppression utilisateur expiré : {e}")
            messages.error(request, 'Le lien d\'activation a expiré. Veuillez recommencer l\'inscription.')
            return redirect('inscription')

        try:
            with transaction.atomic():
                # Email déjà utilisé ?
                if Utilisateur.objects.filter(email=utilisateur_temporaire.email).exists():
                    try:
                        utilisateur_temporaire.delete()
                    except Exception as e:
                        logger.error(f"Erreur suppression utilisateur temporaire doublon : {e}")
                    messages.error(request, 'Cet email est déjà associé à un compte actif. Veuillez vous connecter.')
                    return redirect('login')

                # Supprimer les doublons éventuels dans Utilisateur
                Utilisateur.objects.filter(email=utilisateur_temporaire.email).delete()

                # Récupération des infos supplémentaires temporaires
                try:
                    informations_temporaire = InformationsSupplementairesTemporaire.objects.get(
                        utilisateur_temporaire=utilisateur_temporaire
                    )
                except InformationsSupplementairesTemporaire.DoesNotExist as e:
                    logger.error(f"Infos temporaires introuvables : {e}")
                    utilisateur_temporaire.delete()
                    messages.error(request, 'Erreur interne. Veuillez recommencer l\'inscription.')
                    return redirect('inscription')

                # Création de l'utilisateur final
                utilisateur = Utilisateur.objects.create_user(
                    identifiant_unique=utilisateur_temporaire.identifiant_unique,
                    email=utilisateur_temporaire.email,
                    password=utilisateur_temporaire.password,
                    nom_complet=utilisateur_temporaire.nom_complet,
                    numero=utilisateur_temporaire.numero,
                    nom_boutique=utilisateur_temporaire.nom_boutique,
                    username=utilisateur_temporaire.email,
                    produits_vendus=informations_temporaire.produits_vendus
                )
                utilisateur.is_active = True
                utilisateur.save()

                # Enregistrement des infos supplémentaires
                InformationsSupplementaires.objects.create(
                    utilisateur=utilisateur,
                    type_boutique=informations_temporaire.type_boutique,
                    source_decouverte=informations_temporaire.source_decouverte,
                    produits_vendus=informations_temporaire.produits_vendus
                )

        except Exception as e:
            logger.critical(f"Erreur critique activation : {e}", exc_info=True)
            messages.error(request, 'Une erreur est survenue lors de l\'activation.')
            return redirect('inscription')

        # Nettoyage après succès
        try:
            utilisateur_temporaire.delete()
            informations_temporaire.delete()
        except Exception as e:
            logger.warning(f"Nettoyage post-activation échoué : {e}")

        messages.success(request, 'Votre compte a été activé avec succès. Vous pouvez maintenant vous connecter.')
        return redirect('login')

    else:
        try:
            utilisateur_temporaire.delete()
        except Exception as e:
            logger.error(f"Échec suppression utilisateur après token invalide : {e}")
        messages.error(request, 'L\'activation a échoué. Le lien peut avoir expiré ou le token est invalide. Veuillez réessayer.')
        return redirect('inscription')
