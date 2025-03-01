from django.http import JsonResponse, Http404
from shop.models import Variante

def ajouter_au_panier_variante(request, variante_id):
    try:
        # Récupérer la variante
        variante = Variante.objects.get(id=variante_id)

        # Mettre à jour le champ panier
        variante.panier = True
        variante.save(update_fields=['panier'])

        # Retourner une réponse JSON pour informer que l'action a été réussie
        return JsonResponse({'success': True, 'message': 'Variante ajoutée au panier avec succès.'})

    except Variante.DoesNotExist:
        raise Http404("Variante introuvable.")
