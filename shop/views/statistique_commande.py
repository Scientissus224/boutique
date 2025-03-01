from datetime import datetime, timedelta
from django.db.models import Count
from django.shortcuts import render, redirect
from shop.models import Commande
from django.contrib import messages
from django.utils import timezone  # Importer timezone

def statistiques_commandes(request):
    if not request.session.get('connection'):
        messages.error(request, 'Vous devez être connecté pour consulter les statistiques.')
        return redirect('login')

    utilisateur = request.session.get('user_id')
    filter_type = request.GET.get('filter', 'all')

    # Récupérer la date sélectionnée pour filtrer par jour spécifique
    selected_date = request.GET.get('selected_date', None)  # Format : 'YYYY-MM-DD'
    start_date = request.GET.get('start_date', None)  # Date de début personnalisée
    end_date = request.GET.get('end_date', None)  # Date de fin personnalisée

    # Logique de filtrage des commandes en fonction du type de filtre
    if filter_type == 'week':
        start_date = timezone.now() - timedelta(weeks=1)
        commandes = Commande.objects.filter(utilisateur=utilisateur, date_commande__gte=start_date)
    elif filter_type == 'month':
        start_date = timezone.now().replace(day=1)
        commandes = Commande.objects.filter(utilisateur=utilisateur, date_commande__gte=start_date)
    elif filter_type == 'day':
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start.replace(hour=23, minute=59, second=59, microsecond=999999)
        commandes = Commande.objects.filter(utilisateur=utilisateur, date_commande__range=(today_start, today_end))
    elif filter_type == 'date' and selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            start_of_day = timezone.make_aware(datetime.combine(selected_date, datetime.min.time()))
            end_of_day = timezone.make_aware(datetime.combine(selected_date, datetime.max.time()))
            commandes = Commande.objects.filter(utilisateur=utilisateur, date_commande__range=(start_of_day, end_of_day))
        except ValueError:
            commandes = Commande.objects.none()
    elif filter_type == 'custom' and start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            start_of_day = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
            end_of_day = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
            commandes = Commande.objects.filter(utilisateur=utilisateur, date_commande__range=(start_of_day, end_of_day))
        except ValueError:
            commandes = Commande.objects.none()
    else:
        commandes = Commande.objects.filter(utilisateur=utilisateur)

    # Calcul des statistiques de commandes (comme dans le code d'origine)
    total_commandes = commandes.count()
    commandes_livrees = commandes.filter(statut='Livrée').count()
    commandes_annulees = commandes.filter(statut='Annulée').count()
    commandes_en_attente = commandes.filter(statut='En attente').count()
    commandes_en_cours = commandes.filter(statut='En cours').count()

    # Pourcentages
    if total_commandes > 0:
        pourcentage_livrees = (commandes_livrees / total_commandes) * 100
        pourcentage_annulees = (commandes_annulees / total_commandes) * 100
        pourcentage_en_attente = (commandes_en_attente / total_commandes) * 100
        pourcentage_en_cours = (commandes_en_cours / total_commandes) * 100
    else:
        pourcentage_livrees = pourcentage_annulees = pourcentage_en_attente = pourcentage_en_cours = 0

    # Calcul de l'évolution des commandes en fonction du filtre personnalisé
    evolution_livrees = []
    evolution_annulees = []
    months = []
    # Si l'utilisateur a sélectionné une période personnalisée (start_date, end_date)
    if start_date and end_date:
        commandes_months = Commande.objects.filter(
            utilisateur=utilisateur,
            date_commande__range=(start_date, end_date)
        )
        # Calcul des commandes livrées et annulées par mois dans la période
        for month in range(1, 13):
            start_of_month = timezone.make_aware(datetime(datetime.now().year, month, 1))
            end_of_month = timezone.make_aware(datetime(datetime.now().year, month + 1, 1)) if month < 12 else timezone.make_aware(datetime(datetime.now().year + 1, 1, 1))

            livrees_count = commandes_months.filter(statut='Livrée', date_commande__range=(start_of_month, end_of_month)).count()
            annulees_count = commandes_months.filter(statut='Annulée', date_commande__range=(start_of_month, end_of_month)).count()

            evolution_livrees.append(livrees_count)
            evolution_annulees.append(annulees_count)
            months.append(start_of_month.strftime('%b'))  # Ajouter le mois au tableau
    else:
        # Par défaut : calcul des commandes par mois (Janvier - Décembre)
        for month in range(1, 13):
            start_of_month = timezone.make_aware(datetime(datetime.now().year, month, 1))
            end_of_month = timezone.make_aware(datetime(datetime.now().year, month + 1, 1)) if month < 12 else timezone.make_aware(datetime(datetime.now().year + 1, 1, 1))

            livrees_count = Commande.objects.filter(utilisateur=utilisateur, statut='Livrée', date_commande__range=(start_of_month, end_of_month)).count()
            annulees_count = Commande.objects.filter(utilisateur=utilisateur, statut='Annulée', date_commande__range=(start_of_month, end_of_month)).count()

            evolution_livrees.append(livrees_count)
            evolution_annulees.append(annulees_count)
            months.append(start_of_month.strftime('%b'))  # Ajouter le mois au tableau

    # Passer ces données au template
    context = {
        'total_commandes': total_commandes,
        'commandes_livrees': commandes_livrees,
        'commandes_annulees': commandes_annulees,
        'commandes_en_attente': commandes_en_attente,
        'commandes_en_cours': commandes_en_cours,
        'pourcentage_livrees': pourcentage_livrees,
        'pourcentage_annulees': pourcentage_annulees,
        'pourcentage_en_attente': pourcentage_en_attente,
        'pourcentage_en_cours': pourcentage_en_cours,
        'evolution_livrees': evolution_livrees,
        'evolution_annulees': evolution_annulees,
        'months': months,
        'filter_type': filter_type,
        'selected_date': selected_date,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'statistiques_commandes.html', context)
