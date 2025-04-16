from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import urllib.request
from django.shortcuts import redirect, get_object_or_404
from shop.models import Utilisateur, Commande, Produit, Variante, Devise, VenteAttente
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.utils.html import strip_tags
import logging
from django.db import transaction
from urllib.error import URLError
from socket import timeout as SocketTimeout
from django.core.exceptions import ValidationError

# Configuration du logger
logger = logging.getLogger(__name__)

def recuperer_panier(request):
    """ Récupère le panier depuis la session avec vérification complète. """
    try:
        if not hasattr(request, 'session'):
            logger.error("Aucune session disponible dans la requête")
            messages.error(request, "Problème de session. Veuillez rafraîchir la page.")
            return None
            
        panier = request.session.get('panier', {})
        if not isinstance(panier, dict):
            logger.error("Format de panier invalide dans la session")
            request.session['panier'] = {}  # Réinitialise un panier valide
            messages.error(request, "Problème avec votre panier. Veuillez réessayer.")
            return None
            
        if not panier:
            messages.error(request, "Votre panier est vide.")
            return None
            
        return panier
        
    except Exception as e:
        logger.error(f"Erreur critique lors de la récupération du panier: {str(e)}", exc_info=True)
        messages.error(request, "Une erreur critique est survenue avec votre panier.")
        return None

def valider_item_panier(item):
    """ Valide la structure d'un item du panier. """
    required_fields = {'type', 'prix'}
    if not all(field in item for field in required_fields):
        raise ValidationError("Item de panier incomplet")
    
    if item['type'] not in ('produit', 'variante'):
        raise ValidationError("Type d'article invalide")
    
    try:
        float(item['prix'])
    except (ValueError, TypeError):
        raise ValidationError("Prix invalide")

def recuperer_produits_info(panier):
    """ Récupère les informations des produits et variantes dans le panier avec gestion robuste des erreurs. """
    produits_info = []
    total_prix = 0.0
    items_valides = 0
    
    if not isinstance(panier, dict):
        raise ValidationError("Le panier doit être un dictionnaire")
    
    for key, item in panier.items():
        try:
            # Validation de la structure de l'item
            if not isinstance(item, dict):
                logger.warning(f"Item {key} ignoré: format invalide")
                continue
                
            valider_item_panier(item)
            
            # Traitement selon le type
            if item['type'] == 'produit':
                try:
                    produit_id = key.split('-')[1]
                    produit = get_object_or_404(Produit, pk=produit_id)
                    
                    produit_data = {
                        'id': produit.id,
                        'nom': produit.nom,
                        'prix': float(item['prix']),
                        'image': produit.image.url if produit.image else '',
                        'type': 'produit',
                    }
                    produits_info.append(produit_data)
                    total_prix += produit_data['prix']
                    items_valides += 1
                    
                except (IndexError, ValueError) as e:
                    logger.error(f"Erreur de format de clé pour l'article {key}: {str(e)}")
                    continue
                    
            elif item['type'] == 'variante':
                try:
                    variante_id = key.split('-')[1]
                    variante = get_object_or_404(Variante, pk=variante_id)
                    
                    variante_data = {
                        'id': variante.id,
                        'nom': f"{variante.produit.nom} - {variante.taille}",
                        'taille': item.get('taille', ''),
                        'couleur': item.get('couleur', ''),
                        'prix': float(item['prix']),
                        'image': variante.image.url if variante.image else variante.produit.image.url if variante.produit.image else '',
                        'type': 'variante',
                    }
                    produits_info.append(variante_data)
                    total_prix += variante_data['prix']
                    items_valides += 1
                    
                except (IndexError, ValueError) as e:
                    logger.error(f"Erreur de format de clé pour la variante {key}: {str(e)}")
                    continue
        
        except ValidationError as e:
            logger.warning(f"Article {key} ignoré: {str(e)}")
            continue
        except Exception as e:
            logger.error(f"Erreur inattendue avec l'article {key}: {str(e)}", exc_info=True)
            continue
    
    if items_valides == 0:
        raise ValidationError("Aucun article valide dans le panier")
    
    return produits_info, round(total_prix, 2)

