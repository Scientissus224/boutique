from django.http import JsonResponse
from shop.models import Produit

def rechercher_produits(request):
    if request.method == 'GET':
        try:
            # Récupération des paramètres
            search_query = request.GET.get('search_query', '').strip()
            user_id = request.GET.get('user_id', None)

            # Vérification de l'ID utilisateur
            if not user_id:
                return JsonResponse({'error': 'ID utilisateur manquant'}, status=400)

            # Rechercher les produits correspondant
            produits = Produit.objects.filter(
                utilisateur__id=user_id,
                nom__icontains=search_query
            )

            # Construire la réponse JSON
            produits_data = [
                {
                    'nom': produit.nom,
                    'prix': produit.prix,
                    'image': produit.image.url if produit.image else None,
                    'get_produit_url': produit.get_produit_url(),  # Correction ici : appeler la méthode
                }
                for produit in produits
            ]

            return JsonResponse({'products': produits_data, 'devise': '€'})

        except Exception as e:
            # Journaliser l'erreur dans la console
            print(f"Erreur lors de la recherche des produits : {e}")
            return JsonResponse({'error': 'Erreur interne du serveur', 'details': str(e)}, status=500)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
