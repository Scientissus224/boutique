from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from datetime import datetime, timedelta
from shop.models import Utilisateur, SupportClient, Produit,Boutique,Abonnement,HistoriqueAbonnement
from django.db.models import Count, Q, Sum
from shop.forms import ProduitForm  # Supposons que vous avez un formulaire ProduitForm
from django.urls import reverse
from urllib.parse import quote





def update_utilisateur_status(request):
    # Vérification de la connexion
    if request.session.get('connection') != True:
        messages.error(request, 'Vous devez être connecté pour accéder à cette page.')
        return redirect('login')

    # Récupération du personnel support
    personnel_support_id = request.session.get('user_id')
    if not personnel_support_id:
        messages.error(request, 'Utilisateur non trouvé dans la session.')
        return redirect('login')

    supportClient = get_object_or_404(SupportClient, id=personnel_support_id)

    if supportClient.validation_compte == 'non accordé':
        messages.error(request, "Vous n'êtes pas autorisé à valider ou invalider les comptes clients.")
        return redirect('login')

    # Récupération des paramètres de filtrage
    nom_recherche = request.GET.get('nom', '')
    statut_filtre = request.GET.get('statut', '')
    date_specifique = request.GET.get('date_specifique')
    intervalle_debut = request.GET.get('intervalle_debut')
    intervalle_fin = request.GET.get('intervalle_fin')
    annee_specifique = request.GET.get('annee_specifique')

    # Base queryset
    utilisateurs = Utilisateur.objects.all().order_by('-date_joined')

    # Application des filtres
    if nom_recherche:
        utilisateurs = utilisateurs.filter(nom_complet__icontains=nom_recherche)
    
    if statut_filtre:
        utilisateurs = utilisateurs.filter(statut_validation_compte=statut_filtre)

    # Filtrage par date spécifique (jour)
    if date_specifique:
        try:
            date_obj = datetime.strptime(date_specifique, '%Y-%m-%d').date()
            utilisateurs = utilisateurs.filter(date_joined__date=date_obj)
        except ValueError:
            messages.error(request, "Format de date invalide. Utilisez YYYY-MM-DD.")

    # Filtrage par intervalle de temps
    if intervalle_debut and intervalle_fin:
        try:
            debut_obj = datetime.strptime(intervalle_debut, '%Y-%m-%d').date()
            fin_obj = datetime.strptime(intervalle_fin, '%Y-%m-%d').date()
            utilisateurs = utilisateurs.filter(date_joined__date__range=[debut_obj, fin_obj])
        except ValueError:
            messages.error(request, "Format de date invalide. Utilisez YYYY-MM-DD.")

    # Filtrage par année spécifique
    if annee_specifique:
        try:
            annee = int(annee_specifique)
            utilisateurs = utilisateurs.filter(date_joined__year=annee)
        except ValueError:
            messages.error(request, "Année invalide. Utilisez un nombre (ex: 2023).")

    # Statistiques globales
    total_utilisateurs = utilisateurs.count()
    
    # Statistiques par statut
    compte_valide = utilisateurs.filter(statut_validation_compte='valider').count()
    compte_invalide = utilisateurs.filter(statut_validation_compte='invalider').count()
    compte_en_attente = utilisateurs.filter(statut_validation_compte='attente').count()

    # Calcul des pourcentages
    pourcentage_valide = (compte_valide / total_utilisateurs * 100) if total_utilisateurs else 0
    pourcentage_invalide = (compte_invalide / total_utilisateurs * 100) if total_utilisateurs else 0
    pourcentage_en_attente = (compte_en_attente / total_utilisateurs * 100) if total_utilisateurs else 0

    # Statistiques temporelles
    aujourdhui = timezone.now().date()
    
    # Inscriptions aujourd'hui
    inscrits_aujourdhui = Utilisateur.objects.filter(date_joined__date=aujourdhui).count()
    
    # Inscriptions cette semaine
    debut_semaine = aujourdhui - timedelta(days=aujourdhui.weekday())
    inscrits_semaine = Utilisateur.objects.filter(date_joined__date__gte=debut_semaine).count()
    
    # Inscriptions ce mois
    debut_mois = aujourdhui.replace(day=1)
    inscrits_mois = Utilisateur.objects.filter(date_joined__date__gte=debut_mois).count()
    
    # Inscriptions cette année
    debut_annee = aujourdhui.replace(month=1, day=1)
    inscrits_annee = Utilisateur.objects.filter(date_joined__date__gte=debut_annee).count()

    # Gestion des actions POST (validation/invalidation des comptes)
    if request.method == 'POST':
        utilisateur_id = request.POST.get('utilisateur_id')
        action = request.POST.get('action')

        try:
            utilisateur = Utilisateur.objects.get(id=utilisateur_id)
            
            if action == 'valider':
                utilisateur.statut_validation_compte = 'valider'
                utilisateur.save()
                messages.success(request, f"Compte de {utilisateur.nom_complet} validé avec succès.")
            elif action == 'invalider':
                utilisateur.statut_validation_compte = 'invalider'
                utilisateur.save()
                messages.success(request, f"Compte de {utilisateur.nom_complet} invalidé avec succès.")
            elif action == 'attente':
                utilisateur.statut_validation_compte = 'attente'
                utilisateur.save()
                messages.info(request, f"Statut de {utilisateur.nom_complet} mis à jour à 'en attente'.")
            else:
                messages.error(request, 'Action non reconnue.')

            return redirect('update_status')

        except Utilisateur.DoesNotExist:
            messages.error(request, 'Utilisateur non trouvé.')
            return redirect('update_status')

    # Préparation des données pour le template
    for utilisateur in utilisateurs:
        # Création du lien WhatsApp
        whatsapp_link = f"https://wa.me/{utilisateur.numero}"
        utilisateur.whatsapp_link = whatsapp_link

    context = {
        'utilisateurs': utilisateurs,
        'supportClient': supportClient,
        'nom_recherche': nom_recherche,
        'statut_filtre': statut_filtre,
        'date_specifique': date_specifique,
        'intervalle_debut': intervalle_debut,
        'intervalle_fin': intervalle_fin,
        'annee_specifique': annee_specifique,
        
        # Statistiques
        'total_utilisateurs': total_utilisateurs,
        'compte_valide': compte_valide,
        'compte_invalide': compte_invalide,
        'compte_en_attente': compte_en_attente,
        'pourcentage_valide': round(pourcentage_valide, 2),
        'pourcentage_invalide': round(pourcentage_invalide, 2),
        'pourcentage_en_attente': round(pourcentage_en_attente, 2),
        
        # Statistiques temporelles
        'inscrits_aujourdhui': inscrits_aujourdhui,
        'inscrits_semaine': inscrits_semaine,
        'inscrits_mois': inscrits_mois,
        'inscrits_annee': inscrits_annee,
    }

    return render(request, 'support_client.html', context)







