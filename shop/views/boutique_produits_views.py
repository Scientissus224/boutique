from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q
from django.urls import reverse
from shop.models import Produit, Utilisateur, Boutique


def obtenir_produits_ajax(request, utilisateur_id):
    """
    Vue AJAX pour récupérer les produits filtrés avec:
    - Calcul robuste de la moyenne des notes
    - Nombre total de commentaires
    - Utilisation de prefetch_related pour optimiser les requêtes
    """
    # Vérification requête AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"error": "Requête invalide"}, status=400)
    
    if request.GET.get('type') != 'produits':
        return JsonResponse({"error": "Type de requête invalide"}, status=400)

    try:
        # Initialisation
        utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
        boutique = get_object_or_404(Boutique, utilisateur=utilisateur)
        categorie = request.GET.get('categorie', 'default')
        page = int(request.GET.get('page', 1))
        sort_by = request.GET.get('sort_by', 'default')
        search_query = request.GET.get('search', '').strip()
        per_page = 12
        
        likes_ids = request.session.get('likes_ids', [])

        # Base QuerySet avec prefetch_related pour les commentaires
        produits = Produit.objects.filter(
            utilisateur=utilisateur,
            disponible=True
        ).prefetch_related('commentaires')

        # Filtrage par catégorie
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
        else:
            produits = produits.exclude(type_produit=Produit.PROMO)

        # Filtre de recherche
        if search_query:
            produits = produits.filter(
                Q(nom__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(marque__icontains=search_query) |
                Q(tags__nom__icontains=search_query)
            ).distinct()

        # Tri
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
        elif sort_by == "rating":
            produits = produits.annotate(
                moyenne_notes=Avg('commentaires__note')
            ).order_by('-moyenne_notes')
        elif sort_by == "reviews":
            produits = produits.annotate(
                nombre_avis=Count('commentaires')
            ).order_by('-nombre_avis')

        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        total_products = produits.count()
        produits_page = produits[start:end]

        # Préparation des données avec calcul des notes et commentaires
        produits_list = []
        for produit in produits_page:
            # Calcul robuste des commentaires et notes comme dans la fonction home
            commentaires = produit.commentaires.all()
            nb_commentaires = commentaires.count()
            
            moyenne_notes = None
            if nb_commentaires > 0:
                notes_valides = [c.note for c in commentaires if c.note is not None]
                if notes_valides:
                    moyenne_notes = round(sum(notes_valides) / len(notes_valides), 1)

            produit_data = {
                "id": produit.id,
                "identifiant": produit.identifiant,
                "nom": produit.nom,
                "url_boutique": produit.get_produit_url(),
                "prix": float(produit.prix) if produit.prix else 0.0,
                "ancien_prix": float(produit.ancien_prix) if produit.ancien_prix else None,
                "image": produit.image.url if produit.image and hasattr(produit.image, 'url') else None,
                "boutique_url": reverse('boutique_contenu', args=[boutique.identifiant]),
                "produit_url": produit.get_produit_url(),
                "is_liked": produit.id in likes_ids,
                "nombre_avis": nb_commentaires,
                "moyenne_notes": moyenne_notes,
                "has_notes": moyenne_notes is not None,
                "marque": produit.marque or '',
                "description": produit.description or '',
                "disponible": produit.disponible if hasattr(produit, 'disponible') else True,
                "quantite_stock": produit.quantite_stock if hasattr(produit, 'quantite_stock') else 0,
                "pourcentage_reduction": round(((produit.ancien_prix - produit.prix) / produit.ancien_prix) * 100, 2) if produit.prix and produit.ancien_prix else 0,
            }
            produits_list.append(produit_data)

        # Contexte pour le template
        context = {
            "produits": produits_list,
            "has_more": total_products > end,
            "total_products": total_products,
            "current_category": categorie,
            "request": request,
        }

        # Rendu
        produits_html = render_to_string('produits_list.html', context)

        return JsonResponse({
            "produits_html": produits_html,
            "has_more": context["has_more"],
            "total_products": context["total_products"]
        })

    except Exception as e:
        # En production, vous devriez logger cette erreur
        return JsonResponse({"error": "Erreur serveur"}, status=500)