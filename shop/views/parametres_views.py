from django.shortcuts import render, redirect  , get_object_or_404
from django.contrib import messages
from shop.forms import (
    DeviseUpdateForm,
    MiseAJourUtilisateurForm,
    MiseAJourLocalisationForm,
    NavbarSettingsForm,
    BoutiqueSettingsForm,
    BoutiqueNavCusorForm,

)

from shop.models import (
    Utilisateur,
    Localisation,
    Devise,
    NavbarSettings,
    BoutiqueSettings,
    BoutiqueNavCusor,

)


def parametres(request):
    # Vérification de la connexion utilisateur
    if not request.session.get('connection', False):
        messages.error(request, "Vous devez être connecté pour accéder à cette page.")
        return redirect('login')

    # Récupération de l'utilisateur connecté
    utilisateur_id = request.session.get('user_id')
    if not utilisateur_id:
        messages.error(request, "Impossible de récupérer les informations de l'utilisateur.")
        return redirect('login')
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)

    # Récupération ou initialisation des instances liées à l'utilisateur
    localisation = Localisation.objects.filter(utilisateur=utilisateur).first()
    devise_instance, _ = Devise.objects.get_or_create(utilisateur=utilisateur, defaults={'devise': 'GNF'})
    navbar_instance, _ = NavbarSettings.objects.get_or_create(utilisateur=utilisateur, defaults={'couleur_fond': '#FFFFFF'})
    shop_nom_color_instance, _ = BoutiqueSettings.objects.get_or_create(utilisateur=utilisateur, defaults={'couleur_texte': '#FFFFFF'})
    shop_cursor_nav_instance, _ = BoutiqueNavCusor.objects.get_or_create(utilisateur=utilisateur, defaults={'couleur_texte_cursor': '#000000'})
    
    # Données initiales pour l'affichage
    anciennes_localisations = {
        'lien_maps': localisation.lien_maps if localisation else 'Aucune localisation disponible',
        'ville': localisation.ville if localisation else 'N/A',
        'quartier': localisation.quartier if localisation else 'N/A',
        'repere': localisation.repere if localisation else 'N/A',  # Ajout du champ repère
    }
    ancienne_devise = devise_instance.devise
    ancienne_navbar = navbar_instance.couleur_fond
    ancien_shop_nom_color = shop_nom_color_instance.couleur_texte
    ancien_cursor_nav = shop_cursor_nav_instance.couleur_texte_cursor
    
    # Initialisation des formulaires
    form = MiseAJourUtilisateurForm(request.POST or None, instance=utilisateur)
    form_localisation = MiseAJourLocalisationForm(request.POST or None, instance=localisation)
    form_devise = DeviseUpdateForm(request.POST or None, instance=devise_instance, user=utilisateur)
    form_navbar = NavbarSettingsForm(request.POST or None, instance=navbar_instance, user=utilisateur)
    form_shop_nom_color = BoutiqueSettingsForm(request.POST or None, instance=shop_nom_color_instance, user=utilisateur)
    form_shop_cursor_nav = BoutiqueNavCusorForm(request.POST or None, instance=shop_cursor_nav_instance, user=utilisateur)

    # Traitement des formulaires
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Vos informations personnelles ont été mises à jour avec succès.")
            return redirect('profil')
        elif form_localisation.is_valid():
            localisation = form_localisation.save(commit=False)
            localisation.utilisateur = utilisateur
            localisation.save()
            messages.success(request, "Vos informations de localisation ont été mises à jour avec succès.")
            return redirect('profil')
        elif form_devise.is_valid():
            form_devise.save()
            messages.success(request, "Votre devise a été mise à jour avec succès.")
            return redirect('profil')
        elif form_navbar.is_valid():
            form_navbar.save()
            messages.success(request, "La couleur de votre navbar a été mise à jour avec succès.")
            return redirect('profil')
        elif form_shop_nom_color.is_valid():
            form_shop_nom_color.save()
            messages.success(request, "La couleur du texte de votre boutique a été mise à jour avec succès.")
            return redirect('profil')
        elif form_shop_cursor_nav.is_valid():
            form_shop_cursor_nav.save()
            messages.success(request, "La couleur du curseur de votre boutique a été mise à jour avec succès.")
            return redirect('profil')
        else:
            messages.error(request, "Une ou plusieurs erreurs se sont produites. Veuillez vérifier vos informations.")

    # Préparation des données pour le template
    context = {
        'form': form,
        'form_localisation': form_localisation,
        'form_devise': form_devise,
        'form_navbar': form_navbar,
        'form_shop_nom_color': form_shop_nom_color,
        'form_shop_cursor_nav': form_shop_cursor_nav,
        'user': {
            'nom': utilisateur.nom_complet,
            'email': utilisateur.email,
            'numero': utilisateur.numero,
            'boutique': utilisateur.nom_boutique,
        },
        'localisation': anciennes_localisations,  # Mise à jour des anciennes localisations
        'ancienne_devise': ancienne_devise,
        'ancien_navbar': ancienne_navbar,
        'ancien_shop_nom_color': ancien_shop_nom_color,
        'ancien_cursor_nav': ancien_cursor_nav,
    }

    return render(request, 'parametres.html', context)
