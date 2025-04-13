from django.shortcuts import render, redirect  , get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from shop.forms import (
    DeviseUpdateForm,
    MiseAJourUtilisateurForm,
    MiseAJourLocalisationForm,

)

from shop.models import (
    Utilisateur,
    Localisation,
    Devise,
    Boutique,

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
    boutique = Boutique.objects.filter(utilisateur=utilisateur).first()
    devise_instance, _ = Devise.objects.get_or_create(utilisateur=utilisateur, defaults={'devise': 'GNF'})

    # Données initiales pour l'affichage
    anciennes_localisations = {
        'lien_maps': localisation.lien_maps if localisation else 'Aucune localisation disponible',
        'ville': localisation.ville if localisation else 'N/A',
        'quartier': localisation.quartier if localisation else 'N/A',
        'repere': localisation.repere if localisation else 'N/A',  # Ajout du champ repère
        'ouvert_24h':localisation.ouvert_24h if localisation else 'N/A',
        'heure_ouverture':localisation.heure_ouverture if localisation else 'N/A',
        'heure_fermeture':localisation.heure_fermeture if localisation else 'N/A',
        'ferme_jour_ferie':localisation.ferme_jour_ferie if localisation else 'N/A',
        'jour_ouverture': getattr(localisation, 'jour_ouverture', None) if localisation else None,
        'jour_fermeture': getattr(localisation, 'jour_fermeture', None) if localisation else None,

        
    }
    ancienne_devise = devise_instance.devise
    
    # Initialisation des formulaires
    form = MiseAJourUtilisateurForm(request.POST or None, request.FILES or None, instance=utilisateur)
    form_localisation = MiseAJourLocalisationForm(request.POST or None, instance=localisation)
    form_devise = DeviseUpdateForm(request.POST or None, instance=devise_instance, user=utilisateur)
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
        else:
            messages.error(request, "Une ou plusieurs erreurs se sont produites. Veuillez vérifier vos informations.")

    # Préparation des données pour le template
    current_site = get_current_site(request)
    context = {
        'form': form,
        'form_localisation': form_localisation,
        'form_devise': form_devise,
        'user': {
            'nom': utilisateur.nom_complet,
            'email': utilisateur.email,
            'numero': utilisateur.numero,
            'boutique': utilisateur.nom_boutique,
            'logo': utilisateur.logo_boutique.url if utilisateur.logo_boutique else None,
            'url_boutique': boutique.get_absolute_url(current_site) if boutique else None,
        },
        'localisation': anciennes_localisations,  # Mise à jour des anciennes localisations
        'ancienne_devise': ancienne_devise,
        'jour_ouverture': getattr(localisation, 'jour_ouverture', None) if localisation else None,
        'jour_fermeture': getattr(localisation, 'jour_fermeture', None) if localisation else None,

    }

    return render(request, 'parametres.html', context)
