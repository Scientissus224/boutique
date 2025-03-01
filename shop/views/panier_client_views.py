from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from shop.models import Produit, Variante

def ajouter_produit_au_panier(request, produit_id):
    # Récupérer ou initialiser le panier de la session
    panier = request.session.get('panier', {})
    session_id = request.session.get('session_id', [])
    if not isinstance(session_id, list):  
        session_id = []  # Forcer session_id à être une liste

    # Gestion de l'ajout d'un produit
    produit = get_object_or_404(Produit, id=produit_id)
    produit_key = f"produit-{produit.pk}"
    # Initialiser le compteur s'il n'existe pas dans la session
    compteur = request.session.get('compteur', 0)

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
        # Incrémenter le compteur
    compteur += 1
    request.session['compteur'] = compteur  # Mise à jour du compteur dans la session

    # Sauvegarder le panier dans la session
    request.session['panier'] = panier
    request.session['session_id'] = list(set(session_id))  # Éviter les doublons

    # Calculer le nombre total d'articles distincts dans le panier
    total_articles = len(panier)

    # Retourner la somme totale des articles distincts dans le panier
    return JsonResponse({'total_articles': total_articles})


def ajouter_variante_au_panier(request, variante_id):
    # Récupérer ou initialiser le panier de la session
    panier = request.session.get('panier', {})
    session_id = request.session.get('session_id', [])
    
    if not isinstance(session_id, list):  
        session_id = []  # Forcer session_id à être une liste

    # Gestion de l'ajout d'une variante
    variante = get_object_or_404(Variante, id=variante_id)
    variante_key = f"variante-{variante.pk}"
     # Initialiser le compteur s'il n'existe pas dans la session
    compteur = request.session.get('compteur', 0)

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
        # Sauvegarder le panier dans la session
         # Incrémenter le compteur
        compteur += 1
        request.session['compteur'] = compteur  # Mise à jour du compteur dans la session
        request.session['panier'] = panier
        request.session['session_id'] = list(set(session_id))

        # Retourner la réponse que la variante a été ajoutée
        return JsonResponse({
            'status': 'added_to_cart',  # Indication que la variante a été ajoutée
            'total_articles': len(panier)  # Nombre total d'articles distincts dans le panier
        })
    else:
        # Retourner la réponse que la variante est déjà dans le panier
        return JsonResponse({
            'status': 'already_in_cart',  # Indication que la variante est déjà dans le panier
            'total_articles': len(panier)  # Nombre total d'articles distincts dans le panier
        })



def retirer_produit_du_panier(request, produit_id):
    """
    Retirer un produit spécifique du panier stocké dans la session.
    """
    # Récupérer ou initialiser le panier depuis la session
    panier = request.session.get('panier', {})
    session_id = request.session.get('session_id', [])

    # Identifier la clé du produit dans le panier
    produit_key = f"produit-{produit_id}"

    if produit_key in panier:
        # Supprimer le produit du panier
        del panier[produit_key]
        
        if produit_id in session_id:  # Vérifie et supprime l'ID
            session_id.remove(produit_id)
         # Mise à jour du compteur (décrémentation)
        compteur = request.session.get('compteur', 0)
        if compteur > 0:
            compteur -= 1  # Décrémenter le compteur
        request.session['compteur'] = compteur
        # Sauvegarder les modifications dans la session
        request.session['panier'] = panier
        request.session['session_id'] = session_id

        # Log pour confirmer la suppression
        print(f"Produit {produit_id} supprimé du panier.")

        # Retourner un succès
        return JsonResponse({
            'status': 'removed_from_cart',
            'total_articles': len(panier),
            'message': f"Le produit {produit_id} a été retiré avec succès."
        })
    else:
        # Log si le produit n'est pas trouvé
        print(f"Produit {produit_id} non trouvé dans le panier.")

        # Retourner une erreur si le produit n'existe pas
        return JsonResponse({
            'status': 'not_found',
            'total_articles': len(panier),
            'message': f"Le produit {produit_id} n'existe pas dans le panier."
        })


def retirer_variante_du_panier(request, variante_id):
    """
    Retirer une variante spécifique du panier stocké dans la session.
    """
    # Récupérer ou initialiser le panier depuis la session
    panier = request.session.get('panier', {})
    session_id = request.session.get('session_id', [])

    # Identifier la clé de la variante dans le panier
    variante_key = f"variante-{variante_id}"

    if variante_key in panier:
        # Supprimer la variante du panier
        del panier[variante_key]
        
        if variante_id in session_id:  # Vérifie et supprime l'ID
            session_id.remove(variante_id)
         # Mise à jour du compteur (décrémentation)
        compteur = request.session.get('compteur', 0)
        if compteur > 0:
            compteur -= 1  # Décrémenter le compteur
        request.session['compteur'] = compteur

        # Sauvegarder les modifications dans la session
        request.session['panier'] = panier
        request.session['session_id'] = session_id

        # Log pour confirmer la suppression
        print(f"Variante {variante_id} supprimée du panier.")

        # Retourner un succès
        return JsonResponse({
            'status': 'removed_from_cart',
            'total_articles': len(panier),
            'message': f"La variante {variante_id} a été retirée avec succès."
        })
    else:
        # Log si la variante n'est pas trouvée
        print(f"Variante {variante_id} non trouvée dans le panier.")

        # Retourner une erreur si la variante n'existe pas
        return JsonResponse({
            'status': 'not_found',
            'total_articles': len(panier),
            'message': f"La variante {variante_id} n'existe pas dans le panier."
        })


def afficher_session_id(request):
    session_id = request.session.get('session_id', [])
    compteur = request.session.get('compteur', 0)
    print(session_id)  # Affichage dans le terminal
    return JsonResponse({'session_id': session_id , 'compteur': compteur})  # Correction du retour JSON