from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from shop.models import Produit, Variante
from django.urls import reverse
from decimal import Decimal, InvalidOperation
import logging


logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def obtenir_panier_table(request):
    try:
        panier = request.session.get('panier', {})
        produits_info = []
        total_prix = Decimal('0.00')
        identifiant_boutique = None

        for key, item in panier.items():
            try:
                if item['type'] == 'produit':
                    produit = get_object_or_404(Produit, pk=key.split('-')[1])
                    utilisateur = produit.utilisateur
                    boutique = getattr(utilisateur, "boutique", None)
                    prix = Decimal(str(item['prix']))
                    
                    # Récupération de l'identifiant de la boutique (une seule fois)
                    if boutique is not None:
                        identifiant_boutique = boutique.identifiant
                    else:
                        identifiant_boutique = None  # Ou une valeur par défaut

                    
                    produits_info.append({
                        'id': produit.id,
                        'nom': produit.nom,
                        'prix': str(prix.quantize(Decimal('0.00'))),
                        'image': item.get('image', produit.image.url if produit.image else ''),
                        'url': produit.get_absolute_url(),
                        'type': 'produit'
                    })
                    total_prix += prix

                elif item['type'] == 'variante':
                    variante = get_object_or_404(Variante, pk=key.split('-')[1])
                    prix = Decimal(str(item['prix']))
                    
                    # Récupération de l'identifiant de la boutique (une seule fois)
                    if identifiant_boutique is None and hasattr(variante.produit.utilisateur, 'boutique'):
                        identifiant_boutique = variante.produit.utilisateur.boutique.identifiant
                    
                    produits_info.append({
                        'id': variante.id,
                        'nom': variante.produit.nom,
                        'prix': str(prix.quantize(Decimal('0.00'))),
                        'image': item.get('image', variante.image.url if variante.image else variante.produit.image.url),
                        'url': variante.produit.get_absolute_url(),
                        'type': 'variante'
                    })
                    total_prix += prix

            except Exception as e:
                logger.error(f"Erreur traitement article {key}: {str(e)}")
                continue

        context = {
            'produits': produits_info,
            'total_prix': str(total_prix.quantize(Decimal('0.00'))),
            'panier_vide': len(produits_info) == 0,
            'devise': 'FG',
            'url_boutique':reverse('boutique_contenu', args=[identifiant_boutique]),
            
        }

        panier_html = render_to_string('panier_content.html', context)
        
        return JsonResponse({
            'status': 'success',
            'panier_html': panier_html,
            'data': {
                'articles': produits_info,
                'total': context['total_prix'],
                'devise': context['devise'],
                'boutique_identifiant': identifiant_boutique
            }
        })

    except Exception as e:
        logger.critical(f"Erreur: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Erreur système'
        }, status=500)





logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def obtenir_produits_likes(request):
    response_data = {
        'status': 'success',
        'likes_html': '',
        'data': {'articles': [], 'devise': 'FG', 'count': 0}
    }

    try:
        likes = request.session.get('likes', {})
        
        for produit_id, item in likes.items():
            try:
                produit = get_object_or_404(Produit, pk=int(produit_id))
                likes_ids = request.session.get('session_id', [])
                
                response_data['data']['articles'].append({
                    'id': produit.id,
                    'nom': item.get('nom', produit.nom),
                    'prix': str(Decimal(str(item.get('prix', 0)))),
                    'image': item.get('image', produit.image.url if produit.image else ''),
                    'url': produit.get_absolute_url(),
                    "is_liked": produit.id in likes_ids,
                    'disponible': getattr(produit, 'en_stock', True)
                })

            except Exception as e:
                logger.warning(f"Erreur produit {produit_id}: {str(e)}")
                continue

        response_data['data']['count'] = len(response_data['data']['articles'])
        
        context = {
            'produits': response_data['data']['articles'],
            'likes_vide': not response_data['data']['articles'],
            'devise': 'FG',
            'request': request
        }
        response_data['likes_html'] = render_to_string('likes_content.html', context)

    except Exception as e:
        logger.error(f"Erreur système: {str(e)}", exc_info=True)
        response_data.update({
            'status': 'error',
            'message': str(e)
        })

    return JsonResponse(response_data)