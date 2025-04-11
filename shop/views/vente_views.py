from django.shortcuts import render, redirect
from django.contrib import messages
from shop.models import Vente, Utilisateur, Produit, Tag , VenteAttente
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from decimal import Decimal, InvalidOperation
from collections import defaultdict
import calendar
from django.db.models import F, Sum, Avg,  Q , Max
from django.db.models import ExpressionWrapper, FloatField
from django.core.paginator import Paginator
import logging
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.db.models import Q
from django.db.models import F, Sum, Avg,  Q , Max
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pandas as pd




# Configuration du logger
logger = logging.getLogger(__name__)

def calculate_business_metrics(ventes_terminees):
    """Calcule les métriques principales du business"""
    metrics = {
        'total_revenu': 0,
        'total_cout': 0,
        'total_profit': 0,
        'total_profil': 0,
        'pourcentage_profit': 0,
        'total_ventes': 0,
        'avg_profit_margin': 0,
        'avg_sale_value': 0
    }
    
    if not ventes_terminees.exists():
        return metrics
    
    # Calcul des totaux de base
    metrics['total_revenu'] = sum(vente.prix_vente * vente.quantite_vendue for vente in ventes_terminees)
    metrics['total_cout'] = sum(vente.prix_achat * vente.quantite_vendue for vente in ventes_terminees)
    metrics['total_profit'] = metrics['total_revenu'] - metrics['total_cout']
    metrics['total_profil'] = metrics['total_profit']  # Peut être ajusté avec d'autres coûts
    metrics['total_ventes'] = sum(vente.quantite_vendue for vente in ventes_terminees)
    
    # Calcul des pourcentages et moyennes
    if metrics['total_revenu'] > 0:
        metrics['pourcentage_profit'] = round((metrics['total_profit'] / metrics['total_revenu']) * 100, 2)
        metrics['avg_profit_margin'] = metrics['total_profit'] / metrics['total_ventes'] if metrics['total_ventes'] > 0 else 0
        metrics['avg_sale_value'] = metrics['total_revenu'] / metrics['total_ventes'] if metrics['total_ventes'] > 0 else 0
    
    return metrics

def analyze_sales_trends(ventes_terminees, annee_analyse=None):
    """Analyse les tendances de ventes"""
    trends = {
        'ventes_par_mois': [],
        'profits_par_mois': [],
        'ventes_par_jour': [],
        'tendance_annuelle': None,
        'meilleurs_mois': [],
        'pires_mois': []
    }
    
    if not ventes_terminees.exists():
        return trends
    
    # Analyse par mois
    if annee_analyse:
        try:
            ventes_annee = ventes_terminees.filter(date_vente__year=annee_analyse)
            
            # Préparation des données mensuelles
            ventes_par_mois = defaultdict(float)
            profits_par_mois = defaultdict(float)
            
            for vente in ventes_annee:
                mois = vente.date_vente.month
                # Initialisation de la clé dans les dictionnaires avec Decimal si elle n'existe pas déjà
                if mois not in ventes_par_mois:
                    ventes_par_mois[mois] = Decimal(0)
                if mois not in profits_par_mois:
                    profits_par_mois[mois] = Decimal(0)

                # Vérification si les prix sont valides
                if vente.prix_vente is not None and vente.prix_achat is not None:
                    # Conversion explicite des prix en Decimal
                    prix_vente = Decimal(str(vente.prix_vente))
                    prix_achat = Decimal(str(vente.prix_achat))
                    
                    # Additionner la quantité vendue au mois
                    ventes_par_mois[mois] += Decimal(vente.quantite_vendue)
                    
                    # Calculer les profits pour le mois en utilisant Decimal pour les prix
                    profits_par_mois[mois] += (prix_vente - prix_achat) * Decimal(vente.quantite_vendue)
            # Formatage pour le template
            trends['ventes_par_mois'] = [
                {'mois': calendar.month_name[i], 'total': ventes_par_mois.get(i, 0)}
                for i in range(1, 13)
            ]
            
            trends['profits_par_mois'] = [
                {'mois': calendar.month_name[i], 'total': profits_par_mois.get(i, 0)}
                for i in range(1, 13)
            ]
            
            # Identification des meilleurs et pires mois
            if profits_par_mois:
                sorted_months = sorted(profits_par_mois.items(), key=lambda x: x[1], reverse=True)
                trends['meilleurs_mois'] = [
                    {'mois': calendar.month_name[m], 'profit': p}
                    for m, p in sorted_months[:3]
                ]
                trends['pires_mois'] = [
                    {'mois': calendar.month_name[m], 'profit': p}
                    for m, p in sorted_months[-3:] if p < 0  # Assurez-vous de prendre les mois avec des profits négatifs
                ]
                
                # Calcul de la tendance annuelle
                total_annee = sum(profits_par_mois.values())
                moyenne_mensuelle = total_annee / 12 if total_annee > 0 else 0
                trends['tendance_annuelle'] = {
                    'direction': 'positive' if moyenne_mensuelle > 0 else 'negative',
                    'valeur': abs(moyenne_mensuelle)
                }
                
        except ValueError as e:
            logger.error(f"Erreur d'analyse de l'année: {str(e)}")
    
    # Analyse des ventes par jour de la semaine
    jours_semaine = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    ventes_par_jour = defaultdict(float)
    
    for vente in ventes_terminees:
        if vente.date_vente:
            jour = vente.date_vente.weekday()  # 0=lundi, 6=dimanche
            ventes_par_jour[jour] += vente.quantite_vendue
    
    trends['ventes_par_jour'] = [
        {'jour': jours_semaine[i], 'total': ventes_par_jour.get(i, 0)}
        for i in range(7)
    ]
    
    return trends

