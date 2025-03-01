from django.http import JsonResponse
from shop.models import Utilisateur, Produit, Variante

def count_panier_utilisateur(user_id):
    total_panier = 0
    try:
        utilisateur = Utilisateur.objects.get(id=user_id)
    except Utilisateur.DoesNotExist:
        return 0

    # Récupérer les produits avec panier=True
    produits_panier = Produit.objects.filter(utilisateur=utilisateur, panier=True)

    # Ajouter le nombre de produits ayant panier=True
    total_panier += produits_panier.count()

    # Compter les variantes des produits avec panier=True
    for produit in produits_panier:
        variantes = Variante.objects.filter(produit=produit, panier=True)
        total_panier += variantes.count()

    # Récupérer les produits avec panier=False
    produits_sans_panier = Produit.objects.filter(utilisateur=utilisateur, panier=False)

    # Compter les variantes des produits avec panier=False ayant panier=True
    for produit in produits_sans_panier:
        variantes = Variante.objects.filter(produit=produit, panier=True)
        total_panier += variantes.count()

    return total_panier

# Vue pour obtenir le total panier
def get_total_panier(request, user_id):
    total_panier = count_panier_utilisateur(user_id)
    return JsonResponse({'total_panier': total_panier})
