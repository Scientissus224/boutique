from django.http import JsonResponse
from shop.models import Produit, Devise

def produits_sans_variante(request, utilisateur_id):
    # Récupérer tous les produits de l'utilisateur
    produits = Produit.objects.filter(utilisateur_id=utilisateur_id)
    
    # Récupérer la devise de l'utilisateur
    devise_utilisateur = Devise.objects.filter(utilisateur_id=utilisateur_id).first()
    devise = devise_utilisateur.devise if devise_utilisateur else 'GNF'  # Valeur par défaut si la devise n'est pas trouvée
    
    # Créer une liste de dictionnaires avec les informations des produits
    produits_data = [{
        'id': produit.id,
        'nom': produit.nom,
        'prix': str(produit.prix),
        'image': produit.image.url if produit.image else None,
        'url': produit.get_produit_url(),  # Utilisation de la méthode get_produit_url()
        'a_variante': produit.variantes.exists()  # Indique si le produit a des variantes
    } for produit in produits]
    
    # Retourner une réponse JSON avec les produits et la devise
    return JsonResponse({'status': 'ok', 'produits': produits_data, 'devise': devise})