def analyze_products_performance(ventes_terminees, produits):
    """Analyse la performance des produits"""
    performance = {
        'top_produits': [],
        'produits_sous_performance': [],
        'meilleures_categories': [],
        'top_marques': [],
        'produits_plus_rentables': []
    }
    
    if not ventes_terminees.exists():
        return performance
    
    # Analyse des produits
    all_ventes = ventes_terminees.annotate(
        profit_unitaire=ExpressionWrapper(
            F('prix_vente') - F('prix_achat'),
            output_field=FloatField()
        ),
        profit_total=ExpressionWrapper(
            (F('prix_vente') - F('prix_achat')) * F('quantite_vendue'),
            output_field=FloatField()
        )
    ).values('nom_produit', 'produit__marque', 'produit__tags__nom').annotate(
        total_vendu=Sum('quantite_vendue'),
        total_revenu=Sum(F('prix_vente') * F('quantite_vendue')),
        total_profit=Sum('profit_total'),
        profit_margin=Avg('profit_unitaire')
    ).order_by('-total_vendu')
    
    if all_ventes.exists():
        # Top produits par quantité vendue
        performance['top_produits'] = list(all_ventes[:5])
        
        # Produits sous-performance (profit < 0)
        performance['produits_sous_performance'] = [
            p for p in all_ventes if p['total_profit'] < 0
        ][:5]
        
        # Produits les plus rentables (meilleure marge)
        performance['produits_plus_rentables'] = list(
            sorted(all_ventes, key=lambda x: x['profit_margin'], reverse=True)[:5]
        )
        
        # Meilleures marques
        marques_data = defaultdict(float)
        for vente in all_ventes:
            if vente['produit__marque']:
                marques_data[vente['produit__marque']] += vente['total_profit']
        
        performance['top_marques'] = sorted(
            [{'marque': k, 'profit': v} for k, v in marques_data.items()],
            key=lambda x: x['profit'],
            reverse=True
        )[:5]
        
        # Meilleures catégories (tags)
        tags_data = defaultdict(float)
        for vente in all_ventes:
            if vente['produit__tags__nom']:
                tags_data[vente['produit__tags__nom']] += vente['total_profit']
        
        performance['meilleures_categories'] = sorted(
            [{'tag': k, 'profit': v} for k, v in tags_data.items()],
            key=lambda x: x['profit'],
            reverse=True
        )[:5]
        
        # Enrichissement des produits avec les données des produits (y compris les images)
        for category in ['top_produits', 'produits_sous_performance', 'produits_plus_rentables']:
            for product in performance[category]:
                produit_obj = produits.filter(nom=product['nom_produit']).first()
                if produit_obj:
                    product['stock'] = produit_obj.quantite_stock
                    product['image'] = produit_obj.image.url if produit_obj.image else None
                    product['id'] = produit_obj.id
                    product['description'] = produit_obj.description  # Ajouter la description si disponible
                    
    return performance


