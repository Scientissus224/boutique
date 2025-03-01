from django.http import JsonResponse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse  # Import nécessaire pour générer les liens dynamiques
from shop.models import Produit, Boutique

@receiver(post_save, sender=Produit)
def ajouter_produit(sender, instance, created, **kwargs):
    """
    Fonction appelée dès qu'un produit est ajouté. Vérifie si le produit a été ajouté,
    puis met à jour le compteur dans toutes les boutiques publiées de l'utilisateur.
    """
    if created:
        utilisateur = instance.utilisateur  # L'utilisateur qui a ajouté le produit
        
        # Vérifier les boutiques publiées de cet utilisateur
        boutiques_publiées = Boutique.objects.filter(utilisateur=utilisateur, publier=True)

        if boutiques_publiées.exists():
            produit_data = []
            total_produits_ajoutés = 0
            
            for boutique in boutiques_publiées:
                # Ajouter les données du produit et la boutique associée
                produit_data.append({
                    'nom': instance.nom,
                    'image_url': instance.image.url if instance.image else None,
                    "page_html_path": reverse('boutique_contenu', args=[boutique.id]),  # Utiliser le lien HTML ou le contenu
                })
                
                # Incrémenter le nombre de produits ajoutés pour chaque boutique
                session_key = f"produits_ajoutes_boutique_{boutique.id}"
                produits_ajoutes = utilisateur.session.get(session_key, 0)  # Récupérer le nombre de produits ajoutés dans la session
                utilisateur.session[session_key] = produits_ajoutes + 1  # Incrémenter le produit ajouté
                total_produits_ajoutés += 1

            # Retourner les données du produit et le total des produits ajoutés dans les boutiques publiées
            return JsonResponse({
                'success': True,
                'produit_data': produit_data,
                'total_produits_ajoutés': total_produits_ajoutés
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'L\'utilisateur n\'a pas de boutiques publiées.'
            })

    return JsonResponse({
        'success': False,
        'message': 'Erreur lors de l\'ajout du produit.'
    })
