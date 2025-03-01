from django.shortcuts import render, redirect
from django.contrib import messages
from shop.forms import (
    LocalImagesForm,
    LocalisationForm,
)
from shop.models import (
    Utilisateur,
    Localisation,
    LocalImages,
)

def gestion_localisation(request):
    # Vérification de la connexion de l'utilisateur via la session
    if request.session.get('connection') != True:
        messages.error(request, 'Vous devez être connecté pour gérer votre localisation.')
        return redirect('login')

    # Récupérer l'utilisateur à partir de la session
    utilisateur_id = request.session.get('user_id')
    utilisateur = Utilisateur.objects.get(id=utilisateur_id)

    # Initialisation des variables nécessaires
    form = None
    lien_maps, ville, quartier, repere = None, None, None, None

    # Vérifier si l'utilisateur a déjà une localisation enregistrée
    try:
        localisation = Localisation.objects.get(utilisateur=utilisateur)
        # Récupérer les informations existantes de localisation
        lien_maps = localisation.lien_maps
        ville = localisation.ville
        quartier = localisation.quartier
        repere = localisation.repere  # Récupérer le repère si présent
    except Localisation.DoesNotExist:
        localisation = None
        form = LocalisationForm(request.POST or None, request.FILES or None, user=utilisateur)

    # Gestion de la soumission du formulaire
    if request.method == 'POST':
        # Si un formulaire de localisation est soumis
        if form and form.is_valid():
            form.save()
            messages.success(request, 'Localisation ajoutée avec succès!')
            return redirect('localisation')

        # Gestion des images de localisation (ajout ou suppression)
        image_form = LocalImagesForm(request.POST, request.FILES)

        if image_form.is_valid():
            image = image_form.save(commit=False)
            image.utilisateur = utilisateur
            image.save()
            messages.success(request, "L'image de localisation a été ajoutée avec succès.")
            return redirect('localisation')

        # Suppression d'une image si demandé
        if 'delete_image' in request.POST:
            image_id = request.POST.get('image_id')  # Récupérer l'ID de l'image à supprimer
            if image_id:
                try:
                    image_to_delete = LocalImages.objects.get(id=image_id, utilisateur=utilisateur)
                    image_to_delete.delete()  # Supprimer l'image
                    messages.success(request, "L'image de localisation a été supprimée avec succès.")
                except LocalImages.DoesNotExist:
                    messages.error(request, "L'image spécifiée n'existe pas ou n'appartient pas à cet utilisateur.")
            else:
                messages.error(request, "Aucun ID d'image fourni pour la suppression.")
            return redirect('localisation')

    # Récupérer toutes les images associées à l'utilisateur connecté
    images = LocalImages.objects.filter(utilisateur=utilisateur)

    # Rendre la page avec les informations de localisation et le formulaire d'ajout d'image
    return render(request, 'gestion_localisation.html', {
        'form': form,
        'localisation': localisation,
        'lien_maps': lien_maps,
        'ville': ville,
        'quartier': quartier,
        'repere': repere,
        'images': images,
        'image_form': LocalImagesForm(),
    })
