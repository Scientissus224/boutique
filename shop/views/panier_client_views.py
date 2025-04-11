from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from shop.models import Produit, Variante
from django.views.decorators.http import require_POST
import logging


def ajouter_produit_au_panier(request, produit_id):
    # Récupérer ou initialiser le panier de la session
    panier = request.session.get('panier', {})
    session_id = request.session.get('session_id', [])
    if not isinstance(session_id, list):  
        session_id = []  # Forcer session_id à être une liste

    # Gestion de l'ajout d'un produit
    produit = get_object_or_404(Produit, id=produit_id)
    produit_key = f"produit-{produit.pk}"
    # Initialiser le compteur_boutique s'il n'existe pas dans la session
    compteur_boutique = request.session.get('compteur_boutique', 0)

    # Vérifier si le produit n'est pas déjà dans le panier
    if produit_key not in panier:
        panier[produit_key] = {
            'nom': produit.nom,
            'quantite': 1,  # Initialisation de la quantité
            'prix': str(produit.prix),
            'image': produit.image.url if produit.image else None,
            'type': 'produit'
        }
        session_id.append(produit.pk)  # Ajouter l'ID à la session_id
        # Incrémenter le compteur_boutique seulement si nouveau produit
        compteur_boutique += 1
        request.session['compteur_boutique'] = compteur_boutique

    # Sauvegarder le panier dans la session
    request.session['panier'] = panier
    request.session['session_id'] = list(set(session_id))  # Éviter les doublons

    # Calculer le nombre total d'articles distincts dans le panier
    total_articles = len(panier)

    # Retourner la somme totale des articles distincts dans le panier
    return JsonResponse({
        'total_articles': total_articles,
        'compteur_boutique': compteur_boutique
    })

def ajouter_variante_au_panier(request, variante_id):
    # Récupérer ou initialiser le panier de la session
    panier = request.session.get('panier', {})
    session_id = request.session.get('session_id', [])
    
    if not isinstance(session_id, list):  
        session_id = []  # Forcer session_id à être une liste

    # Initialiser le compteur_boutique
    compteur_boutique = request.session.get('compteur_boutique', 0)

    # Gestion de l'ajout d'une variante
    variante = get_object_or_404(Variante, id=variante_id)
    variante_key = f"variante-{variante.pk}"

    # Vérifier si la variante est déjà dans le panier
    if variante_key not in panier:
        # Ajouter la variante au panier 
        panier[variante_key] = {
            'taille': variante.taille,
            'couleur': variante.couleur,
            'quantite': 1,  # Initialisation de la quantité
            'prix': str(variante.prix),
            'image': variante.image.url if variante.image else None,
            'type': 'variante'
        }
        session_id.append(variante.pk)
        
        # Incrémenter le compteur seulement si nouvelle variante
        compteur_boutique += 1
        request.session['compteur_boutique'] = compteur_boutique
        
        # Sauvegarder les modifications de session
        request.session['panier'] = panier
        request.session['session_id'] = list(set(session_id))

        return JsonResponse({
            'status': 'added_to_cart',
            'total_articles': len(panier),
            'compteur_boutique': compteur_boutique
        })
    else:
        return JsonResponse({
            'status': 'already_in_cart',
            'total_articles': len(panier),
            'compteur_boutique': compteur_boutique
        })


def retirer_du_panier(request, item_id, item_type):
    # Récupérer le panier et les IDs de session
    panier = request.session.get('panier', {})
    session_id = request.session.get('session_id', [])
    compteur_boutique = request.session.get('compteur_boutique', 0)
    
    # Créer la clé selon le type d'item (produit ou variante)
    item_key = f"{item_type}-{item_id}"
    
    # Vérifier si l'item est dans le panier
    if item_key in panier:
        # Retirer l'item du panier
        del panier[item_key]
        
        # Retirer l'ID de la liste session_id
        if int(item_id) in session_id:
            session_id.remove(int(item_id))
        
        # Décrémenter le compteur_boutique si nécessaire
        if compteur_boutique > 0:
            compteur_boutique -= 1
        
        # Mettre à jour la session
        request.session['panier'] = panier
        request.session['session_id'] = session_id
        request.session['compteur_boutique'] = compteur_boutique
        
        # Retourner une réponse de succès
        return JsonResponse({
            'status': 'removed_from_cart',
            'total_articles': len(panier)
        })
    else:
        # Retourner une réponse si l'item n'était pas dans le panier
        return JsonResponse({
            'status': 'not_in_cart',
            'total_articles': len(panier)
        })

