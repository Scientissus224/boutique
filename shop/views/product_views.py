from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from shop.forms import ProduitForm
from shop.models import Utilisateur, Produit

def gestion_produits(request):
    # Vérification si l'utilisateur est connecté
    if request.session.get('connection') != True:
        messages.error(request, 'Vous devez être connecté pour ajouter ou supprimer vos produits.')
        return redirect('login')

    utilisateur_id = request.session.get('user_id')
    form = ProduitForm()

    # Récupérer l'utilisateur
    try:
        utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
    except Utilisateur.DoesNotExist:
        messages.error(request, "L'utilisateur spécifié n'existe pas.")
        return redirect('login')

    # Récupérer la devise de l'utilisateur
    devise_obj = utilisateur.devise.first()  # Récupérer l'objet devise associé
    devise = devise_obj.devise if devise_obj else 'GNF'  # Utiliser 'GNF' par défaut si aucune devise n'est associée

    # Initialiser les produits filtrés en fonction de l'utilisateur
    produits = Produit.objects.filter(utilisateur=utilisateur)

    # Récupérer les valeurs des filtres
    availability_filter = request.GET.get('availability', '')
    search_text = request.GET.get('search', '')  # Récupérer la valeur de la barre de recherche
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    etat_filter = request.GET.get('etat', '')  # Filtre pour l'état du produit
    poids_filter = request.GET.get('poids', '')  # Filtre pour le poids
    dimensions_filter = request.GET.get('dimensions', '')  # Filtre pour les dimensions

    # Appliquer les filtres uniquement si des valeurs sont présentes
    filters_applied = False  # Variable pour savoir si des filtres sont appliqués

    if availability_filter:
        filters_applied = True
        if availability_filter == 'disponible':
            produits = produits.filter(disponible=True)
        elif availability_filter == 'indisponible':
            produits = produits.filter(disponible=False)

    if search_text:
        filters_applied = True
        produits = produits.filter(nom__icontains=search_text)  # Filtrage par nom

    if min_price:
        filters_applied = True
        produits = produits.filter(prix__gte=min_price)

    if max_price:
        filters_applied = True
        produits = produits.filter(prix__lte=max_price)

    if etat_filter:
        filters_applied = True
        produits = produits.filter(etat=etat_filter)  # Filtrage par état (Neuf, Occasion, Reconditionné)

    if poids_filter:
        filters_applied = True
        produits = produits.filter(poids__gte=poids_filter)  # Filtrage par poids minimum

    if dimensions_filter:
        filters_applied = True
        produits = produits.filter(dimensions__icontains=dimensions_filter)  # Filtrage par dimensions (ex: "10x20x30")

    # Ajouter un message si aucun produit ne correspond aux critères, mais seulement si des filtres ont été appliqués
    if filters_applied and not produits.exists():
        messages.info(request, "Aucun produit ne correspond aux critères sélectionnés.")

    # Gestion des actions de formulaire pour l'ajout ou la suppression de produits
    if request.method == 'POST':
        if 'ajouter' in request.POST:
            form = ProduitForm(request.POST, request.FILES, utilisateur=utilisateur)  # Passer 'utilisateur' au lieu de 'user'
            if form.is_valid():
                try:
                    produit = form.save(commit=False)
                    produit.utilisateur = utilisateur  # Associer l'utilisateur au produit
                    produit.save()

                    # Ajouter le produit à la liste des produits affichés
                    produits = Produit.objects.filter(utilisateur=utilisateur)  # Rafraîchir la liste des produits

                    messages.success(request, 'Produit ajouté avec succès !')
                    return redirect('produits')  # Redirige après l'ajout du produit
                except Exception as e:
                    messages.error(request, f"Une erreur est survenue lors de l'ajout du produit : {str(e)}")
            
        elif 'supprimer' in request.POST:
            produit_id = request.POST.get('produit_id')
            if produit_id:
                try:
                    produit = get_object_or_404(Produit, id=produit_id)
                    produit.delete()
                    messages.success(request, 'Produit supprimé avec succès !')
                except Exception as e:
                    messages.error(request, f"Une erreur est survenue lors de la suppression du produit : {str(e)}")
            else:
                messages.error(request, "Aucun produit sélectionné pour suppression.")
            return redirect('produits')

    # Rendu du template avec les produits filtrés, la devise et le formulaire
    return render(request, 'gestion_produits.html', {
        'form': form,
        'products': produits,
        'devise': devise,  # Ajouter la devise au contexte
    })
