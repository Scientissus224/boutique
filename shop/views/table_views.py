from django.shortcuts import render, redirect
from django.contrib import messages
from shop.models import Commande, Utilisateur

def table(request):
    # Récupérer la valeur de connection depuis la session
    connection = request.session.get('connection', False)

    if connection:
        # Récupération de l'utilisateur connecté
        utilisateur_id = request.session.get('user_id')
        if utilisateur_id:
            utilisateur = Utilisateur.objects.filter(id=utilisateur_id).first()
            if utilisateur:
                # Calcul du nombre de commandes liées à l'utilisateur
                nombre_commandes = Commande.objects.filter(utilisateur=utilisateur).count()
            else:
                messages.error(request, "Utilisateur introuvable.")
                return redirect('login')
        else:
            messages.error(request, "Aucune information utilisateur trouvée.")
            return redirect('login')

        # Si l'utilisateur est connecté, afficher la table
        return render(request, 'table.html', {
            'nombre_commandes': nombre_commandes,
            'statut_validation_compte': utilisateur.statut_validation_compte
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