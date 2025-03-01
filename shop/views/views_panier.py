from django.shortcuts import get_object_or_404, render
from shop.models import Produit, Variante, Utilisateur, Devise,Boutique

def afficher_produits_panier(request, utilisateur_id):
    # Récupérer l'utilisateur associé à l'id
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)

    # Récupérer les produits et variantes de cet utilisateur
    produits = Produit.objects.filter(utilisateur=utilisateur)
    variantes = Variante.objects.filter(produit__utilisateur=utilisateur, panier=True)
      # Récupérer la boutique lié à cet utilisateur
    boutique = get_object_or_404(Boutique, utilisateur_id=utilisateur_id)

    produits_avec_variantes = []
    produits_traités = set()  # Pour éviter les doublons de produits

    # Gérer les produits avec `panier=True`
    for produit in produits.filter(panier=True):
        # Récupérer les variantes ayant `panier=True` pour ce produit
        variantes_associees = variantes.filter(produit=produit)

        if variantes_associees.exists():  # Si des variantes sont dans le panier
            produits_avec_variantes.append({
                'produit': produit,
                'variantes': variantes_associees
            })
        else:  # Si aucune variante n'est dans le panier, ajouter uniquement le produit
            produits_avec_variantes.append({
                'produit': produit,
                'variantes': []
            })

        # Marquer le produit comme traité
        produits_traités.add(produit.id)

    # Gérer les variantes seules (produits avec `panier=False`)
    for variante in variantes.exclude(produit__id__in=produits_traités):
        produits_avec_variantes.append({
            'produit': None,  # Pas de produit parent
            'variantes': [variante]
        })

    # Récupérer la devise de l'utilisateur
    devise = Devise.objects.filter(utilisateur=utilisateur).first()
    devise_utilisateur = devise.devise if devise else 'GNF'

    # Passer toutes les informations au template
    context = {
        'produits_panier': produits_avec_variantes,
        'devise': devise_utilisateur,
        'user_id': utilisateur_id,
        'numero':utilisateur.numero,
        'boutique':utilisateur.nom_boutique,
        'boutique_id':boutique.pk,
        'nom_boutique':utilisateur.nom_boutique,
    }

    # Rendu du template 'produits_panier.html' avec le contexte
    return render(request, 'produits_panier.html', context)
