from django.shortcuts import render, redirect
from django.contrib import messages
from shop.models import Utilisateur

def statut_validation_compte(request):
    # Vérification si l'utilisateur est connecté
    if request.session.get('connection') != True:
        messages.error(request, 'Vous devez être connecté pour voir le statut de validation de votre compte.')
        return redirect('login')

    utilisateur_id = request.session.get('user_id')
    try:
        utilisateur = Utilisateur.objects.get(id=utilisateur_id)
        validation_compte = utilisateur.statut_validation_compte 
    except Utilisateur.DoesNotExist:
        messages.error(request, 'Utilisateur non trouvé.')
        return redirect('login')

    return render(request, 'validation_compte.html', {'validation_compte': validation_compte})
