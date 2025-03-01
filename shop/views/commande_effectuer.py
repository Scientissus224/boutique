from django.utils import timezone
from datetime import datetime
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from shop.models import Commande, Utilisateur

def commandes_utilisateur(request):
    if not request.session.get('connection', False):
        messages.error(request, "Vous devez être connecté pour accéder à cette page.")
        return redirect('login')

    utilisateur_id = request.session.get('user_id')
    if not utilisateur_id:
        messages.error(request, "Impossible de récupérer les informations de l'utilisateur.")
        return redirect('login')

    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)

    # Liste des commandes "supprimées" temporairement (en utilisant la session)
    commandes_supprimees = request.session.get('commandes_supprimees', [])

    if request.method == "POST":
        commande_id = request.POST.get('commande_id')
        action = request.POST.get('action')

        # Action de suppression définitive
        if action == 'supprimer' and commande_id:
            commande = get_object_or_404(Commande, id=commande_id, utilisateur=utilisateur)
            commande.delete()  # Supprimer la commande de la base de données
            messages.success(request, "Commande supprimée définitivement.")
            return redirect('commandes_utilisateur')

        # Logique de changement de statut, déjà présente
        if commande_id and action:
            commande = get_object_or_404(Commande, id=commande_id, utilisateur=utilisateur)
            transitions_valides = {
                'En attente': ['En cours', 'Annulée'],
                'En cours': ['Livrée', 'Annulée'],
                'Livrée': [],
                'Annulée': []
            }

            if action in transitions_valides[commande.statut]:
                commande.statut = action
                commande.save()
                messages.success(request, f"Statut de la commande mis à jour en {action}.")
            else:
                messages.error(request, "Changement de statut invalide.")

            return redirect('commandes_utilisateur')

    # Filtrer les commandes par date (semaine, mois, jour, date spécifique)
    filter_type = request.GET.get('filter', 'all')
    selected_date = request.GET.get('selected_date')  # Date spécifique pour le filtre

    if filter_type == 'week':
        start_date = timezone.now() - timedelta(weeks=1)
        commandes = Commande.objects.filter(utilisateur=utilisateur, date_commande__gte=start_date, statut__in=['En attente', 'En cours'])
    elif filter_type == 'month':
        start_date = timezone.now().replace(day=1)
        commandes = Commande.objects.filter(utilisateur=utilisateur, date_commande__gte=start_date, statut__in=['En attente', 'En cours'])
    elif filter_type == 'day':
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start.replace(hour=23, minute=59, second=59, microsecond=999999)
        commandes = Commande.objects.filter(utilisateur=utilisateur, date_commande__range=(today_start, today_end), statut__in=['En attente', 'En cours'])
    elif filter_type == 'date' and selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            start_of_day = timezone.make_aware(datetime.combine(selected_date, datetime.min.time()))
            end_of_day = timezone.make_aware(datetime.combine(selected_date, datetime.max.time()))
            commandes = Commande.objects.filter(utilisateur=utilisateur, date_commande__range=(start_of_day, end_of_day), statut__in=['En attente', 'En cours'])
        except ValueError:
            commandes = Commande.objects.filter(utilisateur=utilisateur, statut__in=['En attente', 'En cours'])
    else:
        commandes = Commande.objects.filter(utilisateur=utilisateur, statut__in=['En attente', 'En cours'])

    # Exclure les commandes marquées comme supprimées
    commandes = commandes.exclude(id__in=commandes_supprimees)

    commandes = commandes.order_by('-date_commande')
    
    paginator = Paginator(commandes, 10)
    page = request.GET.get('page')
    commandes = paginator.get_page(page)

    nombre_commandes = Commande.objects.filter(utilisateur=utilisateur).count()
    request.session['nombre_commandes'] = nombre_commandes

    return render(request, 'mes_commandes.html', {
        'commandes': commandes,
        'nombre_commandes': nombre_commandes,
        'statut_choices': Commande.STATUT_CHOICES,
    })