def recuperer_utilisateur(user_id):
    """ Récupère l'utilisateur avec validation complète. """
    if not user_id or not str(user_id).isdigit():
        raise ValidationError("ID utilisateur invalide")
    
    try:
        return Utilisateur.objects.get(id=user_id)
    except Utilisateur.DoesNotExist:
        logger.error(f"Utilisateur avec l'ID {user_id} non trouvé")
        raise
    except Exception as e:
        logger.error(f"Erreur de base de données lors de la récupération de l'utilisateur: {str(e)}")
        raise

def recuperer_devise(utilisateur):
    """ Récupère la devise avec gestion robuste des erreurs. """
    if not isinstance(utilisateur, Utilisateur):
        raise ValidationError("Utilisateur invalide")
    
    try:
        devise_obj = Devise.objects.filter(utilisateur=utilisateur).first()
        return devise_obj.devise if devise_obj and hasattr(devise_obj, 'devise') else 'GNF'
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la devise: {str(e)}")
        return 'GNF'

def preparer_email(produits_info, total_prix, devise, utilisateur, client_nom, client_numero, lieu_de_livraison, request):
    """ Prépare l'email avec validation complète des données. """
    try:
        # Validation des entrées
        if not all(isinstance(x, (int, float)) for x in [total_prix]):
            raise ValidationError("Données numériques invalides")
            
        if not all(isinstance(x, str) for x in [client_nom, client_numero, lieu_de_livraison]):
            raise ValidationError("Données texte invalides")
            
        if not isinstance(produits_info, list):
            raise ValidationError("Liste de produits invalide")
            
        # Rendu du template
        current_site = get_current_site(request)
        context = {
            'produits_info': produits_info,
            'total_prix': total_prix,
            'devise': devise,
            'client_nom': client_nom,
            'client_numero': client_numero,
            'lieu_de_livraison': lieu_de_livraison,
            'domain': current_site.domain if current_site else 'localhost',
        }
        
        html_message = render_to_string('commande.html', context)
        
        # Préparation de l'email
        subject = 'Nouvelle Commande'
        from_email = settings.EMAIL_HOST_USER
        to_list = [utilisateur.email] if hasattr(utilisateur, 'email') else []
        
        if not to_list:
            raise ValidationError("Adresse email du destinataire manquante")
            
        email = EmailMultiAlternatives(
            subject=subject,
            body=strip_tags(html_message),
            from_email=from_email,
            to=to_list,
        )
        email.attach_alternative(html_message, "text/html")
        
        return email
        
    except Exception as e:
        logger.error(f"Erreur lors de la préparation de l'email: {str(e)}", exc_info=True)
        raise

def verifier_connexion_internet():
    """ Vérifie la connexion internet avec plusieurs méthodes. """
    try:
        # Essai avec différents serveurs pour plus de robustesse
        test_servers = [
            'https://www.google.com',
            'https://www.cloudflare.com',
            'https://1.1.1.1'
        ]
        
        for server in test_servers:
            try:
                urllib.request.urlopen(server, timeout=5)
                return True
            except (URLError, SocketTimeout):
                continue
                
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la connexion: {str(e)}")
        return False

