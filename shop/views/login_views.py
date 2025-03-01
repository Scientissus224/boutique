from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db.models import Q
from shop.models import Utilisateur, Client, InformationsSupplementaires, SupportClient

def login(request):
    if request.method == 'POST':
        # Récupération des informations du formulaire
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Vérification des champs obligatoires
        if not username or not password:
            messages.error(request, 'Veuillez renseigner tous les champs.')
            return redirect('login')

        # Authentifier l'utilisateur (client, utilisateur/boutiquier, support)
        user = authenticate(request, username=username, password=password)
        print(user)

        if user:
            # Vérification si l'utilisateur est actif
            if user.is_active:
                # Connexion sécurisée de l'utilisateur
                auth_login(request, user)

                # Vérification du type d'utilisateur (client, utilisateur/boutiquier, support)
                if isinstance(user, Utilisateur):
                    # Si l'utilisateur est un utilisateur/boutiquier
                    try:
                        # Récupérer les informations supplémentaires de l'utilisateur (boutiquier)
                        infos = InformationsSupplementaires.objects.get(utilisateur=user)

                        # Stockage des données nécessaires dans la session
                        request.session.update({
                            'connection': True,
                            'user_id': user.id,
                            'type_boutique': infos.type_boutique,
                        })

                        messages.success(request, f"Bienvenue, {user.nom_complet} dans votre boutique '{user.nom_boutique}' !")

                        # Redirection en fonction du type de boutique
                        if infos.type_boutique == 'petite':
                            return redirect('table_petite')
                        elif infos.type_boutique == 'croissance':
                            return redirect('table_croissance')
                        elif infos.type_boutique == 'grande':
                            return redirect('table')
                        else:
                            messages.error(request, "Le type de boutique est invalide.")
                            return redirect('login')

                    except InformationsSupplementaires.DoesNotExist:
                        # Aucun enregistrement trouvé pour les informations supplémentaires
                        messages.error(request, "Aucune information supplémentaire associée à votre compte.")
                        return redirect('login')

                elif isinstance(user, Client):
                    # Si l'utilisateur est un client
                    # Stockage des données nécessaires pour le client dans la session
                    request.session.update({
                        'connection': True,
                        'user_id': user.id,
                    })

                    messages.success(request, f"Bienvenue, {user.nom_complet} !")

                    # Redirection vers la page du client
                    return redirect('platForm')
                
                elif isinstance(user, SupportClient):
                    # Si l'utilisateur est un support client
                    # Stockage des données nécessaires pour le support client dans la session
                    request.session.update({
                        'connection': True,
                        'user_id': user.id,
                    })

                    messages.success(request, f"Bienvenue, {user.nom} !")

                    # Redirection vers la page de gestion du statut
                    return redirect('update_status')

            else:
                # Si l'utilisateur est inactif
                messages.error(request, "Votre compte n'est pas encore activé. Veuillez vérifier votre email pour l'activer.")
                return redirect('login')

        else:
            # L'utilisateur n'a pas pu être authentifié (identifiants incorrects)
            messages.error(request, "Identifiants incorrects. Veuillez réessayer.")
            return redirect('login')

    # Si la méthode est GET, rendre la page de connexion
    return render(request, 'login.html')
