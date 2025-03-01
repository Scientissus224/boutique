from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from shop.models import Produit, Variante, Utilisateur, Devise

def api_produits_panier(request, utilisateur_id):
    # Récupérer l'utilisateur ou renvoyer une erreur 404
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)

    # Récupérer la devise associée (ou GNF par défaut)
    devise = Devise.objects.filter(utilisateur=utilisateur).first()
    devise_utilisateur = devise.devise if devise else 'GNF'

    # Récupérer tous les produits et variantes associés à cet utilisateur
    produits_panier = Produit.objects.filter(utilisateur=utilisateur)
    variantes_panier = Variante.objects.filter(produit__utilisateur=utilisateur, panier=True)

    # Créer une liste d'éléments pour le panier
    items_panier = []

    # Gestion des produits et variantes
    for produit in produits_panier:
        if produit.panier:  # Si le produit est dans le panier
            # Récupérer ses variantes
            variantes = variantes_panier.filter(produit=produit)
            items_panier.append({
                'produit': {
                    'pk': produit.pk,
                    'nom': produit.nom,
                    'prix': produit.prix,
                    'image': produit.image.url if produit.image else None,
                },
                'variantes': [
                    {
                        'pk': variante.pk,
                        'taille': variante.taille,
                        'prix': variante.produit.prix,  # Prix hérité du produit
                        'image': variante.produit.image.url if variante.produit.image else None,
                        'couleur': variante.couleur,
                    }
                    for variante in variantes
                ]
            })
        else:
            # Si le produit n'est pas dans le panier, vérifier ses variantes
            variantes = variantes_panier.filter(produit=produit)
            if variantes.exists():
                items_panier.append({
                    'produit': None,
                    'variantes': [
                        {
                            'pk': variante.pk,
                            'taille': variante.taille,
                            'prix': variante.produit.prix,  # Prix hérité du produit
                            'image': variante.produit.image.url if variante.produit.image else None,
                            'couleur': variante.couleur,
                        }
                        for variante in variantes
                    ]
                })

    # Retourner les données sous forme JSON
    return JsonResponse({
        'items_panier': items_panier,
        'devise': devise_utilisateur,
    })
