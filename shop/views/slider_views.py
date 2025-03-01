from django.shortcuts import render, redirect , get_object_or_404
from django.contrib import messages
from shop.forms import (

    SliderImageForm,

)

from shop.models import (
    Utilisateur,

    SliderImage,

)




def gestion_slider(request):
    """
    Gère l'ajout d'images de slider pour l'utilisateur connecté.
    Permet également de supprimer des images de slider.
    Inclut la possibilité de rechercher des images par titre.
    """
    if request.session.get('connection') != True:
        messages.error(request, 'Vous devez être connecté pour ajouter ou supprimer vos images de slider.')
        return redirect('login')

    utilisateur_id = request.session.get('user_id')  # Récupérer l'ID de l'utilisateur
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)

    form = SliderImageForm(user=utilisateur)
    
    # Récupérer toutes les images de slider de l'utilisateur
    slider_images = SliderImage.objects.filter(utilisateur=utilisateur)

    # Recherche par titre si un terme est spécifié dans la barre de recherche
    search_text = request.GET.get('search', '')
    if search_text:
        slider_images = slider_images.filter(title__icontains=search_text)
        # Vérifier s'il n'y a pas de résultats après la recherche
        if not slider_images.exists():
            messages.info(request, "Aucune image ne correspond à votre recherche.")

    # Ajouter une image de slider
    if request.method == 'POST' and 'ajouter' in request.POST:
        form = SliderImageForm(request.POST, request.FILES)
        if form.is_valid():
            slider_image = form.save(commit=False)
            slider_image.utilisateur = utilisateur
            slider_image.save()
            messages.success(request, 'Image ajoutée au slider avec succès !')
            return redirect('sliders')  # Rediriger après ajout

    # Supprimer une image de slider
    if request.method == 'POST' and 'delete_slider' in request.POST:
        slider_id = request.POST.get('slider_id')
        if slider_id:
            image = get_object_or_404(SliderImage, id=slider_id)
            image.delete()
            messages.success(request, 'Image supprimée avec succès !')
            return redirect('sliders')  # Rediriger après suppression

    return render(request, 'slider_images.html', {
        'form': form,
        'slider_images': slider_images,
    })
