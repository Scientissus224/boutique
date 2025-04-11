from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q
from django.urls import reverse
from shop.models import Produit, Utilisateur, Boutique
from datetime import datetime, timedelta

def obtenir_produits_ajax(request, utilisateur_id):
    """
    Vue AJAX pour récupérer les produits filtrés selon les catégories et états
    avec toutes les données comme dans la vue home
    """
    # Vérification requête AJAX
    if not (request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 
            request.GET.get('type') == 'produits'):
        return JsonResponse({"error": "Requête invalide"}, status=400)

    try:
        # Initialisation des paramètres
        utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
        boutique = get_object_or_404(Boutique, utilisateur=utilisateur)
        categorie = request.GET.get('categorie', 'default')
        page = int(request.GET.get('page', 1))
        sort_by = request.GET.get('sort_by', 'default')
        search_query = request.GET.get('search', '').strip()
        per_page = 12
        
        likes_ids = request.session.get('likes_ids', [])

        # Base QuerySet - produits disponibles uniquement
        produits = Produit.objects.filter(
            utilisateur=utilisateur,
            disponible=True
        )

        # Filtrage par catégorie principale
        if categorie == "promo":
            produits = produits.filter(
                Q(type_produit=Produit.PROMO) | 
                Q(ancien_prix__isnull=False)
            )
        elif categorie == "populaire":
            produits = produits.filter(type_produit=Produit.POPULAIRE)
        elif categorie == "nouveaute":
            produits = produits.filter(type_produit=Produit.NOUVEAUTE)
        elif categorie == "occasion":
            produits = produits.filter(etat=Produit.OCCASION)
        elif categorie == "reconditionne":
            produits = produits.filter(etat=Produit.RECONDITIONNE)
        elif categorie == "neuf":
            produits = produits.filter(etat=Produit.NEUF)
        else:  # Par défaut: tous sauf promos
            produits = produits.exclude(type_produit=Produit.PROMO)

        # Filtre de recherche
        if search_query:
            produits = produits.filter(
                Q(nom__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(marque__icontains=search_query) |
                Q(tags__nom__icontains=search_query)
            ).distinct()

        # Système de tri
        if sort_by == "price-asc":
            produits = produits.order_by('prix')
        elif sort_by == "price-desc":
            produits = produits.order_by('-prix')
        elif sort_by == "newest":
            produits = produits.order_by('-date_ajout')
        elif sort_by == "name-asc":
            produits = produits.order_by('nom')
        elif sort_by == "name-desc":
            produits = produits.order_by('-nom')

        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        total_products = produits.count()
        produits_page = produits[start:end]

        # Préparation des données des produits avec toutes les propriétés
        produits_list = [{
            "id": produit.id,
            "identifiant":produit.identifiant,
            "nom": produit.nom,
            "url_boutique": produit.get_produit_url(),
            "prix": float(produit.prix) if produit.prix else 0.0,
            "pourcentage_reduction": round(((produit.ancien_prix - produit.prix) / produit.ancien_prix) * 100, 2) if produit.prix and produit.ancien_prix else 0,
            "ancien_prix": float(produit.ancien_prix) if produit.ancien_prix else None,
            "image": produit.image.url if produit.image and hasattr(produit.image, 'url') else None,
            "boutique_url": reverse('boutique_contenu', args=[boutique.identifiant]),
            "produit_url": produit.get_produit_url() if hasattr(produit, 'get_produit_url') else '#',
            "type_produit": produit.type_produit if hasattr(produit, 'type_produit') else '',
            "etat": produit.etat if hasattr(produit, 'etat') else '',
            "is_liked": produit.id in likes_ids,  # Info like
            "date_ajout": produit.date_ajout if hasattr(produit, 'date_ajout') else None,
            "disponible": produit.disponible if hasattr(produit, 'disponible') else True
        } for produit in produits_page]

        # Préparation du contexte pour le template
        context = {
            "produits": produits_list,
            "has_more": total_products > end,
            "total_products": total_products,
            "current_category": categorie,
            "request": request,
        }

        # Rendu du template
        produits_html = render_to_string('produits_list.html', context)

        return JsonResponse({
            "produits_html": produits_html,
            "has_more": context["has_more"],
            "total_products": context["total_products"]
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)