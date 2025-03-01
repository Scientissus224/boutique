from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import logout
from django.db.models import Q
from .models import Utilisateur, Client, SupportClient
import logging

# Configuration du logger pour les messages de débogage
logger = logging.getLogger(__name__)

class UtilisateurBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        """
        Authentifie un utilisateur (client, boutiquier, ou support) en utilisant son email ou son identifiant_unique.
        """
        if request and request.user.is_authenticated:
            # Déconnecter l'utilisateur actuel pour éviter des conflits
            logout(request)

        if not username or not password:
            logger.error("Les champs 'username' et 'password' sont requis.")
            return None  # Les deux champs sont obligatoires

        # Nettoyer le username pour éviter les espaces blancs
        username = username.strip()

        try:
            utilisateur = None
            support_client = None

            # Recherche par email (insensible à la casse)
            if '@' in username:
                logger.debug(f"Recherche par email: {username}")
                utilisateur = Utilisateur.objects.filter(email__iexact=username).first()
                if utilisateur:
                    logger.debug(f"Utilisateur trouvé dans Utilisateur: {utilisateur}")
                    if utilisateur.check_password(password):
                        return utilisateur  # Retourne un utilisateur boutiquier

                # Recherche dans SupportClient
                support_client = SupportClient.objects.filter(
                    email__iexact=username, is_active=True  # S'assurer que l'utilisateur est actif
                ).first()
                if support_client:
                    logger.debug(f"Utilisateur trouvé dans SupportClient: {support_client}")
                    if support_client.check_password(password):
                        return support_client  # Retourne un utilisateur support

            # Recherche par identifiant_unique
            else:
                logger.debug(f"Recherche par identifiant_unique ou nom: {username}")
                utilisateur = Utilisateur.objects.filter(Q(identifiant_unique=username) | Q(nom_complet__icontains=username)).first()
                if utilisateur:
                    logger.debug(f"Utilisateur trouvé dans Utilisateur: {utilisateur}")
                    if utilisateur.check_password(password):
                        return utilisateur  # Retourne un utilisateur boutiquier

                # Recherche dans SupportClient
                support_client = SupportClient.objects.filter(
                    Q(nom__icontains=username) | Q(email__iexact=username), is_active=True
                ).first()
                if support_client:
                    logger.debug(f"Utilisateur trouvé dans SupportClient: {support_client}")
                    if support_client.check_password(password):
                        return support_client  # Retourne un utilisateur support

            # Recherche de client par email si l'utilisateur n'est pas trouvé
            client = Client.objects.filter(email__iexact=username).first()
            if client:
                logger.debug(f"Client trouvé: {client}")
                if client.check_password(password):
                    return client  # Retourne un client authentifié

        except Exception as e:
            # Journaliser l'erreur pour déboguer si nécessaire
            logger.error(f"Erreur lors de l'authentification: {e}")
            return None  # Retourner None si l'authentification échoue

        logger.warning("Aucun utilisateur trouvé avec les identifiants fournis.")
        return None  # Retourner None si l'authentification échoue

    def get_user(self, user_id):
        """
        Récupère un utilisateur à partir de son ID.
        """
        try:
            utilisateur = Utilisateur.objects.get(pk=user_id)
            if utilisateur:
                return utilisateur

            client = Client.objects.get(pk=user_id)
            if client:
                return client

            support_client = SupportClient.objects.get(pk=user_id)
            if support_client:
                return support_client

        except (Utilisateur.DoesNotExist, Client.DoesNotExist, SupportClient.DoesNotExist) as e:
            logger.error(f"Erreur lors de la récupération de l'utilisateur: {e}")
            return None
