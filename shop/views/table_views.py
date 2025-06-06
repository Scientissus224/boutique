from django.shortcuts import render, redirect
from django.contrib import messages
from shop.models import Commande, Utilisateur ,Boutique, VenteAttente , Produit,SliderImage,Localisation,LocalImages

def table(request):
    # Récupérer la valeur de connection depuis la session
    connection = request.session.get('connection', False)

    if connection:
        # Récupération de l'utilisateur connecté
        utilisateur_id = request.session.get('user_id')
        if utilisateur_id:
            utilisateur = Utilisateur.objects.filter(id=utilisateur_id).first()
            if utilisateur:
                # Calcul du nombre de commandes et de vente non vues par le boutiquier
                nouvelles_ventes = VenteAttente.objects.filter(utilisateur=utilisateur, vue_par_boutiquier=False).count()

                nouvelles_commandes = Commande.objects.filter( utilisateur=utilisateur, statut__in=["En attente", "En cours"]).count()
                produits_stock_critique = Produit.objects.filter(utilisateur=utilisateur, quantite_stock__lte=5).count()
                produits_stock_limite = Produit.objects.filter(utilisateur=utilisateur, quantite_stock__gt=5, quantite_stock__lte=20).count()

                # Récupérer les informations supplémentaires
                nombre_produits = Produit.objects.filter(utilisateur=utilisateur).count()
                nombre_slider_images = SliderImage.objects.filter(utilisateur=utilisateur).count()
                localisation = Localisation.objects.filter(utilisateur=utilisateur).first()
                nombre_local_images =LocalImages.objects.filter(utilisateur=utilisateur).count()
                boutique = Boutique.objects.filter(utilisateur=utilisateur).first()
                html_contenu = boutique.html_contenu if boutique else None
                # Calcul du nombre de jours restants d'essai
                jours_restants = utilisateur.jours_restants_essai  # Utilisation de la propriété
                # Vérification du statut d'essai et désactivation si nécessaire
                utilisateur.verifier_statut_essai()


            else:
                messages.error(request, "Utilisateur introuvable.")
                return redirect('login')
        else:
            messages.error(request, "Aucune information utilisateur trouvée.")
            return redirect('login')

        # Si l'utilisateur est connecté, afficher la table
        return render(request, 'table.html', {
            'nouvelles_commandes': nouvelles_commandes,
            'nouvelles_ventes': nouvelles_ventes,
            'produits_stock_critique': produits_stock_critique,
            'produits_stock_limite': produits_stock_limite,
            'statut_validation_compte': utilisateur.statut_validation_compte,
            'nombre_produits': nombre_produits,
            'nombre_slider_images': nombre_slider_images,
            'localisation': localisation,
            'nombre_local_images': nombre_local_images,
            'boutique': html_contenu if html_contenu else None,
            'jours_restants': jours_restants
        })
    else:
        # Si l'utilisateur n'est pas connecté, rediriger vers la page de connexion
        messages.error(request, "Vous devez vous connecter pour accéder à cette page.")
        return redirect('login')



  
def table_petite(request):
     connection = request.session.get('connection',False)
     
     if connection:
         return render(request, 'table_petite.html')
     else:
         messages.error(request, "Vous devez vous connecter pour accéder à cette page.")
         return redirect('login')
     
def table_croissance(request):
    
    connection = request.session.get('connection',False)
    
    if connection:
        return render(request, 'table_croissance.html')
    else:
        messages.error(request, "Vous devez vous connecter pour accéder à cette page.")
        return redirect('login')
def plat_forme(request):
    return render(request , 'platform.html')