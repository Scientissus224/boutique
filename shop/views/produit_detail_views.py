from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from shop.forms import ProduitImageForm, VarianteForm
from shop.models import Produit, ProduitImage, Variante, Utilisateur

def detail_produits(request, produit_id):
    """
    Affiche les détails du produit, permet d'ajouter des images et des variantes.
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
    devise_obj = utilisateur.devise.first()  # Récupérer la devise associée à l'utilisateur
    devise = devise_obj.devise if devise_obj else 'GNF'  # Utiliser 'GNF' par défaut si aucune devise n'est associée

    # Récupérer le produit associé à l'utilisateur
    produit = get_object_or_404(Produit, id=produit_id, utilisateur=utilisateur)

    # Initialiser les formulaires
    image_form = ProduitImageForm(request.POST or None, request.FILES or None, utilisateur=utilisateur, produit=produit)
    variante_form = VarianteForm(request.POST or None, request.FILES or None, produit=produit)

    if request.method == 'POST':
        if 'ajout_image' in request.POST:
            # Vérifier que le produit n'a pas déjà 4 images
            if produit.images.count() >= 4:
                messages.error(request, 'Ce produit a déjà 4 images. Vous ne pouvez pas en ajouter plus.')
            elif image_form.is_valid():
                image_form.save()
                messages.success(request, 'Image ajoutée avec succès.')
                return redirect('detail_produits', produit_id=produit.id)
            else:
                messages.error(request, "Une erreur est survenue lors de l'ajout de l'image. Vérifiez que le format est valide (seuls les formats JPG, JPEG et PNG sont autorisés).")

        elif 'supprimer_image' in request.POST:
            image_id = request.POST.get('supprimer_image')
            image = get_object_or_404(ProduitImage, id=image_id, produit=produit)
            image.delete()
            messages.success(request, 'Image supprimée avec succès.')
            return redirect('detail_produits', produit_id=produit.id)

        elif 'ajouter_variante' in request.POST:
            if variante_form.is_valid():
                # Vérifier si les champs du formulaire ne sont pas vides
                if not any(variante_form.cleaned_data.values()):  # Si tous les champs sont vides
                    messages.error(request, 'Le formulaire est vide. Veuillez remplir les champs.')
                else:
                    variante_form.save()
                    messages.success(request, 'Variante ajoutée avec succès.')
                    return redirect('detail_produits', produit_id=produit.id)
            else:
                messages.error(request, 'Une erreur est survenue lors de l\'ajout de la variante.')

        elif 'supprimer_variante' in request.POST:
            variante_id = request.POST.get('supprimer_variante')  # Récupérer l'ID de la variante à supprimer
            if variante_id:
                variante = get_object_or_404(Variante, id=variante_id, produit=produit)
                variante.delete()
                messages.success(request, 'Variante supprimée avec succès.')
                return redirect('detail_produits', produit_id=produit.id)

    # Récupérer les variantes et les images du produit
    variantes = Variante.objects.filter(produit=produit)
    images = ProduitImage.objects.filter(produit=produit)

    # Retourner la page de détails avec les informations
    return render(request, 'detail_produit.html', {
        'produit': produit,
        'image_form': image_form,
        'form': variante_form,
        'variantes': variantes,
        'images': images,
        'devise': devise,  # Passer la devise au template
    })
