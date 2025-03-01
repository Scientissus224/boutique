from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from shop.models import Produit, Utilisateur, Devise

def rechercher_produits(request, utilisateur_id):
    # Récupérer l'utilisateur
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)

    # Récupérer la devise de l'utilisateur connecté
    devise_utilisateur = get_object_or_404(Devise, utilisateur=utilisateur).devise

    # Obtenir les paramètres de recherche depuis la requête GET
    nom_produit = request.GET.get('nom', '').strip()  # Nom du produit à rechercher
    prix_min = request.GET.get('prix_min', None)  # Filtre de prix minimum
    prix_max = request.GET.get('prix_max', None)  # Filtre de prix maximum

    # Construire la requête de filtrage de base
    produits = Produit.objects.filter(utilisateur=utilisateur)

    # Appliquer les filtres si des valeurs sont fournies
    if nom_produit:  # Si un nom est fourni, filtrer par nom
        produits = produits.filter(nom__icontains=nom_produit)
    
    if prix_min:  # Si un prix minimum est fourni, filtrer par prix minimum
        try:
            prix_min = float(prix_min)  # Convertir en float pour éviter les erreurs
            produits = produits.filter(prix__gte=prix_min)
        except ValueError:
            pass  # Si le prix minimum est invalide, on ignore ce filtre
    
    if prix_max:  # Si un prix maximum est fourni, filtrer par prix maximum
        try:
            prix_max = float(prix_max)  # Convertir en float pour éviter les erreurs
            produits = produits.filter(prix__lte=prix_max)
        except ValueError:
            pass  # Si le prix maximum est invalide, on ignore ce filtre

    # Si aucun produit n'est trouvé, renvoyer une réponse vide
    if not produits.exists():
        return JsonResponse({'produits': []})

    # Créer une liste de dictionnaires avec les résultats
    resultat = [
        {
            'id': produit.pk,
            'nom': produit.nom,
            'description': produit.description,
            'prix': str(produit.prix),
            'image_url': produit.image.url if produit.image else None,
            'quantite_stock': produit.quantite_stock,
            'url': produit.get_produit_url(),
            'devise': devise_utilisateur,  # Ajouter la devise de l'utilisateur
        }
        for produit in produits
    ]

    # Retourner les résultats sous forme de JSON
    return JsonResponse({'produits': resultat})