def analyze_inventory(produits, ventes_terminees):
    """Analyse l'inventaire et fait des prédictions, incluant des alertes pour stock faible"""
    inventory = {
        'prediction_stock': [],
        'stock_bas': [],
        'surstock': [],
        'rotation_stock': [],
        'alertes_stock': []  # Liste des produits avec stock faible ou nul
    }
    
    if not produits.exists():
        return inventory
    
    for produit in produits:
        # Analyse des ventes du produit
        ventes_produit = ventes_terminees.filter(
            Q(nom_produit=produit.nom) | Q(produit=produit))
        
        stats = ventes_produit.aggregate(
            total_vendu=Sum('quantite_vendue'),
            moyenne_mensuelle=Avg('quantite_vendue'),
            derniere_vente=Max('date_vente')
        )
        
        item = {
            'produit': produit.nom,
            'id': produit.id,
            'stock_actuel': produit.quantite_stock,
            'jours_sans_vente': (timezone.now() - stats['derniere_vente']).days if stats['derniere_vente'] else None,
            'niveau': 'inconnu',
            'image': produit.image.url if produit.image else None  # Ajout de l'image du produit
        }
        
        # Vérification des stocks faibles ou nuls
        if produit.quantite_stock == 0:
            inventory['alertes_stock'].append({
                'produit': produit.nom,
                'id': produit.id,
                'stock': produit.quantite_stock,
                'niveau': 'rupture',  # Stock épuisé
                'image': produit.image.url if produit.image else None  # Ajout de l'image du produit
            })
        elif produit.quantite_stock <= 5:
            inventory['alertes_stock'].append({
                'produit': produit.nom,
                'id': produit.id,
                'stock': produit.quantite_stock,
                'niveau': 'faible',  # Stock faible
                'image': produit.image.url if produit.image else None  # Ajout de l'image du produit
            })
        
        if stats['moyenne_mensuelle'] and stats['moyenne_mensuelle'] > 0:
            mois_restants = produit.quantite_stock / stats['moyenne_mensuelle']
            item['mois_restants'] = round(mois_restants, 1)
            
            # Détermination du niveau de stock
            if mois_restants < 1:
                item['niveau'] = 'danger'
                inventory['stock_bas'].append(item)
            elif mois_restants < 3:
                item['niveau'] = 'warning'
            else:
                item['niveau'] = 'safe'
                
                # Identification des surstocks
                if mois_restants > 6:
                    inventory['surstock'].append(item)
            
            inventory['prediction_stock'].append(item)
        
        # Calcul de la rotation des stocks (si le produit existe depuis assez longtemps)
        if produit.date_ajout:
            mois_existence = (timezone.now() - produit.date_ajout).days / 30
            if mois_existence >= 1 and stats['moyenne_mensuelle']:
                ventes_mensuelles = stats['moyenne_mensuelle']
                if ventes_mensuelles > 0:
                    # Rotation des stocks basée sur les ventes mensuelles moyennes
                    rotation = ventes_mensuelles / produit.quantite_stock
                    inventory['rotation_stock'].append({
                        'produit': produit.nom,
                        'id': produit.id,
                        'rotation': round(rotation, 2),
                        'niveau': 'bon' if rotation >= 0.5 else 'moyen' if rotation >= 0.2 else 'faible'
                    })
    
    # Tri des listes
    inventory['stock_bas'].sort(key=lambda x: x.get('mois_restants', 999))
    inventory['surstock'].sort(key=lambda x: -x.get('mois_restants', 0))
    inventory['rotation_stock'].sort(key=lambda x: -x['rotation'])

    # Intégration des alertes de stock faible ou nul dans l'inventaire
    inventory['alertes_stock'].sort(key=lambda x: x['niveau'] == 'rupture', reverse=True)  # Les ruptures d'abord

    return inventory


