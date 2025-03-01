from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from shop.models import Utilisateur, SupportClient

def update_utilisateur_status(request):
    # Vérifier si l'utilisateur est connecté
    if request.session.get('connection') != True:
        messages.error(request, 'Vous devez être connecté pour ajouter ou supprimer vos images de slider.')
        return redirect('login')  # Rediriger vers la page de connexion  

    # Récupérer l'ID du personnel support depuis la session
    personnel_support_id = request.session.get('user_id')

    # Vérifier si l'ID du personnel support est présent dans la session
    if not personnel_support_id:
        messages.error(request, 'Utilisateur non trouvé dans la session.')
        return redirect('login')  # Rediriger si aucun ID trouvé

    # Récupérer le SupportClient correspondant à l'ID du personnel support
    supportClient = get_object_or_404(SupportClient, id=personnel_support_id)

    # Vérification si le SupportClient est autorisé à valider ou invalider les comptes
    if supportClient.validation_compte == 'non accordé':
        messages.error(request, "Vous n'êtes pas autorisé à valider ou invalider les comptes clients.")
        return redirect('login')  # Rediriger vers la page d'accueil ou une autre page appropriée
    # Si l'utilisateur a les droits, continuer le traitement des utilisateurs
    utilisateurs = Utilisateur.objects.all()

    # Filtrer les utilisateurs selon le nom ou le statut de validation, si spécifié dans la requête
    nom_recherche = request.GET.get('nom', '')
    statut_filtre = request.GET.get('statut', '')

    if nom_recherche:
        utilisateurs = utilisateurs.filter(nom_complet__icontains=nom_recherche)

    if statut_filtre:
        utilisateurs = utilisateurs.filter(statut_validation_compte=statut_filtre)

    # Vérifier s'il y a des utilisateurs après les filtres
    if not utilisateurs:
        messages.info(request, 'Aucun utilisateur ne correspond à votre recherche ou filtre.')

    # Compter les utilisateurs par statut de validation
    compte_valide = utilisateurs.filter(statut_validation_compte='valider').count()
    compte_invalide = utilisateurs.filter(statut_validation_compte='invalider').count()
    compte_en_attente = utilisateurs.filter(statut_validation_compte='attente').count()

    # Calcul des pourcentages
    total_utilisateurs = utilisateurs.count()
    pourcentage_valide = (compte_valide / total_utilisateurs * 100) if total_utilisateurs else 0
    pourcentage_invalide = (compte_invalide / total_utilisateurs * 100) if total_utilisateurs else 0
    pourcentage_en_attente = (compte_en_attente / total_utilisateurs * 100) if total_utilisateurs else 0

    # Si l'utilisateur a cliqué sur un bouton pour modifier le statut
    if request.method == 'POST':
        utilisateur_id = request.POST.get('utilisateur_id')  # ID de l'utilisateur
        action = request.POST.get('action')  # Action à effectuer : valider, invalider, mettre en attente ou supprimer

        # Vérifier si l'utilisateur existe
        try:
            utilisateur = Utilisateur.objects.get(id=utilisateur_id)
        except Utilisateur.DoesNotExist:
            messages.error(request, 'Utilisateur non trouvé.')
            return redirect('update_status')  # Rediriger vers la page de mise à jour si l'utilisateur n'existe pas

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

        return redirect('update_status')  # Rediriger vers la page de mise à jour après l'action

    # Retourner les informations de SupportClient, les comptes par statut, et les pourcentages dans le contexte
    return render(request, 'support_client.html', {
        'utilisateurs': utilisateurs,
        'supportClient': supportClient,  # Ajouter l'objet supportClient pour l'afficher si nécessaire
        'nom_recherche': nom_recherche,  # Passer le terme de recherche pour la barre de recherche
        'statut_filtre': statut_filtre,   # Passer le statut de filtre pour les options de filtrage
        'compte_valide': compte_valide,  # Nombre de comptes validés
        'compte_invalide': compte_invalide,  # Nombre de comptes invalidés
        'compte_en_attente': compte_en_attente,  # Nombre de comptes en attente
        'pourcentage_valide': pourcentage_valide,  # Pourcentage de comptes validés
        'pourcentage_invalide': pourcentage_invalide,  # Pourcentage de comptes invalidés
        'pourcentage_en_attente': pourcentage_en_attente,  # Pourcentage de comptes en attente
    })
