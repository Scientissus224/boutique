from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render
from shop.models import Boutique,Produit
from django.db.models import Q  # Importer Q pour les requêtes complexes
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string


def home(request):
    """
    Page d'accueil avec boutiques et produits premium - Version robuste
    """
    try:
        # 1. GESTION DES BOUTIQUES
        boutiques_list = Boutique.objects.filter(publier=True).order_by('-id')
        
        # Pagination des boutiques
        page = request.GET.get('page', 1)
        paginator = Paginator(boutiques_list, 10)  # 10 boutique par page
        
        try:
            boutiques_page = paginator.page(page)
        except PageNotAnInteger:
            boutiques_page = paginator.page(1)
        except EmptyPage:
            boutiques_page = paginator.page(paginator.num_pages)

        # Formatage des données des boutiques
        boutiques_data = [{
            "id": boutique.id,
            "description": boutique.titre,
            "logo": boutique.logo.url if boutique.logo else None,
            "page_html_path": reverse('boutique_contenu', args=[boutique.identifiant]),
        } for boutique in boutiques_page]

        # 2. PRODUITS DES BOUTIQUES PREMIUM (version robuste)
        def get_produits_premium():
            try:
                boutiques_premium = Boutique.objects.filter(
                    premium=True,
                    publier=True
                ).order_by('-id')[:6]  # Limite à 6 boutiques premium
                
                produits_data = {
                    'promo': [],
                    'populaire': [],
                    'nouveaute': [],
                    'occasion': [],
                    'reconditionne': [],
                    'neuf': []
                }
                
                for boutique in boutiques_premium:
                    try:
                        # Base QuerySet pour les produits disponibles de la boutique
                        base_query = Produit.objects.filter(
                            utilisateur=boutique.utilisateur,
                            disponible=True
                        )
                        
                        # Remplissage des catégories avec gestion des erreurs
                        for categorie in produits_data.keys():
                            try:
                                filtered = filtrer_produits(
                                    base_query,
                                    request,
                                    force_categorie=categorie
                                )[:8]  # Limite à 8 produits par catégorie
                                
                                produits_data[categorie].extend([{
                                    "id": p.id,
                                    "identifiant":p.identifiant,
                                    'stock':p.quantite_stock,
                                    "nom": p.nom,
                                    "url_boutique": p.get_produit_url(),
                                    "prix": float(p.prix) if p.prix else 0.0,
                                    "pourcentage_reduction": round(((p.ancien_prix - p.prix) / p.ancien_prix) * 100, 2) if p.prix and p.ancien_prix else 0,
                                    "ancien_prix": float(p.ancien_prix) if p.ancien_prix else None,
                                    "image": p.image.url if p.image and hasattr(p.image, 'url') else None,
                                    "boutique_url": reverse('boutique_contenu', args=[boutique.id]),
                                    "produit_url": p.get_produit_url() if hasattr(p, 'get_produit_url') else '#',
                                    "type_produit": p.type_produit if hasattr(p, 'type_produit') else '',
                                    "etat": p.etat if hasattr(p, 'etat') else '',
                                    "date_ajout": p.date_ajout if hasattr(p, 'date_ajout') else None,
                                    "disponible": p.disponible if hasattr(p, 'disponible') else True
                                } for p in filtered])
                            except Exception as e:
                                print(f"Erreur catégorie {categorie}: {str(e)}")
                                continue
                                
                    except Exception as e:
                        print(f"Erreur boutique {boutique.id}: {str(e)}")
                        continue
                
                return produits_data
                
            except Exception as e:
                print(f"Erreur majeure get_produits_premium: {str(e)}")
                return {
                    'promo': [], 'populaire': [], 'nouveaute': [],
                    'occasion': [], 'reconditionne': [], 'neuf': []
                }

        # Fonction de filtrage robuste
        def filtrer_produits(produits_queryset, request, force_categorie=None):
            try:
                categorie = force_categorie if force_categorie else request.GET.get('categorie', 'default')
                search_query = request.GET.get('search', '').strip()
                sort_by = request.GET.get('sort_by', 'default')

                # Filtrage par catégorie avec gestion des erreurs
                try:
                    if categorie == "promo":
                        produits_queryset = produits_queryset.filter(
                            Q(type_produit=Produit.PROMO) | 
                            Q(ancien_prix__isnull=False)
                        )
                    elif categorie == "populaire":
                        produits_queryset = produits_queryset.filter(type_produit=Produit.POPULAIRE)
                    elif categorie == "nouveaute":
                        produits_queryset = produits_queryset.filter(type_produit=Produit.NOUVEAUTE)
                    elif categorie == "occasion":
                        produits_queryset = produits_queryset.filter(etat=Produit.OCCASION)
                    elif categorie == "reconditionne":
                        produits_queryset = produits_queryset.filter(etat=Produit.RECONDITIONNE)
                    elif categorie == "neuf":
                        produits_queryset = produits_queryset.filter(etat=Produit.NEUF)
                    else:
                        produits_queryset = produits_queryset.exclude(type_produit=Produit.PROMO)
                except Exception as e:
                    print(f"Erreur filtrage catégorie: {str(e)}")

                # Filtre de recherche sécurisé
                if search_query:
                    produits_queryset = produits_queryset.filter(
                        Q(nom__icontains=search_query) |
                        Q(description__icontains=search_query) |
                        Q(marque__icontains=search_query) |
                        Q(tags__nom__icontains=search_query)
                    ).distinct()

                # Tri sécurisé
                try:
                    if sort_by == "price-asc":
                        produits_queryset = produits_queryset.order_by('prix')
                    elif sort_by == "price-desc":
                        produits_queryset = produits_queryset.order_by('-prix')
                    elif sort_by == "newest":
                        produits_queryset = produits_queryset.order_by('-date_ajout')
                    elif sort_by == "name-asc":
                        produits_queryset = produits_queryset.order_by('nom')
                    elif sort_by == "name-desc":
                        produits_queryset = produits_queryset.order_by('-nom')
                except Exception as e:
                    print(f"Erreur tri: {str(e)}")
                    produits_queryset = produits_queryset.order_by('-date_ajout')

                return produits_queryset
                
            except Exception as e:
                print(f"Erreur majeure filtrer_produits: {str(e)}")
                return produits_queryset.none()

        # Récupération des produits premium
        produits_premium = get_produits_premium()

        # 3. GESTION AJAX PRODUITS (version robuste)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.GET.get('type') == 'produits':
            def filtrer_produits_liste(liste_produits):
                if not liste_produits:
                    return []
                    
                try:
                    filtered = []
                    for p in liste_produits:
                        try:
                            if not p:
                                continue
                                
                            # Vérification des champs obligatoires
                            if not all(k in p for k in ['id', 'nom', 'prix']):
                                continue
                                
                            filtered.append(p)
                        except Exception as e:
                            print(f"Erreur produit: {str(e)}")
                            continue

                    # Filtre par catégorie
                    categorie = request.GET.get('categorie')
                    if categorie == "promo":
                        filtered = [p for p in filtered if p.get('type_produit') == Produit.PROMO or p.get('ancien_prix') is not None]
                    elif categorie == "populaire":
                        filtered = [p for p in filtered if p.get('type_produit') == Produit.POPULAIRE]
                    elif categorie == "nouveaute":
                        filtered = [p for p in filtered if p.get('type_produit') == Produit.NOUVEAUTE]
                    elif categorie == "occasion":
                        filtered = [p for p in filtered if p.get('etat') == Produit.OCCASION]
                    elif categorie == "reconditionne":
                        filtered = [p for p in filtered if p.get('etat') == Produit.RECONDITIONNE]
                    elif categorie == "neuf":
                        filtered = [p for p in filtered if p.get('etat') == Produit.NEUF]

                    # Filtre de recherche sécurisé
                    search = request.GET.get('search', '').strip()
                    if search:
                        filtered = [p for p in filtered if (
                            search.lower() in p.get("nom", "").lower() or 
                            search.lower() in p.get("description", "").lower() or
                            search.lower() in p.get("marque", "").lower()
                        )]

                    # Tri sécurisé
                    sort_by = request.GET.get('sort_by', 'default')
                    try:
                        if sort_by == "price-asc":
                            filtered.sort(key=lambda x: float(x.get('prix', 0)))
                        elif sort_by == "price-desc":
                            filtered.sort(key=lambda x: float(x.get('prix', 0)), reverse=True)
                        elif sort_by == "newest":
                            filtered.sort(key=lambda x: x.get('date_ajout', ''), reverse=True)
                        elif sort_by == "name-asc":
                            filtered.sort(key=lambda x: x.get('nom', '').lower())
                        elif sort_by == "name-desc":
                            filtered.sort(key=lambda x: x.get('nom', '').lower(), reverse=True)
                    except Exception as e:
                        print(f"Erreur tri: {str(e)}")

                    return filtered
                    
                except Exception as e:
                    print(f"Erreur majeure filtrer_produits_liste: {str(e)}")
                    return []

            try:
                categorie = request.GET.get('categorie')
                produits_html = ""
                default_context = {"produits": []}

                if categorie == 'promo':
                    produits = filtrer_produits_liste(produits_premium.get('promo', []))[:14]
                    produits_html = render_to_string('liste_produits.html', {"produits": produits} or default_context)
                elif categorie == 'populaire':
                    produits = filtrer_produits_liste(produits_premium.get('populaire', []))[:8]
                    produits_html = render_to_string('liste_produits.html', {"produits": produits} or default_context)
                elif categorie == 'nouveaute':
                    produits = filtrer_produits_liste(produits_premium.get('nouveaute', []))[:8]
                    produits_html = render_to_string('liste_produits.html', {"produits": produits} or default_context)
                elif categorie == 'occasion':
                    produits = filtrer_produits_liste(produits_premium.get('occasion', []))[:8]
                    produits_html = render_to_string('liste_produits.html', {"produits": produits} or default_context)
                elif categorie == 'reconditionne':
                    produits = filtrer_produits_liste(produits_premium.get('reconditionne', []))[:8]
                    produits_html = render_to_string('liste_produits.html', {"produits": produits} or default_context)
                elif categorie == 'neuf':
                    produits = filtrer_produits_liste(produits_premium.get('neuf', []))[:8]
                    produits_html = render_to_string('liste_produits.html', {"produits": produits} or default_context)
                else:
                    context = {
                        "produitsPromo": filtrer_produits_liste(produits_premium.get('promo', []))[:14],
                        "produitsPopulaires": filtrer_produits_liste(produits_premium.get('populaire', []))[:8],
                        "produitsNouveautes": filtrer_produits_liste(produits_premium.get('nouveaute', []))[:8],
                        "produitsOccasion": filtrer_produits_liste(produits_premium.get('occasion', []))[:8],
                        "produitsReconditionne": filtrer_produits_liste(produits_premium.get('reconditionne', []))[:8],
                        "produitsNeufs": filtrer_produits_liste(produits_premium.get('neuf', []))[:8],
                    }
                    produits_html = render_to_string('liste_produits.html', context or default_context)
                
                return JsonResponse({"produits_html": produits_html})
                
            except Exception as e:
                print(f"Erreur génération réponse AJAX: {str(e)}")
                return JsonResponse({"error": "Une erreur est survenue"}, status=500)

        # 4. GESTION AJAX BOUTIQUES
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                boutiques_html = render_to_string('boutiques_list.html', {
                    'boutiques': boutiques_data,
                    'num_pages': paginator.num_pages,
                    'current_page': boutiques_page.number,
                    'page_range': list(paginator.page_range),
                })
                return JsonResponse({
                    "boutiques": boutiques_html,
                    "num_pages": paginator.num_pages,
                    "current_page": boutiques_page.number,
                    "page_range": list(paginator.page_range),
                })
            except Exception as e:
                print(f"Erreur boutiques AJAX: {str(e)}")
                return JsonResponse({"error": "Erreur chargement boutiques"}, status=500)

        # 5. CONTEXTE FINAL
        context = {
            "boutiques": boutiques_data,
            "num_pages": paginator.num_pages,
            "current_page": boutiques_page.number,
            "page_range": paginator.page_range,
            "produitsPromo": produits_premium.get('promo', [])[:14],
            "produitsPopulaires": produits_premium.get('populaire', [])[:8],
            "produitsNouveautes": produits_premium.get('nouveaute', [])[:8],
            "produitsOccasion": produits_premium.get('occasion', [])[:8],
            "produitsReconditionne": produits_premium.get('reconditionne', [])[:8],
            "produitsNeufs": produits_premium.get('neuf', [])[:8],
        }

        return render(request, 'home.html', context)
        
    except Exception as e:
        print(f"ERREUR GLOBALE: {str(e)}")
        # Retourner une réponse minimale même en cas d'erreur grave
        return render(request, 'home.html', {
            "boutiques": [],
            "produitsPromo": [],
            "produitsPopulaires": [],
            "produitsNouveautes": [],
            "produitsOccasion": [],
            "produitsReconditionne": [],
            "produitsNeufs": [],
            "error": "Une erreur est survenue"
        })






