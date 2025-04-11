from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from shop.forms import ProduitImageForm, VarianteForm, ProduitForm  # Ajout du ProduitForm
from shop.models import Produit, ProduitImage, Variante, Utilisateur

def detail_produits(request, produit_id):
    """
    Affiche les détails du produit, permet d'éditer le produit, d'ajouter des images et des variantes.
    Vérifie aussi que le nombre d'images ne dépasse pas la limite.
    Permet également de supprimer des images et des variantes du produit.
    """

    # Vérifier si l'utilisateur est connecté
    if not request.session.get('connection'):
        messages.error(request, 'Vous devez être connecté pour gérer vos produits.')
        return redirect('login')

    # Récupérer l'utilisateur connecté
    utilisateur_id = request.session.get('user_id')
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)

    # Récupérer la devise de l'utilisateur
    devise_obj = utilisateur.devise.first()
    devise = devise_obj.devise if devise_obj else 'GNF'

    # Récupérer le produit associé à l'utilisateur
    produit = get_object_or_404(Produit, id=produit_id, utilisateur=utilisateur)

    # Initialiser les formulaires (TOUTE LA LOGIQUE EXISTANTE EST CONSERVÉE)
    image_form = ProduitImageForm(request.POST or None, request.FILES or None, utilisateur=utilisateur, produit=produit)
    variante_form = VarianteForm(request.POST or None, request.FILES or None, produit=produit)
    
    # AJOUT: Formulaire d'édition du produit
    produit_form = ProduitForm(request.POST or None, request.FILES or None, instance=produit, utilisateur=utilisateur)

    if request.method == 'POST':
        # NOUVELLE CONDITION POUR L'ÉDITION DU PRODUIT
        if 'editer_produit' in request.POST:
            if produit_form.is_valid():
                produit_form.save()
                messages.success(request, 'Produit mis à jour avec succès.')
                return redirect('detail_produits', produit_id=produit.id)
            else:
                messages.error(request, 'Erreur lors de la mise à jour du produit.')

        # TOUTE LA LOGIQUE EXISTANTE EST MAINTENUE SANS MODIFICATION
        elif 'ajout_image' in request.POST:
            if produit.images.count() >= 4:
                messages.error(request, 'Ce produit a déjà 4 images. Vous ne pouvez pas en ajouter plus.')
            elif image_form.is_valid():
                image_form.save()
                messages.success(request, 'Image ajoutée avec succès.')
                return redirect('detail_produits', produit_id=produit.id)
            else:
                messages.error(request, "Erreur lors de l'ajout de l'image. Formats acceptés: JPG, JPEG, PNG.")

        elif 'supprimer_image' in request.POST:
            image_id = request.POST.get('supprimer_image')
            image = get_object_or_404(ProduitImage, id=image_id, produit=produit)
            image.delete()
            messages.success(request, 'Image supprimée avec succès.')
            return redirect('detail_produits', produit_id=produit.id)

        elif 'ajouter_variante' in request.POST:
            if variante_form.is_valid():
                if not any(variante_form.cleaned_data.values()):
                    messages.error(request, 'Le formulaire est vide. Veuillez remplir les champs.')
                else:
                    variante_form.save()
                    messages.success(request, 'Variante ajoutée avec succès.')
                    return redirect('detail_produits', produit_id=produit.id)
            else:
                messages.error(request, 'Erreur lors de l\'ajout de la variante.')

        elif 'supprimer_variante' in request.POST:
            variante_id = request.POST.get('supprimer_variante')
            if variante_id:
                variante = get_object_or_404(Variante, id=variante_id, produit=produit)
                variante.delete()
                messages.success(request, 'Variante supprimée avec succès.')
                return redirect('detail_produits', produit_id=produit.id)

    # Récupérer les variantes et les images du produit
    variantes = Variante.objects.filter(produit=produit)
    images = ProduitImage.objects.filter(produit=produit)

    return render(request, 'detail_produit.html', {
        'produit': produit,
        'image_form': image_form,
        'form': variante_form,  # Conservé tel quel pour la compatibilité
        'variante_form': variante_form,  # Ajout pour plus de clarté
        'produit_form': produit_form,  # AJOUT du formulaire d'édition
        'variantes': variantes,
        'images': images,
        'devise': devise,
    })