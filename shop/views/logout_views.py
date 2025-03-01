from django.shortcuts import redirect 
from django.contrib import messages
from django.contrib.auth import  logout

def logout_view(request):
    # Déconnexion de l'utilisateur
    logout(request)
    
    # Mettre la variable 'connection' à False dans la session
    request.session['connection'] = False
    
    # Ajouter un message de succès
    messages.success(request, "Vous êtes déconnecté avec succès.")
    
    # Rediriger vers la page de connexion ou une autre page de votre choix
    return redirect('login')  #