def gestion_produits_utilisateurs(request):
    # Vérification de la connexion et autorisation
    if not request.session.get('connection'):
        messages.error(request, 'Vous devez être connecté pour accéder à cette page.')
        return redirect('login')

    personnel_support_id = request.session.get('user_id')
    if not personnel_support_id:
        messages.error(request, 'Utilisateur non trouvé dans la session.')
        return redirect('login')

    support_client = get_object_or_404(SupportClient, id=personnel_support_id)

    if support_client.validation_compte == 'non accordé':
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette fonctionnalité.")
        return redirect('login')

    # Gestion des actions POST (suppression, modification)
    if request.method == 'POST':
        if 'delete_produit' in request.POST:
            produit_id = request.POST.get('produit_id')
            produit = get_object_or_404(Produit, id=produit_id)
            utilisateur_id = produit.utilisateur.id
            produit.delete()
            messages.success(request, "Le produit a été supprimé avec succès.")
            return redirect(f'{reverse("gestion_produits_utilisateurs")}?utilisateur_id={utilisateur_id}')

        elif 'edit_produit' in request.POST:
            produit_id = request.POST.get('produit_id')
            produit = get_object_or_404(Produit, id=produit_id)
            form = ProduitForm(request.POST, request.FILES, instance=produit)
            
            if form.is_valid():
                form.save()
                messages.success(request, "Le produit a été mis à jour avec succès.")
                return redirect(f'{reverse("gestion_produits_utilisateurs")}?produit_id={produit_id}')
            else:
                # Réafficher le formulaire avec les erreurs
                utilisateur_detail = produit.utilisateur
                produits_utilisateur = utilisateur_detail.produits.all()
                
                # Construire le contexte
                total_utilisateurs = Utilisateur.objects.count()
                total_produits = Produit.objects.count()
                produits_neufs = Produit.objects.filter(etat=Produit.NEUF).count()
                produits_occasion = Produit.objects.filter(etat=Produit.OCCASION).count()
                produits_reconditionnes = Produit.objects.filter(etat=Produit.RECONDITIONNE).count()
                produits_disponibles = Produit.objects.filter(disponible=True).count()
                produits_indisponibles = Produit.objects.filter(disponible=False).count()
                produits_promo = Produit.objects.filter(type_produit=Produit.PROMO).count()
                produits_populaires = Produit.objects.filter(type_produit=Produit.POPULAIRE).count()
                produits_nouveautes = Produit.objects.filter(type_produit=Produit.NOUVEAUTE).count()
                aujourdhui = timezone.now().date()
                produits_ajoutes_aujourdhui = Produit.objects.filter(date_ajout__date=aujourdhui).count()
                debut_semaine = aujourdhui - timedelta(days=aujourdhui.weekday())
                produits_ajoutes_semaine = Produit.objects.filter(date_ajout__date__gte=debut_semaine).count()
                debut_mois = aujourdhui.replace(day=1)
                produits_ajoutes_mois = Produit.objects.filter(date_ajout__date__gte=debut_mois).count()
                # Calcul des pourcentages
                produits_neufs_pourcentage = round((produits_neufs / total_produits * 100), 2) if total_produits > 0 else 0
                produits_occasion_pourcentage = round((produits_occasion / total_produits * 100), 2) if total_produits > 0 else 0

                context = {
                    'support_client': support_client,
                    'mode': 'detail',
                    'total_utilisateurs': total_utilisateurs,
                    'total_produits': total_produits,
                    'produits_neufs': produits_neufs,
                    'produits_occasion': produits_occasion,
                    'produits_reconditionnes': produits_reconditionnes,
                    'produits_disponibles': produits_disponibles,
                    'produits_indisponibles': produits_indisponibles,
                    'produits_neufs_pourcentage': produits_neufs_pourcentage,
                    'produits_occasion_pourcentage': produits_occasion_pourcentage,
                    'produits_promo': produits_promo,
                    'produits_populaires': produits_populaires,
                    'produits_nouveautes': produits_nouveautes,
                    'produits_ajoutes_aujourdhui': produits_ajoutes_aujourdhui,
                    'produits_ajoutes_semaine': produits_ajoutes_semaine,
                    'produits_ajoutes_mois': produits_ajoutes_mois,
                    'etat_choices': Produit.ETAT_CHOICES,
                    'type_produit_choices': Produit.TYPE_PRODUIT_CHOICES,
                    'mise_en_avant_choices': Produit.MISE_EN_AVANT_CHOICES,
                    'utilisateur_detail': utilisateur_detail,
                    'produits_utilisateur': produits_utilisateur,
                    'form': form,
                    'produit_edition': produit
                }
                return render(request, 'gestion_produits_utilisateurs.html', context)

        return redirect('gestion_produits_utilisateurs')

    # Mode affichage (liste ou détail)
    produit_id = request.GET.get('produit_id')
    utilisateur_id = request.GET.get('utilisateur_id')
    
    if produit_id:
        # Affiche les détails d'un produit spécifique pour édition
        produit = get_object_or_404(Produit, id=produit_id)
        form = ProduitForm(instance=produit)
        
        # Construire le contexte
        total_utilisateurs = Utilisateur.objects.count()
        total_produits = Produit.objects.count()
        produits_neufs = Produit.objects.filter(etat=Produit.NEUF).count()
        produits_occasion = Produit.objects.filter(etat=Produit.OCCASION).count()
        produits_reconditionnes = Produit.objects.filter(etat=Produit.RECONDITIONNE).count()
        produits_disponibles = Produit.objects.filter(disponible=True).count()
        produits_indisponibles = Produit.objects.filter(disponible=False).count()
        produits_promo = Produit.objects.filter(type_produit=Produit.PROMO).count()
        produits_populaires = Produit.objects.filter(type_produit=Produit.POPULAIRE).count()
        produits_nouveautes = Produit.objects.filter(type_produit=Produit.NOUVEAUTE).count()
        aujourdhui = timezone.now().date()
        produits_ajoutes_aujourdhui = Produit.objects.filter(date_ajout__date=aujourdhui).count()
        debut_semaine = aujourdhui - timedelta(days=aujourdhui.weekday())
        produits_ajoutes_semaine = Produit.objects.filter(date_ajout__date__gte=debut_semaine).count()
        debut_mois = aujourdhui.replace(day=1)
        produits_ajoutes_mois = Produit.objects.filter(date_ajout__date__gte=debut_mois).count()
        
        produits_neufs_pourcentage = round((produits_neufs / total_produits * 100), 2) if total_produits > 0 else 0
        produits_occasion_pourcentage = round((produits_occasion / total_produits * 100), 2) if total_produits > 0 else 0

        context = {
            'support_client': support_client,
            'mode': 'produit_detail',
            'total_utilisateurs': total_utilisateurs,
            'total_produits': total_produits,
            'produits_neufs': produits_neufs,
            'produits_neufs_pourcentage': produits_neufs_pourcentage,
            'produits_occasion_pourcentage': produits_occasion_pourcentage,
            'produits_occasion': produits_occasion,
            'produits_reconditionnes': produits_reconditionnes,
            'produits_disponibles': produits_disponibles,
            'produits_indisponibles': produits_indisponibles,
            'produits_promo': produits_promo,
            'produits_populaires': produits_populaires,
            'produits_nouveautes': produits_nouveautes,
            'produits_ajoutes_aujourdhui': produits_ajoutes_aujourdhui,
            'produits_ajoutes_semaine': produits_ajoutes_semaine,
            'produits_ajoutes_mois': produits_ajoutes_mois,
            'etat_choices': Produit.ETAT_CHOICES,
            'type_produit_choices': Produit.TYPE_PRODUIT_CHOICES,
            'mise_en_avant_choices': Produit.MISE_EN_AVANT_CHOICES,
            'produit_detail': produit,
            'form': form
        }
        return render(request, 'gestion_produits_utilisateurs.html', context)
    
    elif utilisateur_id:
        # Affiche les produits d'un utilisateur spécifique
        utilisateur_detail = get_object_or_404(Utilisateur, id=utilisateur_id)
        
        # Récupération des paramètres de filtrage
        statut_produit = request.GET.get('statut_produit', '')
        type_produit = request.GET.get('type_produit', '')
        etat_produit = request.GET.get('etat_produit', '')
        min_prix = request.GET.get('min_prix')
        max_prix = request.GET.get('max_prix')
        mise_en_avant = request.GET.get('mise_en_avant')

        produits_utilisateur = utilisateur_detail.produits.all()
        
        # Application des filtres
        if statut_produit:
            if statut_produit == 'disponible':
                produits_utilisateur = produits_utilisateur.filter(disponible=True)
            elif statut_produit == 'indisponible':
                produits_utilisateur = produits_utilisateur.filter(disponible=False)
        
        if type_produit:
            produits_utilisateur = produits_utilisateur.filter(type_produit=type_produit)
        
        if etat_produit:
            produits_utilisateur = produits_utilisateur.filter(etat=etat_produit)
            
        if min_prix:
            try:
                produits_utilisateur = produits_utilisateur.filter(prix__gte=float(min_prix))
            except ValueError:
                pass
                
        if max_prix:
            try:
                produits_utilisateur = produits_utilisateur.filter(prix__lte=float(max_prix))
            except ValueError:
                pass
                
        if mise_en_avant:
            produits_utilisateur = produits_utilisateur.filter(mise_en_avant=mise_en_avant)

        whatsapp_link = f"https://wa.me/{utilisateur_detail.numero}"
        
        # Construire le contexte
        total_utilisateurs = Utilisateur.objects.count()
        total_produits = Produit.objects.count()
        produits_neufs = Produit.objects.filter(etat=Produit.NEUF).count()
        produits_occasion = Produit.objects.filter(etat=Produit.OCCASION).count()
        produits_reconditionnes = Produit.objects.filter(etat=Produit.RECONDITIONNE).count()
        produits_disponibles = Produit.objects.filter(disponible=True).count()
        produits_indisponibles = Produit.objects.filter(disponible=False).count()
        produits_promo = Produit.objects.filter(type_produit=Produit.PROMO).count()
        produits_populaires = Produit.objects.filter(type_produit=Produit.POPULAIRE).count()
        produits_nouveautes = Produit.objects.filter(type_produit=Produit.NOUVEAUTE).count()
        aujourdhui = timezone.now().date()
        produits_ajoutes_aujourdhui = Produit.objects.filter(date_ajout__date=aujourdhui).count()
        debut_semaine = aujourdhui - timedelta(days=aujourdhui.weekday())
        produits_ajoutes_semaine = Produit.objects.filter(date_ajout__date__gte=debut_semaine).count()
        debut_mois = aujourdhui.replace(day=1)
        produits_ajoutes_mois = Produit.objects.filter(date_ajout__date__gte=debut_mois).count()
        produits_neufs_pourcentage = round((produits_neufs / total_produits * 100), 2) if total_produits > 0 else 0
        produits_occasion_pourcentage = round((produits_occasion / total_produits * 100), 2) if total_produits > 0 else 0

        context = {
            'support_client': support_client,
            'mode': 'detail',
            'total_utilisateurs': total_utilisateurs,
            'total_produits': total_produits,
            'produits_neufs': produits_neufs,
            'produits_occasion': produits_occasion,
            'produits_reconditionnes': produits_reconditionnes,
            'produits_disponibles': produits_disponibles,
            'produits_neufs_pourcentage': produits_neufs_pourcentage,
            'produits_occasion_pourcentage': produits_occasion_pourcentage,
            'produits_indisponibles': produits_indisponibles,
            'produits_promo': produits_promo,
            'produits_populaires': produits_populaires,
            'produits_nouveautes': produits_nouveautes,
            'produits_ajoutes_aujourdhui': produits_ajoutes_aujourdhui,
            'produits_ajoutes_semaine': produits_ajoutes_semaine,
            'produits_ajoutes_mois': produits_ajoutes_mois,
            'etat_choices': Produit.ETAT_CHOICES,
            'type_produit_choices': Produit.TYPE_PRODUIT_CHOICES,
            'mise_en_avant_choices': Produit.MISE_EN_AVANT_CHOICES,
            'utilisateur_detail': utilisateur_detail,
            'produits_utilisateur': produits_utilisateur,
            'whatsapp_link': whatsapp_link,
            'statut_produit': statut_produit,
            'type_produit': type_produit,
            'etat_produit': etat_produit,
            'min_prix': min_prix,
            'max_prix': max_prix,
            'mise_en_avant': mise_en_avant
        }
        return render(request, 'gestion_produits_utilisateurs.html', context)
    
    else:
        # Affiche la liste des utilisateurs avec leurs produits
        # Récupération des paramètres de filtrage
        nom_recherche = request.GET.get('nom', '')
        date_specifique = request.GET.get('date_specifique')
        intervalle_debut = request.GET.get('intervalle_debut')
        intervalle_fin = request.GET.get('intervalle_fin')

        # Base queryset avec préchargement des produits
        utilisateurs = Utilisateur.objects.annotate(
            nombre_produits=Count('produits')
        ).order_by('-date_joined')

        # Application des filtres
        if nom_recherche:
            utilisateurs = utilisateurs.filter(
                Q(nom_complet__icontains=nom_recherche) | 
                Q(numero__icontains=nom_recherche)
            )

        if date_specifique:
            try:
                date_obj = datetime.strptime(date_specifique, '%Y-%m-%d').date()
                utilisateurs = utilisateurs.filter(date_joined__date=date_obj)
            except ValueError:
                pass

        if intervalle_debut and intervalle_fin:
            try:
                debut_obj = datetime.strptime(intervalle_debut, '%Y-%m-%d').date()
                fin_obj = datetime.strptime(intervalle_fin, '%Y-%m-%d').date()
                utilisateurs = utilisateurs.filter(date_joined__date__range=[debut_obj, fin_obj])
            except ValueError:
                pass

        # Préparation des données pour le template
        for utilisateur in utilisateurs:
            utilisateur.whatsapp_link = f"https://wa.me/{utilisateur.numero}"

        # Construire le contexte
        total_utilisateurs = Utilisateur.objects.count()
        total_produits = Produit.objects.count()
        produits_neufs = Produit.objects.filter(etat=Produit.NEUF).count()
        produits_occasion = Produit.objects.filter(etat=Produit.OCCASION).count()
        produits_reconditionnes = Produit.objects.filter(etat=Produit.RECONDITIONNE).count()
        produits_disponibles = Produit.objects.filter(disponible=True).count()
        produits_indisponibles = Produit.objects.filter(disponible=False).count()
        produits_promo = Produit.objects.filter(type_produit=Produit.PROMO).count()
        produits_populaires = Produit.objects.filter(type_produit=Produit.POPULAIRE).count()
        produits_nouveautes = Produit.objects.filter(type_produit=Produit.NOUVEAUTE).count()
        aujourdhui = timezone.now().date()
        produits_ajoutes_aujourdhui = Produit.objects.filter(date_ajout__date=aujourdhui).count()
        debut_semaine = aujourdhui - timedelta(days=aujourdhui.weekday())
        produits_ajoutes_semaine = Produit.objects.filter(date_ajout__date__gte=debut_semaine).count()
        debut_mois = aujourdhui.replace(day=1)
        produits_ajoutes_mois = Produit.objects.filter(date_ajout__date__gte=debut_mois).count()
        produits_neufs_pourcentage = round((produits_neufs / total_produits * 100), 2) if total_produits > 0 else 0
        produits_occasion_pourcentage = round((produits_occasion / total_produits * 100), 2) if total_produits > 0 else 0


        context = {
            'support_client': support_client,
            'mode': 'liste',
            'total_utilisateurs': total_utilisateurs,
            'total_produits': total_produits,
            'produits_neufs': produits_neufs,
            'produits_occasion': produits_occasion,
            'produits_reconditionnes': produits_reconditionnes,
            'produits_disponibles': produits_disponibles,
            'produits_indisponibles': produits_indisponibles,
            'produits_promo': produits_promo,
            'produits_populaires': produits_populaires,
            'produits_nouveautes': produits_nouveautes,
            'produits_ajoutes_aujourdhui': produits_ajoutes_aujourdhui,
            'produits_ajoutes_semaine': produits_ajoutes_semaine,
            'produits_ajoutes_mois': produits_ajoutes_mois,
            'produits_neufs_pourcentage': produits_neufs_pourcentage,
            'produits_occasion_pourcentage': produits_occasion_pourcentage,
            'etat_choices': Produit.ETAT_CHOICES,
            'type_produit_choices': Produit.TYPE_PRODUIT_CHOICES,
            'mise_en_avant_choices': Produit.MISE_EN_AVANT_CHOICES,
            'utilisateurs': utilisateurs,
            'nom_recherche': nom_recherche,
            'date_specifique': date_specifique,
            'intervalle_debut': intervalle_debut,
            'intervalle_fin': intervalle_fin
        }
        return render(request, 'gestion_produits_utilisateurs.html', context)
    
    



