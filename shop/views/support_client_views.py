from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from datetime import datetime, timedelta
from shop.models import Utilisateur, SupportClient, Produit,Boutique,Abonnement,HistoriqueAbonnement
from django.db.models import Count, Q, Sum
from shop.forms import ProduitForm  # Supposons que vous avez un formulaire ProduitForm
from django.urls import reverse
from decimal import Decimal
from urllib import parse
import logging





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
    
    




logger = logging.getLogger(__name__)

def gestion_abonnements(request):
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
        
        if 'creer_abonnement' in request.POST:
            try:
                montant = Decimal(request.POST.get('montant', '0'))
                duree_jours = int(request.POST.get('duree_jours', '30'))
                est_premium = 'est_premium' in request.POST
                methode_paiement = request.POST.get('methode_paiement', '')
                reference_paiement = request.POST.get('reference_paiement', '')

                # Log avant création
                logger.info(f"Création d'abonnement pour {utilisateur.nom_complet} - Montant: {montant} - Durée: {duree_jours} jours - Premium: {est_premium}")

                # Désactiver les anciens abonnements
                Abonnement.objects.filter(utilisateur=utilisateur, actif=True).update(actif=False)

                # Créer le nouvel abonnement
                nouvel_abonnement = Abonnement.objects.create(
                    utilisateur=utilisateur,
                    date_fin=timezone.now() + timedelta(days=duree_jours),
                    montant=montant,
                    actif=True,
                    est_premium=est_premium,
                    methode_paiement=methode_paiement,
                    reference_paiement=reference_paiement,
                    cree_par=support_client
                )

                # Gestion de la boutique
                try:
                    boutique = Boutique.objects.get(utilisateur=utilisateur)
                    if est_premium:
                        boutique.publier = True
                        boutique.save()
                        logger.info(f"Boutique de {utilisateur.nom_complet} publiée (Premium)")
                    else:
                        boutique.publier = False
                        boutique.save()
                        logger.info(f"Boutique de {utilisateur.nom_complet} dépubliée (Standard)")
                except Boutique.DoesNotExist:
                    logger.warning(f"Aucune boutique trouvée pour {utilisateur.nom_complet}")

                # Enregistrer dans l'historique
                HistoriqueAbonnement.objects.create(
                    utilisateur=utilisateur,
                    abonnement=nouvel_abonnement,
                    action="Création",
                    effectue_par=support_client,
                    details=f"Création d'abonnement - {duree_jours} jours - {montant}€ - {'Premium' if est_premium else 'Standard'}"
                )

                # Calcul des revenus de la plateforme
                revenus_platforme = Abonnement.objects.filter(
                    actif=True,
                    date_fin__gte=timezone.now()
                ).aggregate(total=Sum('montant'))['total'] or 0

                logger.info(f"Revenus totaux de la plateforme mis à jour : {revenus_platforme}€")

                # Messages WhatsApp possibles
                whatsapp_messages = {
                    'abonnement_actived_premium': (
                        f"Bonjour {utilisateur.nom_complet},\n\n"
                        f"Félicitations ! Votre abonnement PREMIUM a été activé avec succès.\n"
                        f"• Montant: {montant}€\n"
                        f"• Durée: {duree_jours} jours\n"
                        f"• Expiration: {nouvel_abonnement.date_fin.strftime('%d/%m/%Y')}\n"
                        f"• Boutique: PUBLIÉE\n\n"
                        f"Votre boutique est maintenant visible par tous les clients !\n\n"
                        f"Pour toute question, contactez-nous."
                    ),
                    'abonnement_actived_standard': (
                        f"Bonjour {utilisateur.nom_complet},\n\n"
                        f"Votre abonnement STANDARD a été activé.\n"
                        f"• Montant: {montant}€\n"
                        f"• Durée: {duree_jours} jours\n"
                        f"• Expiration: {nouvel_abonnement.date_fin.strftime('%d/%m/%Y')}\n"
                        f"• Boutique: NON PUBLIÉE\n\n"
                        f"Pour publier votre boutique, passez à l'abonnement PREMIUM.\n"
                        f"Contactez-nous pour plus d'informations."
                    ),
                    'general_contact': (
                        f"Bonjour {utilisateur.nom_complet},\n\n"
                        f"Comment pouvons-nous vous aider aujourd'hui ?\n\n"
                        f"L'équipe de support"
                    )
                }

                # Générer les liens WhatsApp
                whatsapp_links = {}
                for key, message in whatsapp_messages.items():
                    message_encoded = parse.quote(message)
                    whatsapp_links[key] = f"https://wa.me/{utilisateur.numero}?text={message_encoded}"
                
                logger.info(f"Messages WhatsApp générés pour {utilisateur.nom_complet}")
                messages.success(request, f"Abonnement créé pour {utilisateur.nom_complet} jusqu'au {nouvel_abonnement.date_fin.date()}")
            
            except Exception as e:
                logger.error(f"Erreur lors de la création d'abonnement pour {utilisateur.nom_complet}: {str(e)}", exc_info=True)
                messages.error(request, f"Erreur: {str(e)}")

        elif 'desactiver_abonnement' in request.POST:
            abonnement_id = request.POST.get('abonnement_id')
            abonnement = get_object_or_404(Abonnement, id=abonnement_id, utilisateur=utilisateur)
            
            # Log avant désactivation
            logger.info(f"Désactivation de l'abonnement {abonnement_id} pour {utilisateur.nom_complet}")
            
            abonnement.actif = False
            abonnement.save()

            # Dépublier la boutique
            try:
                boutique = Boutique.objects.get(utilisateur=utilisateur)
                if boutique.publier:
                    boutique.publier = False
                    boutique.save()
                    logger.info(f"Boutique de {utilisateur.nom_complet} dépubliée après désactivation d'abonnement")
            except Boutique.DoesNotExist:
                logger.warning(f"Aucune boutique trouvée pour {utilisateur.nom_complet} lors de la désactivation")

            # Enregistrer dans l'historique
            HistoriqueAbonnement.objects.create(
                utilisateur=utilisateur,
                abonnement=abonnement,
                action="Désactivation",
                effectue_par=support_client,
                details="Désactivation manuelle de l'abonnement"
            )

            # Messages WhatsApp possibles
            whatsapp_messages = {
                'abonnement_desactive': (
                    f"Bonjour {utilisateur.nom_complet},\n\n"
                    f"Nous vous informons que votre abonnement a été désactivé.\n"
                    f"Date de désactivation: {timezone.now().strftime('%d/%m/%Y')}\n"
                    f"Votre boutique n'est plus visible par les clients.\n\n"
                    f"Pour renouveler ou toute question, contactez-nous.\n\n"
                    f"L'équipe de support"
                ),
                'renouvellement': (
                    f"Bonjour {utilisateur.nom_complet},\n\n"
                    f"Votre abonnement a expiré. Souhaitez-vous le renouveler ?\n\n"
                    f"Options disponibles :\n"
                    f"- Standard (30 jours) : XX€\n"
                    f"- Premium (30 jours) : XX€\n\n"
                    f"Répondez par 'STANDARD' ou 'PREMIUM' pour choisir."
                ),
                'general_contact': (
                    f"Bonjour {utilisateur.nom_complet},\n\n"
                    f"Comment pouvons-nous vous aider aujourd'hui ?\n\n"
                    f"L'équipe de support"
                )
            }

            # Générer les liens WhatsApp
            whatsapp_links = {}
            for key, message in whatsapp_messages.items():
                message_encoded = parse.quote(message)
                whatsapp_links[key] = f"https://wa.me/{utilisateur.numero}?text={message_encoded}"

            logger.info(f"Messages WhatsApp de fin d'abonnement pour {utilisateur.nom_complet}")
            messages.success(request, f"Abonnement désactivé pour {utilisateur.nom_complet}")

        elif 'prolonger_abonnement' in request.POST:
            abonnement_id = request.POST.get('abonnement_id')
            jours_ajout = int(request.POST.get('jours_ajout', '30'))
            abonnement = get_object_or_404(Abonnement, id=abonnement_id, utilisateur=utilisateur)
            
            # Log avant prolongation
            logger.info(f"Prolongation de l'abonnement {abonnement_id} pour {utilisateur.nom_complet} de {jours_ajout} jours")
            
            ancienne_date_fin = abonnement.date_fin
            abonnement.date_fin += timedelta(days=jours_ajout)
            abonnement.save()

            # Enregistrer dans l'historique
            HistoriqueAbonnement.objects.create(
                utilisateur=utilisateur,
                abonnement=abonnement,
                action="Prolongation",
                effectue_par=support_client,
                details=f"Prolongation de {jours_ajout} jours (ancienne date: {ancienne_date_fin})"
            )

            # Messages WhatsApp possibles
            whatsapp_messages = {
                'abonnement_prolonge': (
                    f"Bonjour {utilisateur.nom_complet},\n\n"
                    f"Nous avons prolongé votre abonnement de {jours_ajout} jours.\n"
                    f"• Ancienne date d'expiration: {ancienne_date_fin.strftime('%d/%m/%Y')}\n"
                    f"• Nouvelle date d'expiration: {abonnement.date_fin.strftime('%d/%m/%Y')}\n\n"
                    f"Votre boutique reste {'PUBLIÉE' if abonnement.est_premium else 'NON PUBLIÉE'}.\n\n"
                    f"Pour toute question, contactez-nous.\n\n"
                    f"L'équipe de support"
                ),
                'upgrade_premium': (
                    f"Bonjour {utilisateur.nom_complet},\n\n"
                    f"Profitez de notre offre PREMIUM pour publier votre boutique !\n\n"
                    f"Avantages :\n"
                    f"- Boutique visible par tous les clients\n"
                    f"- Statistiques avancées\n"
                    f"- Support prioritaire\n\n"
                    f"Répondez 'PREMIUM' pour plus d'informations."
                ),
                'general_contact': (
                    f"Bonjour {utilisateur.nom_complet},\n\n"
                    f"Comment pouvons-nous vous aider aujourd'hui ?\n\n"
                    f"L'équipe de support"
                )
            }

            # Générer les liens WhatsApp
            whatsapp_links = {}
            for key, message in whatsapp_messages.items():
                message_encoded = parse.quote(message)
                whatsapp_links[key] = f"https://wa.me/{utilisateur.numero}?text={message_encoded}"

            logger.info(f"Messages WhatsApp de prolongation pour {utilisateur.nom_complet}")
            messages.success(request, f"Abonnement prolongé jusqu'au {abonnement.date_fin.date()}")

        elif 'publier_boutique' in request.POST:
            try:
                boutique = Boutique.objects.get(utilisateur=utilisateur)
                if not boutique.publier:
                    # Vérifier que l'utilisateur a un abonnement premium actif
                    abonnement_actif = Abonnement.abonnement_actuel(utilisateur)
                    if abonnement_actif and abonnement_actif.est_premium:
                        boutique.publier = True
                        boutique.save()
                        
                        # Messages WhatsApp possibles
                        whatsapp_messages = {
                            'boutique_publiee': (
                                f"Bonjour {utilisateur.nom_complet},\n\n"
                                f"Votre boutique a été publiée avec succès !\n"
                                f"Elle est maintenant visible par tous les clients.\n\n"
                                f"Pour accéder à votre boutique : [lien-de-la-boutique]\n\n"
                                f"Pour toute question, contactez-nous."
                            ),
                            'promotion': (
                                f"Bonjour {utilisateur.nom_complet},\n\n"
                                f"Votre boutique est maintenant en ligne !\n\n"
                                f"Profitez de notre offre spéciale pour promouvoir vos produits :\n"
                                f"- Mise en avant pendant 7 jours : XX€\n"
                                f"- Newsletter spéciale : XX€\n\n"
                                f"Répondez 'PROMO' pour en savoir plus."
                            ),
                            'general_contact': (
                                f"Bonjour {utilisateur.nom_complet},\n\n"
                                f"Comment pouvons-nous vous aider aujourd'hui ?\n\n"
                                f"L'équipe de support"
                            )
                        }

                        # Générer les liens WhatsApp
                        whatsapp_links = {}
                        for key, message in whatsapp_messages.items():
                            message_encoded = parse.quote(message)
                            whatsapp_links[key] = f"https://wa.me/{utilisateur.numero}?text={message_encoded}"
                        
                        messages.success(request, f"Boutique de {utilisateur.nom_complet} publiée avec succès")
                    else:
                        messages.error(request, "L'utilisateur doit avoir un abonnement premium actif pour publier sa boutique")
                else:
                    messages.warning(request, "La boutique est déjà publiée")
            except Boutique.DoesNotExist:
                messages.error(request, "Aucune boutique trouvée pour cet utilisateur")

        elif 'depublier_boutique' in request.POST:
            try:
                boutique = Boutique.objects.get(utilisateur=utilisateur)
                if boutique.publier:
                    boutique.publier = False
                    boutique.save()
                    
                    # Messages WhatsApp possibles
                    whatsapp_messages = {
                        'boutique_depubliee': (
                            f"Bonjour {utilisateur.nom_complet},\n\n"
                            f"Votre boutique a été dépubliée.\n"
                            f"Elle n'est plus visible par les clients.\n\n"
                            f"Pour la republier, assurez-vous d'avoir un abonnement premium actif.\n\n"
                            f"Pour toute question, contactez-nous."
                        ),
                        'reactivation': (
                            f"Bonjour {utilisateur.nom_complet},\n\n"
                            f"Votre boutique a été temporairement dépubliée.\n\n"
                            f"Pour la republier immédiatement, répondez 'REACTIVER' ou contactez-nous."
                        ),
                        'general_contact': (
                            f"Bonjour {utilisateur.nom_complet},\n\n"
                            f"Comment pouvons-nous vous aider aujourd'hui ?\n\n"
                            f"L'équipe de support"
                        )
                    }

                    # Générer les liens WhatsApp
                    whatsapp_links = {}
                    for key, message in whatsapp_messages.items():
                        message_encoded = parse.quote(message)
                        whatsapp_links[key] = f"https://wa.me/{utilisateur.numero}?text={message_encoded}"
                    
                    messages.success(request, f"Boutique de {utilisateur.nom_complet} dépubliée avec succès")
                else:
                    messages.warning(request, "La boutique est déjà dépubliée")
            except Boutique.DoesNotExist:
                messages.error(request, "Aucune boutique trouvée pour cet utilisateur")

        elif 'mettre_en_attente' in request.POST:
            utilisateur.is_active = False
            utilisateur.save()

            # Dépublier la boutique
            try:
                boutique = Boutique.objects.get(utilisateur=utilisateur)
                if boutique.publier:
                    boutique.publier = False
                    boutique.save()
                    logger.info(f"Boutique de {utilisateur.nom_complet} dépubliée après mise en attente du compte")
            except Boutique.DoesNotExist:
                logger.warning(f"Aucune boutique trouvée pour {utilisateur.nom_complet} lors de la mise en attente")

            # Messages WhatsApp possibles
            whatsapp_messages = {
                'compte_en_attente': (
                    f"Bonjour {utilisateur.nom_complet},\n\n"
                    f"Votre compte a été mis en attente par notre équipe.\n"
                    f"Votre boutique n'est plus accessible.\n\n"
                    f"Pour plus d'informations, contactez-nous.\n\n"
                    f"L'équipe de support"
                ),
                'reactivation_demande': (
                    f"Bonjour {utilisateur.nom_complet},\n\n"
                    f"Votre compte est actuellement en attente.\n\n"
                    f"Pour demander une réactivation, répondez 'REACTIVATION' avec les informations suivantes :\n"
                    f"- Raison de la suspension\n"
                    f"- Justificatifs si nécessaire\n\n"
                    f"Nous traiterons votre demande rapidement."
                ),
                'general_contact': (
                    f"Bonjour {utilisateur.nom_complet},\n\n"
                    f"Comment pouvons-nous vous aider aujourd'hui ?\n\n"
                    f"L'équipe de support"
                )
            }

            # Générer les liens WhatsApp
            whatsapp_links = {}
            for key, message in whatsapp_messages.items():
                message_encoded = parse.quote(message)
                whatsapp_links[key] = f"https://wa.me/{utilisateur.numero}?text={message_encoded}"

            messages.success(request, f"Compte {utilisateur.nom_complet} mis en attente")

        elif 'reactiver_compte' in request.POST:
            utilisateur.is_active = True
            utilisateur.save()
            
            # Vérifier si l'utilisateur a un abonnement actif pour republier la boutique
            abonnement_actif = Abonnement.abonnement_actuel(utilisateur)
            if abonnement_actif and abonnement_actif.est_premium:
                try:
                    boutique = Boutique.objects.get(utilisateur=utilisateur)
                    if not boutique.publier:
                        boutique.publier = True
                        boutique.save()
                        logger.info(f"Boutique de {utilisateur.nom_complet} republiée après réactivation du compte (abonnement premium actif)")
                except Boutique.DoesNotExist:
                    logger.warning(f"Aucune boutique trouvée pour {utilisateur.nom_complet} lors de la réactivation")

            # Messages WhatsApp possibles
            whatsapp_messages = {
                'compte_reactive': (
                    f"Bonjour {utilisateur.nom_complet},\n\n"
                    f"Votre compte a été réactivé avec succès !\n"
                    f"Votre boutique est maintenant {'PUBLIÉE' if abonnement_actif and abonnement_actif.est_premium else 'NON PUBLIÉE'}.\n\n"
                    f"Pour toute question, contactez-nous.\n\n"
                    f"L'équipe de support"
                ),
                'remerciement': (
                    f"Bonjour {utilisateur.nom_complet},\n\n"
                    f"Nous sommes ravis de vous retrouver !\n\n"
                    f"Votre compte et votre boutique ont été réactivés.\n"
                    f"Profitez de nos services et n'hésitez pas à nous contacter pour toute question.\n\n"
                    f"L'équipe de support"
                ),
                'general_contact': (
                    f"Bonjour {utilisateur.nom_complet},\n\n"
                    f"Comment pouvons-nous vous aider aujourd'hui ?\n\n"
                    f"L'équipe de support"
                )
            }

            # Générer les liens WhatsApp
            whatsapp_links = {}
            for key, message in whatsapp_messages.items():
                message_encoded = parse.quote(message)
                whatsapp_links[key] = f"https://wa.me/{utilisateur.numero}?text={message_encoded}"

            messages.success(request, f"Compte {utilisateur.nom_complet} réactivé")

        return redirect(f'{reverse("gestion_abonnements")}?utilisateur_id={utilisateur_id}')

    # Mode affichage
    utilisateur_id = request.GET.get('utilisateur_id')
    
    if utilisateur_id:
        # Mode détail
        utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
        abonnements = Abonnement.objects.filter(utilisateur=utilisateur).order_by('-date_debut')
        historique = HistoriqueAbonnement.objects.filter(utilisateur=utilisateur).order_by('-date_action')
        
        # Statuts d'abonnement
        en_essai = Abonnement.est_dans_essai_gratuit(utilisateur)
        doit_payer = Abonnement.doit_payer(utilisateur)
        abonnement_actuel = Abonnement.abonnement_actuel(utilisateur)
        
        # Vérifier si le paiement a expiré
        paiement_expire = False
        if abonnement_actuel and abonnement_actuel.date_fin < timezone.now():
            paiement_expire = True
            logger.warning(f"Abonnement expiré détecté pour {utilisateur.nom_complet} (ID: {abonnement_actuel.id})")

        # Vérifier la boutique
        boutique = None
        boutique_exists = False
        try:
            boutique = Boutique.objects.get(utilisateur=utilisateur)
            boutique_exists = True
        except Boutique.DoesNotExist:
            pass

        # Calcul des revenus de la plateforme
        revenus_platforme = Abonnement.objects.filter(
            actif=True,
            date_fin__gte=timezone.now()
        ).aggregate(total=Sum('montant'))['total'] or 0

        # Messages WhatsApp possibles selon le statut
        whatsapp_messages = {
            'contact_general': (
                f"Bonjour {utilisateur.nom_complet},\n\n"
                f"Comment pouvons-nous vous aider aujourd'hui ?\n\n"
                f"L'équipe de support"
            ),
            'statut_abonnement': (
                f"Bonjour {utilisateur.nom_complet},\n\n"
                f"Statut de votre abonnement :\n"
                f"• Type: {'PREMIUM' if abonnement_actuel and abonnement_actuel.est_premium else 'STANDARD' if abonnement_actuel else 'AUCUN'}\n"
                f"• Statut: {'ACTIF' if abonnement_actuel and abonnement_actuel.actif else 'INACTIF'}\n"
                f"• Expiration: {abonnement_actuel.date_fin.strftime('%d/%m/%Y') if abonnement_actuel else 'N/A'}\n\n"
                f"Pour toute question, contactez-nous."
            ),
            'renouvellement': (
                f"Bonjour {utilisateur.nom_complet},\n\n"
                f"Votre abonnement {'expire bientôt' if abonnement_actuel else 'est inactif'}.\n\n"
                f"Souhaitez-vous le renouveler ?\n"
                f"Options disponibles :\n"
                f"- Standard (30 jours) : XX€\n"
                f"- Premium (30 jours) : XX€\n\n"
                f"Répondez par 'STANDARD' ou 'PREMIUM' pour choisir."
            )
        }

        # Ajouter des messages spécifiques selon le statut
        if en_essai:
            whatsapp_messages['fin_essai'] = (
                f"Bonjour {utilisateur.nom_complet},\n\n"
                f"Votre période d'essai gratuit se termine bientôt.\n"
                f"Jours restants : {(utilisateur.date_joined.date() + timedelta(days=90) - timezone.now().date()).days}\n\n"
                f"Pour continuer à utiliser nos services, choisissez un abonnement :\n"
                f"- Standard (30 jours) : XX€\n"
                f"- Premium (30 jours) : XX€\n\n"
                f"Répondez par 'STANDARD' ou 'PREMIUM' pour choisir."
            )
        
        if paiement_expire:
            whatsapp_messages['expiration'] = (
                f"Bonjour {utilisateur.nom_complet},\n\n"
                f"Votre abonnement a expiré le {abonnement_actuel.date_fin.strftime('%d/%m/%Y')}.\n"
                f"Votre boutique n'est plus visible par les clients.\n\n"
                f"Pour renouveler immédiatement, répondez 'RENOUVELER'."
            )

        # Générer les liens WhatsApp
        whatsapp_links = {}
        for key, message in whatsapp_messages.items():
            message_encoded = parse.quote(message)
            whatsapp_links[key] = f"https://wa.me/{utilisateur.numero}?text={message_encoded}"

        context = {
            'support_client': support_client,
            'mode': 'detail',
            'utilisateur': utilisateur,
            'abonnements': abonnements,
            'historique_abonnements': historique,
            'abonnement_actuel': abonnement_actuel,
            'en_essai': en_essai,
            'doit_payer': doit_payer,
            'paiement_expire': paiement_expire,
            'boutique_exists': boutique_exists,
            'boutique': boutique,
            'now': timezone.now(),
            'jours_restants_essai': (utilisateur.date_joined.date() + timedelta(days=90) - timezone.now().date()).days if en_essai else 0,
            'revenus_platforme': revenus_platforme,
            'whatsapp_links': whatsapp_links,  # Tous les liens WhatsApp disponibles
        }
        return render(request, 'gestion_abonnements.html', context)
    
    else:
        # Mode liste avec filtres
        nom_recherche = request.GET.get('nom', '')
        statut_abonnement = request.GET.get('statut_abonnement', '')
        statut_compte = request.GET.get('statut_compte', '')
        
        utilisateurs = Utilisateur.objects.all().order_by('-date_joined')
        
        if nom_recherche:
            utilisateurs = utilisateurs.filter(
                Q(nom_complet__icontains=nom_recherche) | 
                Q(numero__icontains=nom_recherche))
            
        if statut_compte == 'actif':
            utilisateurs = utilisateurs.filter(is_active=True)
        elif statut_compte == 'inactif':
            utilisateurs = utilisateurs.filter(is_active=False)

        # Préparer les données avec les statuts d'abonnement
        utilisateurs_avec_statut = []
        aujourd_hui = timezone.now().date()
        
        for utilisateur in utilisateurs:
            en_essai = Abonnement.est_dans_essai_gratuit(utilisateur)
            doit_payer = Abonnement.doit_payer(utilisateur)
            abonnement_actuel = Abonnement.abonnement_actuel(utilisateur)
            
            # Déterminer le statut pour le filtre
            statut = 'essai' if en_essai else 'actif' if abonnement_actuel else 'inactif'
            
            if statut_abonnement and statut != statut_abonnement:
                continue
            
            # Calcul des jours restants d'essai
            jours_restants_essai = (utilisateur.date_joined.date() + timedelta(days=90) - aujourd_hui).days if en_essai else 0
            
            # Vérifier si l'abonnement a expiré
            paiement_expire = False
            if abonnement_actuel and abonnement_actuel.date_fin.date() < aujourd_hui:
                paiement_expire = True
                logger.info(f"Utilisateur {utilisateur.nom_complet} avec abonnement expiré détecté en liste")
            
            # Messages WhatsApp de base pour la liste
            whatsapp_messages = {
                'contact_general': (
                    f"Bonjour {utilisateur.nom_complet},\n\n"
                    f"Comment pouvons-nous vous aider aujourd'hui ?\n\n"
                    f"L'équipe de support"
                ),
                'statut_compte': (
                    f"Bonjour {utilisateur.nom_complet},\n\n"
                    f"Statut de votre compte :\n"
                    f"• Abonnement: {'PREMIUM' if abonnement_actuel and abonnement_actuel.est_premium else 'STANDARD' if abonnement_actuel else 'ESSAI'}\n"
                    f"• Statut: {'ACTIF' if utilisateur.is_active else 'INACTIF'}\n"
                    f"• Boutique: {'PUBLIÉE' if Boutique.objects.filter(utilisateur=utilisateur, publier=True).exists() else 'NON PUBLIÉE'}\n\n"
                    f"Pour toute question, contactez-nous."
                )
            }

            # Générer les liens WhatsApp
            whatsapp_links = {}
            for key, message in whatsapp_messages.items():
                message_encoded = parse.quote(message)
                whatsapp_links[key] = f"https://wa.me/{utilisateur.numero}?text={message_encoded}"
                
            utilisateurs_avec_statut.append({
                'utilisateur': utilisateur,
                'en_essai': en_essai,
                'doit_payer': doit_payer,
                'abonnement_actuel': abonnement_actuel,
                'statut': statut,
                'jours_restants_essai': jours_restants_essai,
                'paiement_expire': paiement_expire,
                'boutique': Boutique.objects.filter(utilisateur=utilisateur).first(),
                'whatsapp_links': whatsapp_links,  # Tous les liens WhatsApp disponibles
            })

        # Calculer les statistiques
        stats = {
            'total': Utilisateur.objects.count(),
            'actifs': Utilisateur.objects.filter(is_active=True).count(),
            'inactifs': Utilisateur.objects.filter(is_active=False).count(),
            'en_essai': sum(1 for u in utilisateurs_avec_statut if u['en_essai']),
            'abonnes': sum(1 for u in utilisateurs_avec_statut if u['abonnement_actuel']),
            'en_retard': sum(1 for u in utilisateurs_avec_statut if u['doit_payer'] and not u['en_essai']),
            'expires': sum(1 for u in utilisateurs_avec_statut if u['paiement_expire']),
            'revenus_platforme': Abonnement.objects.filter(
                actif=True,
                date_fin__gte=timezone.now()
            ).aggregate(total=Sum('montant'))['total'] or 0,
        }

        context = {
            'support_client': support_client,
            'mode': 'liste',
            'utilisateurs': utilisateurs_avec_statut,
            'stats': stats,
            'nom_recherche': nom_recherche,
            'statut_abonnement': statut_abonnement,
            'statut_compte': statut_compte,
            'now': timezone.now(),
        }
        return render(request, 'gestion_abonnements.html', context)