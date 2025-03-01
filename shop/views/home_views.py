from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render
from shop.models import Boutique,Produit
from django.db.models import Q  # Importer Q pour les requêtes complexes


def home(request):
    """
    Page d'accueil affichant la liste des boutiques publiées et les produits mis en avant des boutiques premium.
    """
    # Récupération des boutiques publiées
    boutiques = Boutique.objects.filter(publier=True)

    # Récupération des produits mis en avant des boutiques premium uniquement
    produits_premium_data = []
    boutiques_data = []

    produits_boutique1 = []
    produits_boutique2 = []
    produits_boutique3 = []
    produits_boutique4 = []
    produits_boutique5 = []
    produits_boutique6 = []

    # Récupérer les 6 premières boutiques premium
    boutiques_premium = Boutique.objects.filter(premium=True).order_by('id')[:6]

    for boutique in boutiques:
        # Ajouter les boutiques normalement
        boutiques_data.append({
            "description": boutique.description,
            "logo": boutique.logo.url if boutique.logo else None,
            "page_html_path": reverse('boutique_contenu', args=[boutique.id]),  # Génère l'URL dynamique
        })

        # Si la boutique est premium, récupérer ses 10 premiers produits mis en avant
        if boutique.premium:
            produits_premium = Produit.objects.filter(
                utilisateur=boutique.utilisateur, 
                mise_en_avant="OUI"  # Filtre sur les produits mis en avant
            ).order_by('id')[:10]

            # Affecter les produits aux bonnes variables en fonction de la boutique
            if boutique == boutiques_premium[0]:
                produits_boutique1 = [
                    {"nom": produit.nom, "prix": produit.prix, "image": produit.image.url if produit.image else None, "boutique_url": reverse('boutique_contenu', args=[boutique.id])} 
                    for produit in produits_premium
                ]
            elif boutique == boutiques_premium[1]:
                produits_boutique2 = [
                    {"nom": produit.nom, "prix": produit.prix, "image": produit.image.url if produit.image else None, "boutique_url": reverse('boutique_contenu', args=[boutique.id])} 
                    for produit in produits_premium
                ]
            elif boutique == boutiques_premium[2]:
                produits_boutique3 = [
                    {"nom": produit.nom, "prix": produit.prix, "image": produit.image.url if produit.image else None, "boutique_url": reverse('boutique_contenu', args=[boutique.id])} 
                    for produit in produits_premium
                ]
            elif boutique == boutiques_premium[3]:
                produits_boutique4 = [
                    {"nom": produit.nom, "prix": produit.prix, "image": produit.image.url if produit.image else None, "boutique_url": reverse('boutique_contenu', args=[boutique.id])} 
                    for produit in produits_premium
                ]
            elif boutique == boutiques_premium[4]:
                produits_boutique5 = [
                    {"nom": produit.nom, "prix": produit.prix, "image": produit.image.url if produit.image else None, "boutique_url": reverse('boutique_contenu', args=[boutique.id])} 
                    for produit in produits_premium
                ]
            elif boutique == boutiques_premium[5]:
                produits_boutique6 = [
                    {"nom": produit.nom, "prix": produit.prix, "image": produit.image.url if produit.image else None, "boutique_url": reverse('boutique_contenu', args=[boutique.id])} 
                    for produit in produits_premium
                ]

    # Récupérer les données de la session si elles existent
    total_produits_ajoutes = request.session.get('total_produits_ajoutes', 0)  # Nombre total de produits ajoutés
    produit_data = request.session.get('produit_data', [])  # Données des produits ajoutés (nom, image, etc.)

    context = {
        "boutiques": boutiques_data,  # Boutiques publiées
        "produits_premium": produits_premium_data,  # Produits mis en avant des boutiques premium
        "produits_boutique1": produits_boutique1,
        "produits_boutique2": produits_boutique2,
        "produits_boutique3": produits_boutique3,
        "produits_boutique4": produits_boutique4,
        "produits_boutique5": produits_boutique5,
        "produits_boutique6": produits_boutique6,
        "total_produits_ajoutes": total_produits_ajoutes,  # Inclure le total des produits ajoutés
        "produit_data": produit_data,  # Inclure les informations des produits
    }

    return render(request, 'home.html', context)



def rechercher_boutiques_ajax(request):
    """
    Recherche des boutiques selon trois critères (produits_vendus, description, nom_boutique) et retourne les résultats en JSON.
    """
    query = request.GET.get('query', '').strip()  # Valeur de la recherche

    # Filtrer les boutiques publiées
    boutiques = Boutique.objects.filter(publier=True)
    
    if query:
        # Rechercher dans les trois champs (produits_vendus, description, nom_boutique)
        boutiques = boutiques.filter(
            Q(description__icontains=query) |
            Q(produits_vendus__icontains=query) |
            Q(utilisateur__nom_boutique__icontains=query)
        )

    # Construction de la réponse JSON
    boutiques_data = []
    for boutique in boutiques:
        boutiques_data.append({
            "nom_boutique": boutique.utilisateur.nom_boutique,
            "description": boutique.description,
            "logo": boutique.logo.url if boutique.logo else None,
            "produits_vendus": boutique.produits_vendus,
            "page_html_path": reverse('boutique_contenu', args=[boutique.id]),
        })
    
    return JsonResponse({"boutiques": boutiques_data})