def gestion_utilisateurs_boutiques(request):
    # Vérification de la connexion et autorisation
    if not request.session.get('connection'):
        messages.error(request, 'Vous devez être connecté pour accéder à cette page.')
        return redirect('login')

    personnel_support_id = request.session.get('user_id')
    if not personnel_support_id:
        messages.error(request, 'Utilisateur non trouvé dans la session.')
        return redirect('login')

    support_client = get_object_or_404(SupportClient, id=personnel_support_id)

    if support_client.validation_compte == 'non accordé':
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette fonctionnalité.")
        return redirect('login')

    # Gestion des actions POST
    if request.method == 'POST':
        utilisateur_id = request.POST.get('utilisateur_id')
        utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
        
        if 'activate_account' in request.POST:
            # Activation du compte utilisateur
            utilisateur.is_active = True
            utilisateur.save()
            messages.success(request, f"Le compte de {utilisateur.nom_complet} a été activé avec succès.")
            
        elif 'deactivate_account' in request.POST:
            # Désactivation du compte utilisateur
            utilisateur.is_active = False
            utilisateur.save()
            messages.success(request, f"Le compte de {utilisateur.nom_complet} a été désactivé avec succès.")
            
        elif 'delete_account' in request.POST:
            # Suppression du compte utilisateur et de sa boutique associée
            nom_utilisateur = utilisateur.nom_complet
            try:
                if utilisateur :
                   utilisateur.delete()
            except Boutique.DoesNotExist:
                pass
            utilisateur.delete()
            messages.success(request, f"Le compte de {nom_utilisateur} et sa boutique ont été supprimés avec succès.")
            
        elif 'toggle_premium' in request.POST:
            # Basculer le mode premium de la boutique avec vérification supplémentaire
            try:
                boutique = Boutique.objects.filter(utilisateur=utilisateur).first()
                # Vérifier que l'utilisateur a le droit d'avoir une boutique premium
                if not utilisateur.is_active:
                    messages.error(request, "Impossible: le compte utilisateur est désactivé")
                else:
                    boutique.premium = not boutique.premium
                    boutique.save()
                    
                    # Mettre à jour la date de publication si passage en premium
                    if boutique.premium:
                        boutique.date_publication = timezone.now()
                        boutique.save()
                    
                    status = "activé" if boutique.premium else "désactivé"
                    messages.success(request, f"Le mode premium pour la boutique '{boutique.titre}' a été {status}.")
            except Boutique.DoesNotExist:
                messages.error(request, "Cet utilisateur n'a pas de boutique associée.")
            
        elif 'toggle_publish' in request.POST:
            # Publier/dépublier la boutique avec vérifications
            try:
                boutique = Boutique.objects.filter(utilisateur=utilisateur).first()
                if not utilisateur.is_active:
                    messages.error(request, "Impossible: le compte utilisateur est désactivé")
                else:
                    boutique.publier = not boutique.publier
                    boutique.save()
                    
                    # Mettre à jour la date de publication si publication
                    if boutique.publier:
                        boutique.date_publication = timezone.now()
                        boutique.save()
                    
                    status = "publiée" if boutique.publier else "dépubliée"
                    messages.success(request, f"La boutique '{boutique.titre}' a été {status}.")
            except Boutique.DoesNotExist:
                messages.error(request, "Cet utilisateur n'a pas de boutique associée.")
            
        return redirect(f'{reverse("gestion_utilisateurs_boutiques")}?utilisateur_id={utilisateur_id}')

    # Mode affichage (liste ou détail)
    utilisateur_id = request.GET.get('utilisateur_id')
    
    if utilisateur_id:
        # Affiche les détails d'un utilisateur spécifique
        utilisateur_detail = get_object_or_404(Utilisateur, id=utilisateur_id)
        whatsapp_link = f"https://wa.me/{utilisateur_detail.numero}"
        
        # Vérification si l'utilisateur a une boutique
        boutique = None
        boutique_exists = False
        try:
            boutique = utilisateur_detail.boutique
            boutique_exists = True
        except Boutique.DoesNotExist:
            pass

        # Construire le contexte
        context = {
            'support_client': support_client,
            'mode': 'detail',
            'utilisateur_detail': utilisateur_detail,
            'whatsapp_link': whatsapp_link,
            'boutique': boutique,
            'boutique_exists': boutique_exists,
            'now': timezone.now(),
        }
        return render(request, 'gestion_utilisateurs_boutiques.html', context)
    
    else:
        # Affiche la liste des utilisateurs avec possibilité de filtrage
        nom_recherche = request.GET.get('nom', '')
        statut_compte = request.GET.get('statut_compte', '')
        statut_boutique = request.GET.get('statut_boutique', '')
        date_specifique = request.GET.get('date_specifique')
        intervalle_debut = request.GET.get('intervalle_debut')
        intervalle_fin = request.GET.get('intervalle_fin')

        # Base queryset avec select_related pour optimiser les requêtes
        utilisateurs = Utilisateur.objects.select_related('boutique').all().order_by('-date_joined')

        # Application des filtres
        if nom_recherche:
            utilisateurs = utilisateurs.filter(
                Q(nom_complet__icontains=nom_recherche) | 
                Q(numero__icontains=nom_recherche) |
                Q(nom_boutique__icontains=nom_recherche))
                
        if statut_compte == 'actif':
            utilisateurs = utilisateurs.filter(is_active=True)
        elif statut_compte == 'inactif':
            utilisateurs = utilisateurs.filter(is_active=False)

        if statut_boutique == 'avec_boutique':
            utilisateurs = utilisateurs.filter(boutique__isnull=False)
        elif statut_boutique == 'sans_boutique':
            utilisateurs = utilisateurs.filter(boutique__isnull=True)
        elif statut_boutique == 'boutique_premium':
            utilisateurs = utilisateurs.filter(boutique__premium=True)
        elif statut_boutique == 'boutique_publiee':
            utilisateurs = utilisateurs.filter(boutique__publier=True)
        elif statut_boutique == 'boutique_non_publiee':
            utilisateurs = utilisateurs.filter(boutique__publier=False)

        if date_specifique:
            try:
                date_obj = datetime.strptime(date_specifique, '%Y-%m-%d').date()
                utilisateurs = utilisateurs.filter(date_joined__date=date_obj)
            except ValueError:
                pass

        if intervalle_debut and intervalle_fin:
            try:
                debut_obj = datetime.strptime(intervalle_debut, '%Y-%m-%d').date()
                fin_obj = datetime.strptime(intervalle_fin, '%Y-%m-%d').date()
                utilisateurs = utilisateurs.filter(date_joined__date__range=[debut_obj, fin_obj])
            except ValueError:
                pass

        # Préparation des données pour le template
        for utilisateur in utilisateurs:
            utilisateur.whatsapp_link = f"https://wa.me/{utilisateur.numero}"
            utilisateur.boutique_exists = hasattr(utilisateur, 'boutique')
            if utilisateur.boutique_exists:
                utilisateur.boutique_premium = utilisateur.boutique.premium
                utilisateur.boutique_publiee = utilisateur.boutique.publier

        # Statistiques pour le tableau de bord
        total_utilisateurs = Utilisateur.objects.count()
        utilisateurs_actifs = Utilisateur.objects.filter(is_active=True).count()
        utilisateurs_inactifs = Utilisateur.objects.filter(is_active=False).count()
        boutiques_total = Boutique.objects.count()
        boutiques_premium = Boutique.objects.filter(premium=True).count()
        boutiques_publiees = Boutique.objects.filter(publier=True).count()
        boutiques_non_publiees = Boutique.objects.filter(publier=False).count()
        # Calcul des pourcentages
        pourcentage_actifs = round((utilisateurs_actifs / total_utilisateurs * 100), 2) if total_utilisateurs > 0 else 0
        pourcentage_inactifs = round((utilisateurs_inactifs / total_utilisateurs * 100), 2) if total_utilisateurs > 0 else 0
        pourcentage_premium = round((boutiques_premium / boutiques_total * 100), 2) if boutiques_total > 0 else 0

        context = {
            'support_client': support_client,
            'mode': 'liste',
            'utilisateurs': utilisateurs,
            'total_utilisateurs': total_utilisateurs,
            'utilisateurs_actifs': utilisateurs_actifs,
            'utilisateurs_inactifs': utilisateurs_inactifs,
            'boutiques_total': boutiques_total,
            'boutiques_premium': boutiques_premium,
            'boutiques_publiees': boutiques_publiees,
            'pourcentage_actifs': pourcentage_actifs,
            'pourcentage_inactifs': pourcentage_inactifs,
            'pourcentage_premium': pourcentage_premium,
            'boutiques_non_publiees': boutiques_non_publiees,
            'nom_recherche': nom_recherche,
            'statut_compte': statut_compte,
            'statut_boutique': statut_boutique,
            'date_specifique': date_specifique,
            'intervalle_debut': intervalle_debut,
            'intervalle_fin': intervalle_fin,
            'now': timezone.now(),
        }
        return render(request, 'gestion_utilisateurs_boutiques.html', context)
    
    