def ajouter_produit_aux_likes(request, produit_id):
    likes = request.session.get('likes', {})
    likes_ids = request.session.get('likes_ids', [])
    
    if not isinstance(likes_ids, list):
        likes_ids = []

    produit = get_object_or_404(Produit, id=produit_id)
    produit_key = str(produit.pk)  # Convertir en string pour la clé de session
    
    if produit_key not in likes:
       
        
        likes[produit_key] = {
            'nom': produit.nom,
            'prix': str(produit.prix),
            'image': produit.image.url if produit.image else None,
            'type': 'produit'
        }
        
        likes_ids.append(produit.pk)
        request.session['compteur_likes'] = request.session.get('compteur_likes', 0) + 1

    request.session['likes'] = likes
    request.session['likes_ids'] = list(set(likes_ids))
    request.session.modified = True

    return JsonResponse({
        'total_likes': len(likes),
        'compteur_likes': request.session.get('compteur_likes', 0)
    })
    

logger = logging.getLogger(__name__)

@require_POST
def retirer_produit_des_likes(request, produit_id):
    # Initialisation avec valeurs par défaut et vérification de type
    likes = request.session.get('likes', {})
    likes_ids = request.session.get('likes_ids', [])
    
    # Conversion en liste si nécessaire (cas où likes_ids serait None ou autre type)
    if not isinstance(likes_ids, list):
        likes_ids = []
        request.session['likes_ids'] = likes_ids

    try:
        produit = get_object_or_404(Produit, id=produit_id)
        produit_key = str(produit.pk)
        produit_id_int = produit.pk  # Version int de l'ID pour likes_ids
        
        # Vérification de l'existence dans les deux structures
        produit_in_likes = produit_key in likes
        produit_in_likes_ids = produit_id_int in likes_ids
        
        if produit_in_likes or produit_in_likes_ids:
            # Suppression dans le dictionnaire likes
            if produit_in_likes:
                likes.pop(produit_key)
            
            # Suppression dans la liste likes_ids (en s'assurant que c'est bien un int)
            if produit_in_likes_ids:
                # Création d'une nouvelle liste sans l'ID à supprimer
                likes_ids = [id for id in likes_ids if id != produit_id_int]
            
            # Mise à jour du compteur (version sécurisée)
            compteur = request.session.get('compteur_likes', 0)
            new_compteur = max(0, compteur - 1)
            request.session['compteur_likes'] = new_compteur
            
            # Mise à jour session et sauvegarde
            request.session['likes'] = likes
            request.session['likes_ids'] = likes_ids
            request.session.modified = True
            
            return JsonResponse({
                'status': 'success',
                'total_likes': len(likes),
                'compteur_likes': new_compteur,
                'message': 'Produit retiré des favoris',
                'removed_from_likes': produit_in_likes,
                'removed_from_likes_ids': produit_in_likes_ids
            })
        else:
            return JsonResponse({
                'status': 'not_found',
                'total_likes': len(likes),
                'compteur_likes': request.session.get('compteur_likes', 0),
                'message': 'Produit non présent dans les favoris'
            }, status=404)

    except Exception as e:
        logger.error(f"Erreur suppression favori {produit_id}: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': 'Erreur serveur',
            'total_likes': len(likes),
            'compteur_likes': request.session.get('compteur_likes', 0)
        }, status=500)