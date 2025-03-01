from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.urls import reverse
from shop.models import (
    Utilisateur,
    Boutique,
    Produit,
    SliderImage,
    LocalImages,
    Devise,
    Localisation,
)

def site(request):
    """
    Affiche la boutique d'un utilisateur après avoir vérifié sa connexion,
    récupère et génère le contenu dynamique pour la boutique.
    """

    # Vérification de la connexion de l'utilisateur
    if not request.session.get('connection'):
        messages.error(request, 'Vous devez être connecté pour gérer votre localisation.')
        return redirect('login')

    # Récupérer l'ID de l'utilisateur depuis la session
    utilisateur_id = request.session.get('user_id')
    if not utilisateur_id:
        messages.error(request, "Impossible de récupérer les informations de l'utilisateur.")
        return redirect('login')

    # Récupérer l'utilisateur connecté
    utilisateur = Utilisateur.objects.filter(id=utilisateur_id).first()
    if not utilisateur:
        messages.error(request, "Utilisateur non trouvé.")
        return redirect('login')

    # Récupérer les informations de l'utilisateur
    utilisateur_numero = utilisateur.numero
    utilisateur_nom_boutique = utilisateur.nom_boutique
    utilisateur_email = utilisateur.email

    # Récupérer la devise de l'utilisateur, avec 'GNF' par défaut
    devise = Devise.objects.filter(utilisateur=utilisateur).first()
    devise_utilisateur = devise.devise if devise else 'GNF'

    # Récupérer tous les produits associés à l'utilisateur
    produits = Produit.objects.filter(utilisateur=utilisateur)

    # Récupérer uniquement les produits mis en avant
    produits_mis_en_avant = produits.filter(mise_en_avant='oui')

    # Récupérer les images du slider
    slider_images = SliderImage.objects.filter(utilisateur=utilisateur)

    # Récupérer les images de localisation et s'assurer que l'URL est correcte
    images_localisation = LocalImages.objects.filter(utilisateur=utilisateur)[:4]

    # Préparer une liste avec les URLs pour faciliter l'affichage dans le template
    localisation_images = [{"url": image.image.url} for image in images_localisation]

    # Récupérer la localisation principale de l'utilisateur
    localisation = Localisation.objects.filter(utilisateur=utilisateur).first()

    # Utilisez uniquement 'utilisateur_id' pour générer l'URL
    panier_url = reverse('panier', kwargs={'utilisateur_id': utilisateur_id})

    # Générer le contenu HTML de la boutique avec les données collectées
    html_contenu = render_to_string("boutique.html", {
        "logo": None,  # Vous pouvez gérer le logo ici
        "products": produits,
        "featured_products": produits_mis_en_avant,  # Produits mis en avant
        "slides": slider_images,
        "localisation_images": localisation_images,
        "devise": devise_utilisateur,
        "localisation": localisation,
        "utilisateur_numero": utilisateur_numero,
        "shop_name": utilisateur_nom_boutique,
        "utilisateur_email": utilisateur_email, 
        "panier_url": panier_url,
        "user_id": utilisateur_id,
    })
    

    # Vérification de la taille du contenu avant de l'enregistrer
    max_size = 4294967296  # Limite de taille en octets (4 Go)
    if len(html_contenu.encode('utf-8')) > max_size:
        messages.error(request, "Le contenu est trop volumineux pour être enregistré.")
    else:
        # Récupérer ou créer la boutique de l'utilisateur
        boutique, created = Boutique.objects.get_or_create(utilisateur=utilisateur)
        
        # Mettre à jour le contenu HTML de la boutique
        boutique.html_contenu = html_contenu
        boutique.produits_vendus = utilisateur.produits_vendus
        boutique.save()
    
    context = {
         "logo": None,  # Vous pouvez gérer le logo ici
        "products": produits,
        "featured_products": produits_mis_en_avant,  # Produits mis en avant
        "slides": slider_images,
        "localisation_images": localisation_images,
        "devise": devise_utilisateur,
        "localisation": localisation,
        "utilisateur_numero": utilisateur_numero,
        "shop_name": utilisateur_nom_boutique,
        "utilisateur_email": utilisateur_email, 
        "panier_url": panier_url,
        "user_id": utilisateur_id,
        
      }

    # Rendre la page sans passer les données supplémentaires
    return render(request, 'site.html', context)
