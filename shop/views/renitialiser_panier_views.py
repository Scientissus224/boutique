from django.http import JsonResponse

def reinitialiser_panier(request):
    try:
        # Vérifier si le panier existe dans la session
        if 'panier' not in request.session:
            # Si le panier n'existe pas dans la session, renvoyer une erreur
            return JsonResponse({'message': 'Erreur : Aucun panier trouvé dans la session', 'total_articles': 0}, status=400)
        
        # Réinitialiser le panier
        request.session['panier'] = {}
        request.session['session_id'] = {}

        # Retourner un message de confirmation
        return JsonResponse({'message': 'Le panier a été réinitialisé', 'total_articles': 0})

    except Exception as e:
        # En cas d'erreur générale, renvoyer un message d'erreur avec les détails de l'exception
        return JsonResponse({'message': f'Erreur lors de la réinitialisation du panier: {str(e)}', 'total_articles': 0}, status=500)