def gestion_abonnements(request):
    # Vérification de la connexion et des permissions
    if request.session.get('connection') != True:
        messages.error(request, 'Vous devez être connecté pour accéder à cette page.')
        return redirect('login')

    personnel_support_id = request.session.get('user_id')
    if not personnel_support_id:
        messages.error(request, 'Utilisateur non trouvé dans la session.')
        return redirect('login')

    support_client = get_object_or_404(SupportClient, id=personnel_support_id)

    # Récupération des paramètres de filtrage
    nom_recherche = request.GET.get('nom', '')
    statut_filtre = request.GET.get('statut', '')
    abonnement_filtre = request.GET.get('abonnement', '')
    show_historique = request.GET.get('historique', False)
    user_historique = request.GET.get('user_id', None)

    # Base queryset
    utilisateurs = Utilisateur.objects.all().order_by('-date_joined')

    # Application des filtres
    if nom_recherche:
        utilisateurs = utilisateurs.filter(nom_complet__icontains=nom_recherche)
    
    if statut_filtre:
        utilisateurs = utilisateurs.filter(statut_validation_compte=statut_filtre)
    
    if abonnement_filtre:
        if abonnement_filtre == 'essai':
            utilisateurs = utilisateurs.filter(abonnements__isnull=True)
        elif abonnement_filtre == 'payant':
            utilisateurs = utilisateurs.filter(abonnements__isnull=False).distinct()

    # Calcul des statistiques financières
    revenus_totaux = Abonnement.objects.aggregate(total=Sum('montant'))['total'] or 0
    revenus_mois = Abonnement.objects.filter(
        date_creation__month=timezone.now().month,
        date_creation__year=timezone.now().year
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    # Nombre d'abonnés actifs (avec abonnement non expiré)
    abonnes_actifs = Utilisateur.objects.filter(
        abonnements__date_fin__gte=timezone.now()
    ).distinct().count()
    
    # Nombre en période d'essai
    en_essai = Utilisateur.objects.filter(
        abonnements__isnull=True,
        date_fin_essai__gte=timezone.now().date()
    ).count()
    
    # Nombre d'essais expirés
    essais_expires = Utilisateur.objects.filter(
        abonnements__isnull=True,
        date_fin_essai__lt=timezone.now().date()
    ).count()

    # Récupération de l'historique si demandé
    historique_paiements = None
    if show_historique and user_historique:
        historique_paiements = HistoriqueAbonnement.objects.filter(
            utilisateur_id=user_historique
        ).order_by('-date_action')

    # Gestion des actions POST
    if request.method == 'POST':
        action = request.POST.get('action')
        utilisateur_id = request.POST.get('utilisateur_id')
        
        try:
            utilisateur = Utilisateur.objects.get(id=utilisateur_id)
            
            if action == 'modifier_essai':
                # Modification de la période d'essai
                jours_ajoutes = int(request.POST.get('jours_ajoutes', 0))
                nouvelle_date = utilisateur.date_fin_essai + timedelta(days=jours_ajoutes)
                utilisateur.date_fin_essai = nouvelle_date
                utilisateur.is_active = True
                
                # Réactiver la boutique si nécessaire
                if hasattr(utilisateur, 'boutique'):
                    utilisateur.boutique.publier_boutique()
                
                utilisateur.save()
                
                # Historique
                HistoriqueAbonnement.objects.create(
                    utilisateur=utilisateur,
                    action=f"Prolongation période d'essai de {jours_ajoutes} jours",
                    effectue_par=support_client,
                    details=f"Nouvelle date de fin d'essai: {nouvelle_date}"
                )
                messages.success(request, f"Période d'essai prolongée jusqu'au {nouvelle_date}")
            
            elif action == 'ajouter_abonnement':
                # Ajout d'un abonnement payant
                type_abonnement = request.POST.get('type_abonnement')
                montant = float(request.POST.get('montant', 0))
                methode_paiement = request.POST.get('methode_paiement')
                reference_paiement = request.POST.get('reference_paiement')
                
                # Calcul de la date de fin en fonction du type d'abonnement
                mois_ajoutes = int(type_abonnement.replace('M', ''))
                date_fin = timezone.now() + timedelta(days=30*mois_ajoutes)
                
                # Création de l'abonnement
                abonnement = Abonnement.objects.create(
                    utilisateur=utilisateur,
                    date_debut=timezone.now(),
                    date_fin=date_fin,
                    montant=montant,
                    methode_paiement=methode_paiement,
                    reference_paiement=reference_paiement,
                    type_abonnement=type_abonnement,
                    cree_par=support_client.nom
                )
                
                # Prolonger la période d'essai de 30 jours en plus de l'abonnement
                utilisateur.date_fin_essai = date_fin + timedelta(days=30*mois_ajoutes)
                utilisateur.is_active = True
                print(f'nouvelle valeur  {utilisateur.date_fin_essai}')
                
                if hasattr(utilisateur, 'boutique'):
                    utilisateur.boutique.publier_boutique()
                utilisateur.save()
                
                # Historique
                HistoriqueAbonnement.objects.create(
                    utilisateur=utilisateur,
                    abonnement=abonnement,
                    action=f"Ajout abonnement {type_abonnement}",
                    effectue_par=support_client,
                    details=f"Montant: {montant}, Méthode: {methode_paiement}, Réf: {reference_paiement}, Date fin: {date_fin.date()}"
                )
                
                messages.success(request, "Abonnement ajouté avec succès.")
            
            elif action == 'activer_compte':
                # Activation manuelle du compte
                utilisateur.is_active = True
                if hasattr(utilisateur, 'boutique'):
                    utilisateur.boutique.publier_boutique()
                utilisateur.save()
                
                HistoriqueAbonnement.objects.create(
                    utilisateur=utilisateur,
                    action="Activation manuelle du compte",
                    effectue_par=support_client,
                    details="Compte activé par le support client"
                )
                messages.success(request, f"Compte de {utilisateur.nom_complet} activé avec succès.")
            
            elif action == 'desactiver_compte':
                # Désactivation manuelle du compte
                utilisateur.is_active = False
                if hasattr(utilisateur, 'boutique'):
                    utilisateur.boutique.depublier_boutique()
                utilisateur.save()
                
                HistoriqueAbonnement.objects.create(
                    utilisateur=utilisateur,
                    action="Désactivation manuelle du compte",
                    effectue_par=support_client,
                    details="Compte désactivé par le support client"
                )
                messages.success(request, f"Compte de {utilisateur.nom_complet} désactivé avec succès.")
            
            return redirect('gestion_abonnements')
        
        except Utilisateur.DoesNotExist:
            messages.error(request, 'Utilisateur non trouvé.')
            return redirect('gestion_abonnements')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
            return redirect('gestion_abonnements')

    # Préparation des données pour le template
    for utilisateur in utilisateurs:
        # Lien WhatsApp de contact
        utilisateur.whatsapp_link = f"https://wa.me/{utilisateur.numero}"
        
        # Statut d'abonnement
        abonnement_actif = utilisateur.abonnements.filter(date_fin__gte=timezone.now()).order_by('-date_fin').first()
        
        if abonnement_actif:
            utilisateur.abonnement_statut = {
                'type': 'payant',
                'date_fin': abonnement_actif.date_fin.date(),
                'type_abonnement': abonnement_actif.get_type_abonnement_display(),
                'abonnement_obj': abonnement_actif
            }
            
            # Préparation du message WhatsApp pour cet abonnement
            message = (
                f"*Reçu de paiement - WarabaGuinnée*\n\n"
                f"*Client:* {utilisateur.nom_complet}\n"
                f"*Boutique:* {getattr(utilisateur, 'nom_boutique', 'N/A')}\n"
                f"*Type d'abonnement:* {abonnement_actif.get_type_abonnement_display()}\n"
                f"*Durée:* {int(abonnement_actif.type_abonnement.replace('M', ''))} mois\n"
                f"*Montant:* {abonnement_actif.montant} FG\n"
                f"*Méthode de paiement:* {abonnement_actif.methode_paiement}\n"
                f"*Référence:* {abonnement_actif.reference_paiement}\n"
                f"*Date de début:* {abonnement_actif.date_debut.date()}\n"
                f"*Date de fin:* {abonnement_actif.date_fin.date()}\n"
                f"*Période d'essai jusqu'au:* {utilisateur.date_fin_essai}\n\n"
                f"Merci pour votre confiance !\n"
                f"L'équipe WarabaGuinnée"
            )
            
            utilisateur.whatsapp_receipt_link = f"https://wa.me/224{utilisateur.numero}?text={quote(message)}"
            
        elif utilisateur.date_fin_essai >= timezone.now().date():
            utilisateur.abonnement_statut = {
                'type': 'essai',
                'date_fin': utilisateur.date_fin_essai
            }
        else:
            utilisateur.abonnement_statut = {
                'type': 'expire',
                'date_fin': None
            }

    context = {
        'utilisateurs': utilisateurs,
        'support_client': support_client,
        'nom_recherche': nom_recherche,
        'statut_filtre': statut_filtre,
        'abonnement_filtre': abonnement_filtre,
        'historique_paiements': historique_paiements,
        'show_historique': show_historique,
        'user_historique': user_historique,
        
        # Statistiques
        'revenus_totaux': revenus_totaux,
        'revenus_mois': revenus_mois,
        'abonnes_actifs': abonnes_actifs,
        'en_essai': en_essai,
        'essais_expires': essais_expires,
        
        # Options pour les formulaires
        'type_abonnement_choices': Abonnement.TYPE_CHOICES,
    }

    return render(request, 'gestion_abonnements.html', context)