def rechercher_boutiques_ajax(request):
    """
    Recherche des boutiques selon trois critères (produits_vendus, description, nom_boutique)
    et retourne les résultats en JSON. Si aucune recherche n'est effectuée, retourne 10 boutiques aléatoires.
    """
    try:
        query = request.GET.get('query', '').strip()
        
        # Filtrer les boutiques publiées avec select_related pour optimiser
        boutiques = Boutique.objects.filter(publier=True).select_related('utilisateur')
        
        if query:
            # Recherche insensible à la casse avec indexation
            boutiques = boutiques.filter(
                Q(titre__icontains=query) |
                Q(produits_vendus__icontains=query) |
                Q(utilisateur__nom_boutique__icontains=query)
            ).distinct()
        else:
            # 10 boutiques aléatoires pour plus de variété
            boutiques = boutiques.order_by('?')[:10]

        # Construction de la réponse JSON optimisée
        boutiques_data = [{
            "nom_boutique": boutique.utilisateur.nom_boutique,
            "description": boutique.titre,
            "logo": boutique.logo.url if boutique.logo else None,
            "produits_vendus": boutique.produits_vendus,
            "page_html_path": reverse('boutique_contenu', args=[boutique.identifiant]),
        } for boutique in boutiques]

        # Génération du HTML
        boutiques_modal = render_to_string('boutiques_modal.html', {'boutiques': boutiques_data}, request=request)
        
        return JsonResponse({
            "boutiques_modal": boutiques_modal,
            "boutiques": boutiques_data,
            "count": len(boutiques_data)
        })

    except Exception as e:
        logger.error(f"Erreur recherche boutique: {str(e)}")
        return JsonResponse({"error": "Une erreur est survenue"}, status=500)