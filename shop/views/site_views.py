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

    if not request.session.get('connection'):
        messages.error(request, 'Vous devez être connecté pour gérer votre localisation.')
        return redirect('login')

    utilisateur_id = request.session.get('user_id')
    if not utilisateur_id:
        messages.error(request, "Impossible de récupérer les informations de l'utilisateur.")
        return redirect('login')

    utilisateur = Utilisateur.objects.filter(id=utilisateur_id).first()
    if not utilisateur:
        messages.error(request, "Utilisateur non trouvé.")
        return redirect('login')

    utilisateur_numero = utilisateur.numero
    utilisateur_nom_boutique = utilisateur.nom_boutique
    utilisateur_email = utilisateur.email

    devise = Devise.objects.filter(utilisateur=utilisateur).first()
    devise_utilisateur = devise.devise if devise else 'GNF'

    boutique = Boutique.objects.filter(utilisateur=utilisateur).first()
    logo_boutique = utilisateur.logo_boutique.url if utilisateur and utilisateur.logo_boutique else None

    produits = Produit.objects.filter(utilisateur=utilisateur).exclude(type_produit='Promo')
    produits_mis_en_avant = produits.filter(mise_en_avant='oui')
    
    slider_images = SliderImage.objects.filter(utilisateur=utilisateur)
    images_localisation = LocalImages.objects.filter(utilisateur=utilisateur)[:4]
    localisation_images = [{"url": image.image.url} for image in images_localisation]
    localisation = Localisation.objects.filter(utilisateur=utilisateur).first()
    panier_url = reverse('panier', kwargs={'utilisateur_identifiant': utilisateur.identifiant_unique})
    likes_url = reverse('likes_site', kwargs={'utilisateur_identifiant': utilisateur.identifiant_unique})

    html_contenu = render_to_string("boutique.html", {
        "logo": logo_boutique,
        "products": produits,
        "featured_products": produits_mis_en_avant,
        "slides": slider_images,
        "localisation_images": localisation_images,
        "devise": devise_utilisateur,
        "localisation": localisation,
        "utilisateur_numero": utilisateur_numero,
        "shop_name": utilisateur_nom_boutique,
        "utilisateur_email": utilisateur_email, 
        "panier_url": panier_url,
         "likes_url": likes_url,
        "user_id": utilisateur_id,
    })
    
    max_size = 4294967296
    if len(html_contenu.encode('utf-8')) > max_size:
        messages.error(request, "Le contenu est trop volumineux pour être enregistré.")
    else:
        boutique, created = Boutique.objects.get_or_create(utilisateur=utilisateur)
        boutique.html_contenu = html_contenu
        boutique.produits_vendus = utilisateur.produits_vendus
        boutique.save()
    
    context = {
        "logo": logo_boutique,
        "products": produits,
        "featured_products": produits_mis_en_avant,
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

    return render(request, 'site.html', context)
