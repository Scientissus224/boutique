from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from shop.models import Produit, Variante

def obtenir_panier_table(request):
    # Récupérer le panier depuis la session
    panier = request.session.get('panier', {})

    # Variables pour stocker les informations
    produits_info = []
    total_prix = 0

    # Parcourir le panier pour récupérer les produits
    for key, item in panier.items():
        if item['type'] == 'produit':
            # Récupérer les informations du produit
            produit = get_object_or_404(Produit, pk=key.split('-')[1])
            produits_info.append({
                'id': produit.id,  # Ajouter l'identifiant du produit
                'nom': produit.nom,
                'prix': item['prix'],
                'image': item['image'],
                'type': 'produit',  # Ajouter le type 'produit'
            })
            total_prix += float(item['prix'])  # Ajouter le prix du produit

        elif item['type'] == 'variante':
            # Récupérer les informations de la variante
            variante = get_object_or_404(Variante, pk=key.split('-')[1])
            produits_info.append({
                'id': variante.id,  # Ajouter l'identifiant de la variante
                'nom': f"{variante.produit.nom} - {variante.taille}",  # Affichage combiné produit + variante
                'taille': item['taille'],
                'couleur': item['couleur'],
                'prix': item['prix'],
                'image': item['image'],
                'type': 'variante',  # Ajouter le type 'variante'
            })
            total_prix += float(item['prix'])  # Ajouter le prix de la variante

    # Retourner les informations du panier et la somme totale
    return JsonResponse({
        'produits': produits_info,
        'total_prix': total_prix,
    })
