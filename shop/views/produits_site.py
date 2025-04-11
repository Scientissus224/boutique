from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from shop.models import Produit, ProduitImage, Variante, Utilisateur, Devise,Boutique,Localisation

def afficher_produit(request, produit_identifiant, utilisateur_identifiant):
    
    # Récupérer l'utilisateur associé à l'identifiant
    utilisateur = get_object_or_404(Utilisateur, identifiant_unique=utilisateur_identifiant)
    localisation = Localisation.objects.filter(utilisateur=utilisateur).first()
    
    # Récupérer la boutique liée à cet utilisateur
    boutique = get_object_or_404(Boutique, utilisateur_id=utilisateur.id)
    
    # Récupérer le produit lié à cet utilisateur en utilisant l'identifiant UUID
    produit = get_object_or_404(Produit, identifiant=produit_identifiant, utilisateur=utilisateur)
    
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
        'utilisateur_email': utilisateur.email,
        'utilisateur_numero': utilisateur.numero,
        'image': image_principale,
        "localisation": localisation,
        'utilisateur_id': utilisateur.id,
        'boutique_id': boutique.pk,
        "home_boutique": reverse('boutique_contenu', args=[boutique.identifiant]),
        'nom_boutique': utilisateur.nom_boutique,
        'shop_name': utilisateur.nom_boutique,
        'utilisateur_identifiant': utilisateur.identifiant_unique,
        'logo': utilisateur.logo_boutique.url if utilisateur.logo_boutique else "https://via.placeholder.com/600x400?text=Image+non+disponible",
    }
    
    # Rendu du template 'produits_site.html' avec le contexte
    return render(request, 'produits_site.html', context)