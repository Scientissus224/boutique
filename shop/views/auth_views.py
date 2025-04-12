from django.shortcuts import redirect
from django.utils import timezone
from django.db import transaction
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from shop.token import generator_token
from django.contrib import messages
from shop.models import Utilisateur, UtilisateurTemporaire, InformationsSupplementairesTemporaire, InformationsSupplementaires
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)
ACTIVATION_TIMEOUT = timedelta(days=3)  # 3 jours de validité

def activate(request, uidb64, token):
    """Fonction d'activation robuste avec gestion sécurisée des doublons"""
    utilisateur_temporaire = None
    utilisateur = None

    try:
        # Décodage sécurisé de l'UID
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            utilisateur_temporaire = UtilisateurTemporaire.objects.select_for_update().get(pk=uid)
        except (TypeError, ValueError, OverflowError, UtilisateurTemporaire.DoesNotExist) as e:
            logger.warning(f"Échec décodage UID: {str(e)}")
            messages.error(request, 'Lien d\'activation invalide.')
            return redirect('inscription')

        # Vérification du token
        if not generator_token.check_token(utilisateur_temporaire, token):
            logger.warning(f"Token invalide pour {utilisateur_temporaire.email}")
            messages.error(request, 'Token d\'activation invalide.')
            return redirect('inscription')

        # Vérification expiration (3 jours)
        if timezone.now() > utilisateur_temporaire.created_at + ACTIVATION_TIMEOUT:
            logger.warning(f"Lien expiré pour {utilisateur_temporaire.email}")
            utilisateur_temporaire.delete()
            messages.error(request, 'Le lien a expiré. Veuillez recommencer l\'inscription.')
            return redirect('inscription')

        # Traitement transactionnel
        with transaction.atomic():
            # VÉRIFICATION EMAIL EXISTANT (version robuste)
            try:
                if Utilisateur.objects.filter(email=utilisateur_temporaire.email).exists():
                    logger.warning(f"Email existant: {utilisateur_temporaire.email}")
                    messages.error(request, 'Cet email est déjà associé à un compte actif. Veuillez vous connecter.')
                    utilisateur_temporaire.delete()
                    return redirect('login')
            except Exception as e:
                logger.error(f"Erreur vérification email: {str(e)}")
                raise

            # SUPPRESSION DOUBLONS (version robuste)
            try:
                doublons_count = Utilisateur.objects.filter(email=utilisateur_temporaire.email).count()
                if doublons_count > 0:
                    logger.info(f"Suppression de {doublons_count} doublon(s) pour {utilisateur_temporaire.email}")
                    Utilisateur.objects.filter(email=utilisateur_temporaire.email).delete()
            except Exception as e:
                logger.error(f"Erreur suppression doublons: {str(e)}")
                raise

            # CRÉATION UTILISATEUR
            try:
                infos_temporaire = InformationsSupplementairesTemporaire.objects.get(
                    utilisateur_temporaire=utilisateur_temporaire
                )
                
                utilisateur = Utilisateur.objects.create_user(
                    identifiant_unique=utilisateur_temporaire.identifiant_unique,
                    email=utilisateur_temporaire.email,
                    password=utilisateur_temporaire.password,
                    nom_complet=utilisateur_temporaire.nom_complet,
                    numero=utilisateur_temporaire.numero,
                    nom_boutique=utilisateur_temporaire.nom_boutique,
                    username=utilisateur_temporaire.email,
                    produits_vendus=infos_temporaire.produits_vendus,
                    is_active=True
                )

                InformationsSupplementaires.objects.create(
                    utilisateur=utilisateur,
                    type_boutique=infos_temporaire.type_boutique,
                    source_decouverte=infos_temporaire.source_decouverte,
                    produits_vendus=infos_temporaire.produits_vendus
                )

                logger.info(f"Compte activé: {utilisateur.email}")

            except Exception as e:
                logger.error(f"Erreur création utilisateur: {str(e)}")
                raise

        # Nettoyage post-activation
        try:
            utilisateur_temporaire.delete()
            infos_temporaire.delete()
        except Exception as e:
            logger.error(f"Erreur nettoyage: {str(e)}")

        messages.success(request, 'Compte activé avec succès!')
        return redirect('login')

    except Exception as e:
        logger.error(f"ERREUR CRITIQUE: {str(e)}", exc_info=True)
        
        # Nettoyage d'urgence
        if utilisateur and hasattr(utilisateur, 'pk'):
            try:
                utilisateur.delete()
            except Exception:
                logger.critical("Échec suppression utilisateur en erreur")
        
        messages.error(request, 'Une erreur est survenue lors de l\'activation.')
        return redirect('inscription')