def predict_future_sales(ventes_terminees, produits, months_to_predict=3):
    """Prédit les ventes futures en utilisant un modèle ML"""
    if not ventes_terminees.exists():
        return {}
    
    # Préparation des données
    sales_data = []
    for vente in ventes_terminees:
        sales_data.append({
            'date': vente.date_vente,
            'product_id': vente.produit.id if vente.produit else 0,
            'quantity': vente.quantite_vendue,
            'price': float(vente.prix_vente) if hasattr(vente, 'prix_vente') else 0.0,
            'month': vente.date_vente.month,
            'day_of_week': vente.date_vente.weekday(),
            'is_weekend': 1 if vente.date_vente.weekday() >= 5 else 0
        })
    
    df = pd.DataFrame(sales_data)
    
    # Feature engineering
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['rolling_avg'] = df.groupby('product_id')['quantity'].transform(
        lambda x: x.rolling(window=30, min_periods=1).mean()
    )
    
    # Préparation pour l'entraînement
    X = df[['product_id', 'month', 'day_of_week', 'is_weekend', 'rolling_avg', 'price']]
    y = df['quantity']
    
    # Entraînement du modèle
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    if len(X) > 1:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
    else:
        # Pas assez de données pour un split
        X_train, X_test, y_train, y_test = X, X, y, y

    model.fit(X_train, y_train)
    
    # Prédiction pour les mois futurs
    future_dates = pd.date_range(start=timezone.now().date(), periods=months_to_predict, freq='M')
    predictions = {}
    
    for product in produits:
        product_data = []
        for date in future_dates:
            # Vérification des attributs du produit
            product_price = 0.0
            if hasattr(product, 'prix_vente'):
                product_price = float(product.prix_vente) if product.prix_vente else 0.0
            elif hasattr(product, 'prix'):
                product_price = float(product.prix) if product.prix else 0.0
            
            product_data.append({
                'product_id': product.id,
                'month': date.month,
                'day_of_week': date.weekday(),
                'is_weekend': 1 if date.weekday() >= 5 else 0,
                'rolling_avg': df[df['product_id'] == product.id]['quantity'].mean() if not df[df['product_id'] == product.id].empty else 0,
                'price': product_price
            })
        
        if product_data:
            product_df = pd.DataFrame(product_data)
            try:
                pred = model.predict(product_df[X.columns])
                
                # Récupération de l'URL de l'image du produit
                product_image_url = None
                if hasattr(product, 'image') and product.image:
                    product_image_url = product.image.url
                elif hasattr(product, 'image_produit') and product.image_produit:
                    product_image_url = product.image_produit.url
                
                predictions[product.id] = {
                    'product_name': product.nom,
                    'current_stock': product.quantite_stock,
                    'product_image': product_image_url,  # Ajout de l'URL de l'image
                    'predictions': [
                        {
                            'month': future_dates[i].strftime('%Y-%m'), 
                            'predicted_sales': round(pred[i], 2),
                            'confidence': min(100, max(0, round(pred[i]/max(1, df[df['product_id'] == product.id]['quantity'].mean()) * 100, 2)))
                        }
                        for i in range(len(pred))
                    ],
                    'total_predicted': round(sum(pred), 2),
                    'stock_risk': product.quantite_stock < sum(pred)
                }
            except Exception as e:
                logger.error(f"Erreur de prédiction pour le produit {product.id}: {str(e)}")
                continue
    
    return predictions

    
