from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from shop.models import Produit

def mise_a_jour_quantite(request):
    if request.session.get('connection') != True:
        messages.error(request, 'Vous devez être connecté pour accéder à vos ventes.')
        return redirect('login')
    
    utilisateur = request.user  # Supposant que l'utilisateur est authentifié
    produits = Produit.objects.filter(utilisateur=utilisateur)
    
    filtre = request.GET.get('filtre', 'tous')  # 'tous' par défaut pour afficher tous les produits
    recherche = request.GET.get('recherche', '')
    
    if recherche:
        produits = produits.filter(nom__icontains=recherche)
    
    if filtre == 'sup20':
        produits = produits.filter(quantite_stock__gte=20)
    elif filtre == 'inf20':
        produits = produits.filter(quantite_stock__lt=20)
    elif filtre == 'inf5':
        produits = produits.filter(quantite_stock__lte=5)
    elif filtre == 'tous':  # Ajout de la condition pour tous les produits
        produits = produits.all()
    
    if request.method == 'POST':
        produit_id = request.POST.get('produit_id')
        nouvelle_quantite = request.POST.get('quantite_stock')
        
        if produit_id and nouvelle_quantite:
            produit = get_object_or_404(Produit, id=produit_id, utilisateur=utilisateur)
            try:
                nouvelle_quantite = int(nouvelle_quantite)
                produit.quantite_stock = nouvelle_quantite
                
                # Mise à jour de la disponibilité du produit
                if produit.quantite_stock == 0:
                    produit.disponible = False
                else:
                    produit.disponible = True
                
                produit.save()
                messages.success(request, 'Quantité mise à jour avec succès.')
            except ValueError:
                messages.error(request, "Veuillez entrer une valeur valide pour la quantité.")
        
        return redirect('update_quantite')
    
    return render(request, 'gestion_stocke.html', {'produits': produits})