def envoyer_commande(request, user_id):
    """Fonction principale pour envoyer une commande avec gestion complète des erreurs"""
    
    # 1. Vérification de la méthode HTTP
    if request.method != 'POST':
        messages.error(request, "Méthode non autorisée.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    # 2. Vérification connexion internet robuste
    if not verifier_connexion_internet():
        logger.error("Pas de connexion internet disponible")
        messages.error(request, "Veuillez vous connecter à internet pour passer la commande.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # 3. Récupération et validation des données du formulaire
    try:
        client_nom = request.POST.get('name', '').strip()
        client_numero = request.POST.get('phone', '').strip()
        lieu_de_livraison = request.POST.get('lieu_de_livraison', '').strip()

        if not client_nom or len(client_nom) < 2:
            raise ValidationError("Le nom doit contenir au moins 2 caractères")
            
        if not client_numero or len(client_numero) < 8:
            raise ValidationError("Le numéro de téléphone est invalide")
            
        if not lieu_de_livraison or len(lieu_de_livraison) < 5:
            raise ValidationError("Le lieu de livraison est trop court")
            
    except ValidationError as e:
        messages.error(request, str(e))
        return redirect(request.META.get('HTTP_REFERER', '/'))
    except Exception as e:
        logger.error(f"Erreur de validation du formulaire: {str(e)}")
        messages.error(request, "Erreur dans les données du formulaire.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # 4. Traitement principal dans une transaction
    try:
        with transaction.atomic():
            # Récupération du panier
            panier = recuperer_panier(request)
            if panier is None:
                return redirect(request.META.get('HTTP_REFERER', '/'))
            
            # Récupération des infos produits
            produits_info, total_prix = recuperer_produits_info(panier)
            
            # Récupération utilisateur
            utilisateur = recuperer_utilisateur(user_id)
            devise = recuperer_devise(utilisateur)

            # Préparation de l'email
            email = preparer_email(
                produits_info, 
                total_prix, 
                devise, 
                utilisateur,
                client_nom, 
                client_numero, 
                lieu_de_livraison, 
                request
            )

            # Envoi de l'email
            try:
                email.send(fail_silently=False)
            except Exception as e:
                logger.error(f"Échec de l'envoi de l'email: {str(e)}")
                raise Exception("Impossible d'envoyer l'email de confirmation")

            # Création de la commande
            commande = Commande.objects.create(
                utilisateur=utilisateur,
                nom_client=client_nom,
                numero_client=client_numero,
                lieu_de_livraison=lieu_de_livraison,
                html_contenu=render_to_string(
                    "commande-backend.html", 
                    {
                        'produits_info': produits_info,
                        'total_prix': total_prix,
                        'devise': devise,
                        'client_nom': client_nom,
                        'client_numero': client_numero,
                        'lieu_de_livraison': lieu_de_livraison,
                    }
                )
            )
            
            # Enregistrement des ventes
            for produit_info in produits_info:
                try:
                    produit_obj = None
                    image_produit = None

                    if produit_info['type'] == 'produit':
                        produit_obj = Produit.objects.get(pk=produit_info['id'])
                        image = produit_obj.image  # ImageField
                        image_produit = image if image else ''

                    elif produit_info['type'] == 'variante':
                        variante = Variante.objects.get(pk=produit_info['id'])
                        produit_obj = variante.produit  # Récupère le produit parent
                        image_produit = variante.image # Image de la variante

                    if not produit_obj:
                        continue

                    VenteAttente.objects.create(
                        utilisateur=utilisateur,
                        produit=produit_obj,
                        nom_produit=produit_obj.nom,
                        image_produit=image_produit
                    )

                except Exception as e:
                    logger.error(f"Erreur lors de la création de la vente en attente pour {produit_info.get('nom', 'inconnu')}: {str(e)}")
                    continue


            # Nettoyage du panier
            try:
                del request.session['panier']
                del request.session['session_id']
                request.session['compteur_boutique'] = 0
                request.session.modified = True
            except KeyError:
                pass
            except Exception as e:
                logger.error(f"Erreur lors du nettoyage de la session: {str(e)}")

            messages.success(request, "Votre commande a bien été enregistrée.")
            return redirect(request.META.get('HTTP_REFERER'), '/')

    except ValidationError as e:
        logger.warning(f"Erreur de validation: {str(e)}")
        messages.error(request, str(e))
    except Exception as e:
        logger.error(f"Erreur critique lors du traitement de la commande: {str(e)}", exc_info=True)
        messages.error(request, "Une erreur critique est survenue. Veuillez réessayer.")
    
    return redirect(request.META.get('HTTP_REFERER', '/'))