from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db import transaction
from django.core.exceptions import SuspiciousOperation
from shop.models import Utilisateur, Client, InformationsSupplementaires, SupportClient
import urllib.request
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def login(request):
    """
    Vue de connexion ultra-sécurisée avec :
    - Vérification stricte de l'état actif/inactif
    - Protection renforcée contre les attaques
    - Journalisation complète
    - Conservation stricte de la logique originale
    """
    # 1. Vérification connexion internet (sécurisée)
    try:
        urllib.request.urlopen('https://www.google.com', timeout=3)
    except Exception as e:
        logger.warning(f"Absence de connexion internet - {str(e)}")
        messages.error(request, "Connexion internet requise")
        return render(request, 'login.html', status=503)
    
    # 2. Gestion des requêtes POST
    if request.method == 'POST':
        start_time = datetime.now()
        
        try:
            # 3. Nettoyage et validation des entrées
            username = request.POST.get('username', '').strip()[:150]  # Limite anti-DoS
            password = request.POST.get('password', '').strip()[:128]
            
            if not username or not password:
                messages.error(request, 'Tous les champs sont obligatoires')
                return redirect('login')

            # 4. Authentification sécurisée
            with transaction.atomic():
                user = authenticate(request, username=username, password=password)
                
                if not user:
                    logger.warning(f"Échec authentification - username: {username[:10]}...")
                    messages.error(request, "Identifiants incorrects")
                    return redirect('login')

                # 5. Vérification stricte de l'activation
                if not user.is_active:
                    logger.warning(f"Tentative connexion compte inactif - user_id: {user.id}")
                    messages.error(request, "Compte non activé - Vérifiez vos emails")
                    return redirect('login')

                # 6. Connexion autorisée
                auth_login(request, user)
                request.session.cycle_key()  # Protection contre le fixation

                # 7. Gestion des types d'utilisateurs (logique originale conservée)
                if isinstance(user, Utilisateur):
                    try:
                        infos = InformationsSupplementaires.objects.select_for_update().get(utilisateur=user)
                        request.session.update({
                            'connection': True,
                            'user_id': user.id,
                            'type_boutique': infos.type_boutique,
                            'last_login': str(datetime.now())
                        })
                        logger.info(f"Connexion réussie - Boutiquier: {user.id}")
                        messages.success(request, f"Bienvenue, {user.nom_complet} dans votre boutique '{user.nom_boutique}' !")
                        return redirect('table')

                    except InformationsSupplementaires.DoesNotExist:
                        logger.error(f"Infos manquantes - Boutiquier: {user.id}")
                        messages.error(request, "Configuration compte incomplète")
                        return redirect('login')

                elif isinstance(user, Client):
                    request.session.update({
                        'connection': True,
                        'user_id': user.id,
                        'last_login': str(datetime.now())
                    })
                    logger.info(f"Connexion réussie - Client: {user.id}")
                    messages.success(request, f"Bienvenue, {user.nom_complet} !")
                    return redirect('platForm')
                
                elif isinstance(user, SupportClient):
                    request.session.update({
                        'connection': True,
                        'user_id': user.id,
                        'last_login': str(datetime.now())
                    })
                    logger.info(f"Connexion réussie - Support: {user.id}")
                    messages.success(request, f"Bienvenue, {user.nom} !")
                    return redirect('update_status')

        except Exception as e:
            logger.error(f"ERREUR CONNEXION - {str(e)}", exc_info=True)
            messages.error(request, "Erreur système - Veuillez réessayer")
            return redirect('login')

        finally:
            # Mesure du temps d'exécution
            duration = (datetime.now() - start_time).total_seconds()
            logger.debug(f"Temps traitement login: {duration:.3f}s")

    # 8. Gestion des requêtes GET
    return render(request, 'login.html', status=200)