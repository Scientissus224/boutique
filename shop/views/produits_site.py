from django.shortcuts import get_object_or_404, render
from shop.models import Produit, ProduitImage, Variante, Utilisateur, Devise,Boutique

def afficher_produit(request, produit_id, utilisateur_id):
    
    # Récupérer l'utilisateur associé à l'id
    
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
    
    # Récupérer la boutique lié à cet utilisateur
    boutique = get_object_or_404(Boutique, utilisateur_id=utilisateur_id)
    
    # Récupérer le produit lié à cet utilisateur
    produit = get_object_or_404(Produit, id=produit_id, utilisateur=utilisateur)
    
    # Récupérer l'image principale du produit
    image_principale = produit.image.url if produit.image else "https://via.placeholder.com/600x400?text=Image+non+disponible"
    
    # Récupérer les images liées au produit
    images = ProduitImage.objects.filter(produit=produit)
    
    # Extraire les URL des images
    image_urls = [image.image.url for image in images]
    
    # Récupérer les variantes associées au produit
    variantes = Variante.objects.filter(produit=produit)
    
    # Récupérer la devise associée à l'utilisateur
    devise_obj = Devise.objects.filter(utilisateur=utilisateur).first()  # Récupérer la première devise liée à l'utilisateur
    devise = devise_obj.devise if devise_obj else 'GNF'  # Si aucune devise, utiliser 'GNF' comme devise par défaut
    
    # Passer toutes les informations au template
    context = {
        'produit': produit,
        'images': image_urls,  # Passer la liste des URLs des images
        'variantes': variantes,
        'devise': devise,
        'image': image_principale,
        'utilisateur_id': utilisateur_id,
        'boutique_id':boutique.pk,
        'nom_boutique':utilisateur.nom_boutique,
    }
    
    # Rendu du template 'produits_site.html' avec le contexte
    return render(request, 'produits_site.html', context)
