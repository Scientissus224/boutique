from django.shortcuts import render, redirect
from shop.models import Boutique, Produit, ProduitImage, SliderImage, Localisation, LocalImages
from shop.forms import BoutiqueUpdateForm
from django.contrib import messages


def check_user_authenticated(request):
    """Vérifie si l'utilisateur est connecté."""
    if not request.user.is_authenticated:
        messages.error(request, "Vous devez être connecté pour gérer votre boutique.")
        return False
    return True


def check_boutique_exists(utilisateur, request):
    """Vérifie si la boutique de l'utilisateur existe."""
    boutique = Boutique.objects.filter(utilisateur=utilisateur).first()
    if not boutique:
        messages.error(request, "Votre boutique n'est pas encore créée. Cliquez sur 'Voir la boutique' dans votre tableau de bord pour la générer.")
        return None
    return boutique


def check_account_validation(statut_validation_compte):
    """Vérifie si le compte de l'utilisateur est validé."""
    if statut_validation_compte in ['attente', 'invalider']:
        return False
    return True


def check_prerequisites_for_publication(utilisateur, request):
    """Vérifie les prérequis avant de publier la boutique."""
    if not Produit.objects.filter(utilisateur=utilisateur).exists():
        messages.error(request, "Vous devez ajouter des produits à votre boutique avant de la publier.")
        return False
    if not ProduitImage.objects.filter(produit__utilisateur=utilisateur).exists():
        messages.error(request, "Ajoutez des images à vos produits pour rendre votre boutique plus attrayante.")
        return False
    if not SliderImage.objects.filter(utilisateur=utilisateur).exists():
        messages.error(request, "Vous devez ajouter des images de slider pour attirer l'attention des clients.")
        return False
    if not Localisation.objects.filter(utilisateur=utilisateur).exists():
        messages.error(request, "Veuillez ajouter une localisation pour votre boutique afin de permettre aux clients de vous trouver.")
        return False
    if not LocalImages.objects.filter(utilisateur=utilisateur).exists():
        messages.error(request, "Ajoutez des images de votre localisation pour renforcer la visibilité de votre boutique.")
        return False
    return True


def gestion_boutique(request):
    """Gestion de la boutique de l'utilisateur."""
    if not check_user_authenticated(request):
        return redirect('login')

    utilisateur = request.user
    boutique = check_boutique_exists(utilisateur, request)
    if not boutique:
        return redirect('table')

    statut_validation_compte = utilisateur.statut_validation_compte

    # Vérification de la validation du compte
    if not check_account_validation(statut_validation_compte):
         messages.error(request, "Votre compte n'est pas validé ou a été invalidé. Contactez le support avant de publier votre boutique.")
         return redirect('table')

    # Vérification des prérequis avant soumission
    if not check_prerequisites_for_publication(utilisateur, request):
        return redirect('table')  # Si les prérequis ne sont pas remplis, rediriger vers la table

    form = BoutiqueUpdateForm(request.POST or None, request.FILES or None, instance=boutique, user=utilisateur)

    if request.method == 'POST':
        if form.is_valid():
            statut_publication = form.cleaned_data.get('statut_publication')

            if statut_publication == "publié":
                boutique.publier = True
                boutique = form.save()
                messages.success(request, "La boutique a été publiée avec succès.")
                return redirect('gestion_boutique')
            elif statut_publication == "chargé":
                boutique = form.save(commit=False)
                boutique.publier = False
                boutique.save()
                messages.success(request, "Les informations de la boutique ont été chargées avec succès.")
                return redirect('gestion_boutique')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    return render(request, 'gestion_boutique.html', {
        'form': form,
        'boutique': boutique,
        'statut_validation_compte': statut_validation_compte,
    })