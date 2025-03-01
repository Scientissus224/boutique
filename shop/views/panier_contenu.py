from django.http import JsonResponse

def obtenir_panier(request):
    # Récupérer le panier de la session
    panier = request.session.get('panier', {})

    # Calculer le nombre total d'articles en tenant compte des quantités
    total_articles = sum(item['quantite'] for item in panier.values())

    # Retourner le nombre total d'articles dans le panier
    return JsonResponse({
        'total_articles': total_articles  # Nombre total d'articles, incluant les quantités
    })
