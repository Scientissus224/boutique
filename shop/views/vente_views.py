from django.shortcuts import render, redirect
from django.contrib import messages
from shop.models import Vente, Utilisateur, Produit
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
def vente_list(request):
    if request.session.get('connection') != True:
        messages.error(request, 'Vous devez être connecté pour accéder à vos ventes.')
        return redirect('login')

    utilisateur_id = request.session.get('user_id')
    utilisateur = Utilisateur.objects.get(id=utilisateur_id)

    ventes_en_cours = Vente.objects.filter(utilisateur=utilisateur, statut=False)
    ventes_terminees = Vente.objects.filter(utilisateur=utilisateur, statut=True)

    jour_unique = request.GET.get('jour_unique', '')
    intervalle_jours_debut = request.GET.get('debut_jour', '')
    intervalle_jours_fin = request.GET.get('fin_jour', '')

    mois_debut = request.GET.get('mois_debut', '')  # Ajout pour filtrer par mois de début
    mois_fin = request.GET.get('mois_fin', '')  # Ajout pour filtrer par mois de fin

    filtres_appliques = any([jour_unique, intervalle_jours_debut, intervalle_jours_fin, mois_debut, mois_fin])

    try:
        if jour_unique:
            date_unique = datetime.strptime(jour_unique, '%Y-%m-%d')
            start_of_day = timezone.make_aware(datetime.combine(date_unique, datetime.min.time()))
            end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)
            ventes_terminees = ventes_terminees.filter(date_vente__range=[start_of_day, end_of_day])
        
        elif intervalle_jours_debut or intervalle_jours_fin:
            if intervalle_jours_debut:
                debut_date = datetime.strptime(intervalle_jours_debut, '%Y-%m-%d')
                start_of_day = timezone.make_aware(datetime.combine(debut_date, datetime.min.time()))
                ventes_terminees = ventes_terminees.filter(date_vente__gte=start_of_day)
            if intervalle_jours_fin:
                fin_date = datetime.strptime(intervalle_jours_fin, '%Y-%m-%d')
                end_of_day = timezone.make_aware(datetime.combine(fin_date, datetime.min.time())) + timedelta(days=1) - timedelta(seconds=1)
                ventes_terminees = ventes_terminees.filter(date_vente__lte=end_of_day)

        if mois_debut and mois_fin:
            try:
                mois_debut = datetime.strptime(mois_debut, '%Y-%m')
                mois_fin = datetime.strptime(mois_fin, '%Y-%m')
                ventes_terminees = ventes_terminees.filter(date_vente__gte=mois_debut, date_vente__lte=mois_fin + timedelta(days=31))
            except ValueError:
                messages.error(request, "Les dates de mois saisies ne sont pas valides.")
                return redirect('vente_list')

    except ValueError:
        messages.error(request, "Les dates saisies ne sont pas valides.")
        return redirect('vente_list')

    if not filtres_appliques:
        ventes_terminees = Vente.objects.filter(utilisateur=utilisateur, statut=True)

    # Calcul des totaux
    total_revenu = sum(vente.prix_vente * vente.quantite_vendue for vente in ventes_terminees)
    total_cout = sum(vente.prix_achat * vente.quantite_vendue for vente in ventes_terminees)
    total_profit = total_revenu - total_cout
    total_ventes = sum(vente.quantite_vendue for vente in ventes_terminees)
    pourcentage_profit = round((total_profit / total_revenu) * 100 if total_revenu > 0 else 0, 2)
    

    # Produits les plus vendus
    top_produits = Vente.top_produits(utilisateur, limite=5)

    # # Produits recommandés (avec stock faible)
    # produits_recommandes = Vente.produits_a_recommander(utilisateur, limite=5)
    # Récupérer les 5 produits avec stock faible
    produits_stock_basse = Produit.objects.filter(utilisateur=utilisateur, quantite_stock__lte=5)[:5]


   
    if request.method == 'POST':
        for vente in ventes_en_cours:
            action = request.POST.get(f'action_{vente.id}')

            if action == "supprimer":  # Vérifie si l'action est la suppression
                vente.delete()
                messages.success(request, f'La vente de {vente.produit.nom} a été supprimée avec succès.')
                return redirect('vente_list')  # Redirection après suppression pour éviter les erreurs

            prix_achat = request.POST.get(f'prix_achat_{vente.id}')
            prix_vente = request.POST.get(f'prix_vente_{vente.id}')
            quantite_vendue = request.POST.get(f'quantite_vendue_{vente.id}')

            if prix_achat and prix_vente and quantite_vendue:
                try:
                    vente.prix_achat = Decimal(int(prix_achat))
                    vente.prix_vente = Decimal(int(prix_vente))
                    vente.quantite_vendue = int(quantite_vendue)

                    if vente.quantite_vendue > 0:
                        vente.statut = True

                    vente.save()
                    messages.success(request, f'La vente de {vente.produit.nom} a été mise à jour avec succès.')
                except ValueError:
                    messages.error(request, f"Le stock du produit {vente.produit.nom} est épuisé. Impossible d'effectuer la vente.")
        return redirect('vente_list')


    return render(request, 'vente_list.html', {
        'ventes': ventes_en_cours,
        'total_revenu': total_revenu,
        'total_cout': total_cout,
        'total_profit': total_profit,
        'pourcentage_profit': pourcentage_profit,
        'total_ventes': total_ventes,
        'jour_unique': jour_unique,
        'intervalle_jours_debut': intervalle_jours_debut,
        'intervalle_jours_fin': intervalle_jours_fin,
        'top_produits': top_produits,
        'produits_recommandes':produits_stock_basse,
        'mois_debut': mois_debut,
        'mois_fin': mois_fin,
    })
