from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from shop.models import Produit, Utilisateur, Devise

def rechercher_produits(request, utilisateur_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Récupérer l'utilisateur
        utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)

        # Récupérer la devise de l'utilisateur connecté
        devise_utilisateur = get_object_or_404(Devise, utilisateur=utilisateur).devise

        # Obtenir les paramètres de recherche depuis la requête GET
        nom_produit = request.GET.get('nom', '').strip()
        prix_min = request.GET.get('prix_min')
        prix_max = request.GET.get('prix_max')

        # Construire la requête de filtrage de base
        produits = Produit.objects.filter(utilisateur=utilisateur)

        if nom_produit:
            produits = produits.filter(nom__icontains=nom_produit)
        
        if prix_min:
            try:
                prix_min = float(prix_min)
                produits = produits.filter(prix__gte=prix_min)
            except ValueError:
                pass
        
        if prix_max:
            try:
                prix_max = float(prix_max)
                produits = produits.filter(prix__lte=prix_max)
            except ValueError:
                pass
        
        # Rendre le template avec les produits filtrés
        produits_html = render_to_string('boutique_produits.html', {"produits": produits, "devise": devise_utilisateur})
        return JsonResponse({"produits_html": produits_html})
    
    return JsonResponse({"error": "Requête invalide"}, status=400)