def vente_list(request):
    # Vérification de la connexion
    if not request.session.get('connection'):
        messages.error(request, 'Vous devez être connecté pour accéder à vos ventes.')
        return redirect('login')

    try:
        utilisateur = Utilisateur.objects.get(id=request.session.get('user_id'))
    except Utilisateur.DoesNotExist:
        messages.error(request, 'Utilisateur non trouvé.')
        return redirect('login')

    # Récupération des ventes avec select_related pour optimisation
    ventes_en_cours = VenteAttente.objects.filter(
        utilisateur=utilisateur,
     )

    ventes_terminees = Vente.objects.filter(
        utilisateur=utilisateur, 
        statut=True
    ).select_related('produit')

   # Gestion des filtres avec validation robuste
    filtres = {
        'jour_unique': request.GET.get('jour_unique', ''),
        'intervalle_jours_debut': request.GET.get('debut_jour', ''),
        'intervalle_jours_fin': request.GET.get('fin_jour', ''),
        'mois_debut': request.GET.get('mois_debut', ''),
        'mois_fin': request.GET.get('mois_fin', ''),
        'annee_analyse': request.GET.get('annee_analyse', ''),
        'produit_id': request.GET.get('produit', ''),
        'marque': request.GET.get('marque', ''),
        'tag': request.GET.get('tag', '')
    }

    try:
        # Application des filtres de date
        if filtres['jour_unique']:
            date_unique = datetime.strptime(filtres['jour_unique'], '%Y-%m-%d')
            start_of_day = timezone.make_aware(datetime.combine(date_unique, datetime.min.time()))
            end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)
            ventes_terminees = ventes_terminees.filter(date_vente__range=[start_of_day, end_of_day])
        
        elif filtres['intervalle_jours_debut'] or filtres['intervalle_jours_fin']:
            if filtres['intervalle_jours_debut']:
                debut_date = datetime.strptime(filtres['intervalle_jours_debut'], '%Y-%m-%d')
                start_of_day = timezone.make_aware(datetime.combine(debut_date, datetime.min.time()))
                ventes_terminees = ventes_terminees.filter(date_vente__gte=start_of_day)
            
            if filtres['intervalle_jours_fin']:
                fin_date = datetime.strptime(filtres['intervalle_jours_fin'], '%Y-%m-%d')
                end_of_day = timezone.make_aware(datetime.combine(fin_date, datetime.min.time())) + timedelta(days=1) - timedelta(seconds=1)
                ventes_terminees = ventes_terminees.filter(date_vente__lte=end_of_day)

        if filtres['mois_debut'] and filtres['mois_fin']:
            mois_debut = datetime.strptime(filtres['mois_debut'], '%Y-%m')
            mois_fin = datetime.strptime(filtres['mois_fin'], '%Y-%m')
            ventes_terminees = ventes_terminees.filter(
                date_vente__gte=mois_debut, 
                date_vente__lte=mois_fin + timedelta(days=31)
            )

        # Filtre de l'année d'analyse
        if filtres['annee_analyse']:
            try:
                annee_analyse = int(filtres['annee_analyse'])
                if annee_analyse < 1900 or annee_analyse > datetime.now().year:
                    raise ValueError("L'année spécifiée est en dehors de la plage acceptable.")
                ventes_terminees = ventes_terminees.filter(date_vente__year=annee_analyse)
            
            except ValueError as e:
                messages.error(request, f"L'année spécifiée n'est pas valide. {str(e)}")
                return redirect('vente_list')

        # Filtres supplémentaires
        if filtres['produit_id']:
            ventes_terminees = ventes_terminees.filter(produit__id=filtres['produit_id'])
        
        if filtres['marque']:
            ventes_terminees = ventes_terminees.filter(produit__marque__icontains=filtres['marque'])
        
        if filtres['tag']:
            ventes_terminees = ventes_terminees.filter(produit__tags__nom__icontains=filtres['tag'])

    except ValueError as e:
        logger.error(f"Erreur de filtre: {str(e)}")
        messages.error(request, "Les critères de filtrage ne sont pas valides.")
        return redirect('vente_list')

    # Pagination des ventes terminées
    paginator = Paginator(ventes_terminees.order_by('-date_vente'), 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calcul des métriques principales
    business_metrics = calculate_business_metrics(ventes_terminees)

    # Analyses avancées
    sales_trends = analyze_sales_trends(ventes_terminees, filtres['annee_analyse'])
    products_performance = analyze_products_performance(ventes_terminees, Produit.objects.filter(utilisateur=utilisateur))
    inventory_analysis = analyze_inventory(Produit.objects.filter(utilisateur=utilisateur), ventes_terminees)
    
    # Appel des fonctions IA sans modifier la logique existante
    sales_predictions = predict_future_sales(ventes_terminees, Produit.objects.filter(utilisateur=utilisateur))
    if request.method == 'POST':
        updated_count = 0
        deleted_count = 0
        invalid_ventes = []

        try:
            with transaction.atomic():
                action = request.POST.get('form_action')

                if action == 'update_ventes':
                    ventes_ids = request.POST.getlist('vente_id')
                    for vente_id in ventes_ids:
                        vente_attente = VenteAttente.objects.filter(id=vente_id, utilisateur=utilisateur).first()
                        if not vente_attente:
                            continue

                        try:
                            prix_achat = Decimal(request.POST.get(f'prix_achat_{vente_id}', '0'))
                            prix_vente = Decimal(request.POST.get(f'prix_vente_{vente_id}', '0'))
                            quantite = int(request.POST.get(f'quantite_vendue_{vente_id}', '0'))

                            if prix_achat <= 0 or prix_vente <= 0 or quantite <= 0:
                                invalid_ventes.append(f"{vente_attente.nom_produit} a des valeurs invalides.")
                                continue

                            produit = vente_attente.produit
                            print('produit stock', produit.quantite_stock , type(produit.quantite_stock) , 'quantite:', quantite , type(quantite))
                            if not produit or produit.quantite_stock < quantite:
                                stock_dispo = produit.quantite_stock if produit else 0
                                invalid_ventes.append(f"Stock insuffisant pour {vente_attente.nom_produit} (disponible : {stock_dispo})")
                                continue

                            Vente.objects.create(
                                utilisateur=utilisateur,
                                produit=produit,
                                nom_produit=vente_attente.nom_produit,
                                image_produit=vente_attente.image_produit,
                                prix_achat=prix_achat,
                                prix_vente=prix_vente,
                                quantite_vendue=quantite,
                                statut=True
                            )

                            vente_attente.delete()
                            updated_count += 1

                        except (ValueError, InvalidOperation) as e:
                            invalid_ventes.append(f"{vente_attente.nom_produit}: erreur de saisie - {str(e)}")
                            continue

                elif action == 'delete_ventes':
                    ventes_ids = request.POST.getlist('vente_id')
                    for vente_id in ventes_ids:
                        vente = VenteAttente.objects.filter(id=vente_id, utilisateur=utilisateur).first()
                        if not vente:
                            continue
                        vente.delete()
                        deleted_count += 1

            if updated_count > 0 and deleted_count > 0:
                messages.success(request, f"{updated_count} vente(s) mise(s) à jour et {deleted_count} vente(s) supprimée(s) avec succès")
            elif updated_count > 0:
                messages.success(request, f"{updated_count} vente(s) mise(s) à jour avec succès")
            elif deleted_count > 0:
                messages.success(request, f"{deleted_count} vente(s) supprimée(s) avec succès")

            for msg in invalid_ventes:
                messages.error(request, msg)

            if updated_count == 0 and deleted_count == 0 and not invalid_ventes:
                messages.info(request, "Aucune vente mise à jour ou supprimée")

        except Exception as e:
            logger.error(f"Erreur mise à jour et suppression des ventes: {str(e)}")
            messages.error(request, f"Erreur lors de la mise à jour ou de la suppression: {str(e)}")

        return redirect('vente_list')
    
    # Préparation des données pour le template
    context = {
        # Données de base
        'ventes': ventes_en_cours,
        'ventes_terminees': page_obj,
        'filtres': filtres,
        
        # Métriques principales
        **business_metrics,
        
        # Analyses avancées
        'sales_trends': sales_trends,
        'products_performance': products_performance,
        'inventory_analysis': inventory_analysis,
        
        # Données IA ajoutées
        'sales_predictions': sales_predictions,
        
        # Données supplémentaires pour les filtres
        'marques': Produit.objects.filter(utilisateur=utilisateur)
                        .exclude(marque__isnull=True)
                        .exclude(marque__exact='')
                        .values_list('marque', flat=True)
                        .distinct(),
        'tags': Tag.objects.filter(produits__utilisateur=utilisateur).distinct(),
        'produits': Produit.objects.filter(utilisateur=utilisateur),
        
        # Paramètres de pagination
        'paginator': paginator,
    }

    return render(request, 'vente_list.html', context)