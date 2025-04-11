from django.http import JsonResponse

def obtenir_panier(request):
    # Récupérer le compteur d'articles depuis la session (mettre 0 si absent)
    total_articles = request.session.get('compteur_boutique', 0)

    # Retourner le nombre total d'articles dans le panier
    return JsonResponse({
        'total_articles': total_articles
    })
    
def obtenir_like(request):
    # Récupérer le compteur de likes depuis la session (mettre 0 si absent)
    total_likes = request.session.get('compteur_likes', 0)

    # Retourner le nombre total de likes
    return JsonResponse({
        'total_likes': total_likes
    })

def reinitialiser_compteurs(request):
    # Réinitialiser les compteurs
    request.session['compteur_boutique'] = 0
    request.session['compteur_likes'] = 0
    
    # Réinitialiser le panier, les likes et les likes_ids
    request.session['session_id'] = []
    request.session['panier'] = {}
    request.session['likes'] = {}
    request.session['likes_ids'] = []
    
    # Retourner une réponse de confirmation
    return JsonResponse({
        'status': 'success',
        'compteur_boutique': 0,
        'compteur_likes': 0,
        'session_id': request.session['session_id'],
        'panier': request.session['panier'],
        'likes': request.session['likes'],
        'likes_ids': request.session['likes_ids']
    })