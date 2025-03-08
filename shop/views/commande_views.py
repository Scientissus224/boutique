from django.core.mail import  EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import redirect, get_object_or_404
from shop.models import Utilisateur, Commande, Produit, Variante, Devise,Vente 
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.utils.html import strip_tags
import logging

# Configuration du logger
logger = logging.getLogger(__name__)

def recuperer_panier(request):
    """ Récupère le panier depuis la session. """
    panier = request.session.get('panier', {})
    if not panier:
        messages.error(request, "Votre panier est vide.")
        return None
    return panier

def recuperer_produits_info(panier):
    """ Récupère les informations des produits et variantes dans le panier. """
    produits_info = []
    total_prix = 0
    for key, item in panier.items():
        if item['type'] == 'produit':
            produit = get_object_or_404(Produit, pk=key.split('-')[1])
            produits_info.append({
                'id': produit.id,
                'nom': produit.nom,
                'prix': item['prix'],
                'image': produit.image,  # Ajouter l'image du produit
                'type': 'produit',
            })
            total_prix += float(item['prix'])
        elif item['type'] == 'variante':
            variante = get_object_or_404(Variante, pk=key.split('-')[1])
            produits_info.append({
                'id': variante.id,
                'nom': f"{variante.produit.nom} - {variante.taille}",
                'taille': item['taille'],
                'couleur': item['couleur'],
                'prix': item['prix'],
                'image': variante.image,  # Ajouter l'image de la variante
                'type': 'variante',
            })
            total_prix += float(item['prix'])
    return produits_info, total_prix


def recuperer_utilisateur(user_id):
    """ Récupère l'utilisateur associé à la commande. """
    return Utilisateur.objects.get(id=user_id)

def recuperer_devise(utilisateur):
    """ Récupère la devise associée à l'utilisateur. """
    devise_obj = Devise.objects.filter(utilisateur=utilisateur).first()
    return devise_obj.devise if devise_obj else 'GNF'

def preparer_email(produits_info, total_prix, devise, utilisateur, client_nom, client_numero, lieu_de_livraison, request):
    """ Prépare et retourne un email sans images et son, avec les informations de la commande. """
    current_site = get_current_site(request)
    # Rendu du template HTML
    html_message = render_to_string('commande.html', {
        'produits_info': produits_info,
        'total_prix': total_prix,
        'devise': devise,
        'client_nom': client_nom,
        'client_numero': client_numero,
        'lieu_de_livraison': lieu_de_livraison,  # Ajout du lieu de livraison
        'domain': current_site,
    })
    subject = 'Nouvelle Commande'
    from_email = settings.EMAIL_HOST_USER
    to_list = [utilisateur.email]
    
    # Créer un email avec plusieurs parties (HTML et texte brut)
    email = EmailMultiAlternatives(subject, strip_tags(html_message), from_email, to_list)
    email.attach_alternative(html_message, "text/html")  # Attacher le message HTML

    return email



def envoyer_commande(request, user_id):
    if request.method == 'POST':
        # Récupérer les données envoyées par le formulaire
        client_nom = request.POST.get('name')
        client_numero = request.POST.get('phone')
        lieu_de_livraison = request.POST.get('lieu_de_livraison')  # Nouveau champ

        # Validation des données
        if not client_nom or not client_numero or not lieu_de_livraison:
            messages.error(request, "Le nom, le numéro de téléphone et le lieu de livraison sont obligatoires.")
            return redirect(request.META.get('HTTP_REFERER'))  # Rediriger vers la même page avec message

        try:
            # Récupérer le panier et les informations des produits
            panier = recuperer_panier(request)
            if panier is None:
                return redirect(request.META.get('HTTP_REFERER'))
            
            produits_info, total_prix = recuperer_produits_info(panier)

            # Récupérer l'utilisateur et la devise
            utilisateur = recuperer_utilisateur(user_id)
            devise = recuperer_devise(utilisateur)

            # Préparer l'email
            email = preparer_email(produits_info, total_prix, devise, utilisateur, client_nom, client_numero, lieu_de_livraison, request)
            
            # Tenter d'envoyer l'email
            if email.send(fail_silently=False):
                # Créer la commande si l'email est envoyé avec succès
                commande = Commande.objects.create(
                    utilisateur=utilisateur,
                    nom_client=client_nom,
                    numero_client=client_numero,
                    lieu_de_livraison=lieu_de_livraison,  # Ajouter le lieu de livraison
                    html_contenu=render_to_string("commande-backend.html", {
                        'produits_info': produits_info,
                        'total_prix': total_prix,
                        'devise': devise,
                        'client_nom': client_nom,
                        'client_numero': client_numero,
                        'lieu_de_livraison': lieu_de_livraison,  # Passer le lieu de livraison au template
                    })
                )

                # Enregistrer les ventes avec uniquement nom et image du produit
                for produit_info in produits_info:
                    Vente.objects.create(
                        utilisateur=utilisateur,
                        produit_id=produit_info['id'],
                        nom_produit=produit_info['nom'],
                        image_produit=produit_info['image']  # Stocke l'image du produit
                    )

                # Vider le panier après l'enregistrement de la commande
                request.session['panier'] = {}
                request.session['session_id'] = []

                messages.success(request, "Votre commande a bien été enregistrée.")
            else:
                messages.error(request, "L'envoi de l'email a échoué. La commande n'a pas été enregistrée.")
                logger.error(f"Échec de l'envoi de l'email pour la commande de {client_nom}")
                return redirect(request.META.get('HTTP_REFERER'))  # Rediriger vers la même page avec message d'erreur
            
            return redirect(request.META.get('HTTP_REFERER'))  # Rediriger vers la même page avec succès

        except Exception as e:
            print(f"Erreur lors de l'envoi de la commande : {e}")
            logger.error(f"Erreur lors de l'envoi de la commande : {e}")
            messages.error(request, "Une erreur est survenue lors de l'enregistrement de la commande. Veuillez réessayer.")
            return redirect(request.META.get('HTTP_REFERER'))  # Rediriger vers la même page avec message d'erreur

    return redirect(request.META.get('HTTP_REFERER'))
