from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from shop.models import Produit, Variante, Utilisateur, Devise, Localisation, Boutique


def afficher_produits_panier(request, utilisateur_identifiant):
    """
    Affiche les produits du panier pour un utilisateur donné.
    
    Args:
        request: Objet HttpRequest
        utilisateur_identifiant (str): Identifiant unique de l'utilisateur
        
    Returns:
        HttpResponse: Rendu du template avec les produits du panier
    """
    # Récupération de l'utilisateur et vérification d'existence
    utilisateur = get_object_or_404(Utilisateur, identifiant_unique=utilisateur_identifiant)
    boutique = get_object_or_404(Boutique, utilisateur__identifiant_unique=utilisateur_identifiant)
    
    # Récupération des données supplémentaires
    localisation = Localisation.objects.filter(utilisateur=utilisateur).first()
    
    # Construction du contexte
    context = {
        'utilisateur_email': utilisateur.email,
        'shop_name': utilisateur.nom_boutique,
        'user_id': utilisateur.id,
        'numero': utilisateur.numero,
        'logo': utilisateur.logo_boutique.url if utilisateur.logo_boutique else None,
        "localisation": localisation,
        'boutique': utilisateur.nom_boutique,
        'boutique_id': boutique.pk,
        "home_boutique": reverse('boutique_contenu', args=[boutique.identifiant]),
        'utilisateur_numero': utilisateur.numero,
        'utilisateur_identifiant': utilisateur_identifiant
    }

    return render(request, 'produits_panier.html', context)


def likes_site(request, utilisateur_identifiant):
    """
    Affiche la page des likes du site pour un utilisateur donné.
    
    Args:
        request: Objet HttpRequest
        utilisateur_identifiant (str): Identifiant unique de l'utilisateur
        
    Returns:
        HttpResponse: Rendu du template avec les likes du site
    """
    # Récupérer l'utilisateur associé à l'id
    utilisateur = get_object_or_404(Utilisateur, identifiant_unique=utilisateur_identifiant)
    
    # Récupérer la boutique liée à cet utilisateur
    boutique = get_object_or_404(Boutique, utilisateur_id=utilisateur.id)
    localisation = Localisation.objects.filter(utilisateur=utilisateur).first()
    
    # Récupérer la devise de l'utilisateur
    devise = Devise.objects.filter(utilisateur=utilisateur).first()
    devise_utilisateur = devise.devise if devise else 'GNF'
    
    # Préparer le contexte avec les informations de l'utilisateur
    context = {
        'utilisateur_email': utilisateur.email,
        'utilisateur_numero': utilisateur.numero,
        'shop_name': utilisateur.nom_boutique,
        'logo': utilisateur.logo_boutique.url if utilisateur.logo_boutique else None,
        'devise': devise_utilisateur,
        "localisation": localisation,
        'user_id': utilisateur.id,
        'boutique_id': boutique.pk,
        "home_boutique": reverse('boutique_contenu', args=[boutique.identifiant]),
        'utilisateur_identifiant': utilisateur.identifiant_unique
    }
    
    # Rendu du template avec le contexte
    return render(request, 'likes_site.html', context)