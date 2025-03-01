"""
URL configuration for boutique project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from shop.views import (
    InscriptionUtilisateurView,
    home,
    site,
    activate,
    login,
    table,
    parametres,
    logout_view,
    gestion_produits,
    gestion_slider,
    gestion_localisation,
    informations_supplementaires_view,
    table_petite, 
    table_croissance,
    InscriptionClientView,
    plat_forme,
    detail_produits,
    poster_commentaire,
    afficher_produit,
    afficher_produits_panier,
   ajouter_variante_au_panier,
    gestion_boutique,
    get_total_panier,
    boutique_contenu,
    rechercher_produits,
    ajouter_produit_au_panier,
    ajouter_variante_au_panier,
    reinitialiser_panier,
    obtenir_panier,
   obtenir_panier_table,
   retirer_produit_du_panier,
   retirer_variante_du_panier,
   envoyer_commande,
   rechercher_produits,
   commandes_utilisateur,
   produits_sans_variante,
   rechercher_boutiques_ajax,
   demander_reinitialisation,
   renitialisation_mail,
   reset_password,
   password_reset_complete,
   statut_validation_compte,
   update_utilisateur_status,
   statistiques_commandes,
   vente_list,
   mise_a_jour_quantite,

afficher_session_id,


)


urlpatterns = [
    # Route pour l'interface d'administration de Django
    path('admin/', admin.site.urls, name='admin'),

    # Route pour l'inscription d'un utilisateur, utilisant la vue InscriptionUtilisateurView
    path('inscription/', InscriptionUtilisateurView.as_view(), name='inscription'),
    path('inscription_client/', InscriptionClientView.as_view(), name='inscription_client'),
    path('informations-supplementaires/<int:utilisateur_temporaire_id>/', informations_supplementaires_view, name='informations_supplementaires'),
    #Route pour l'activation 
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('login/', login, name='login'),
    path('logout/', logout_view, name='logout'),  # URL pour la déconnexion
    path('table/', table, name='table'),  # Tableau de bord
    path('table_croissance/', table_croissance, name='table_croissance'),  # Tableau de bord
    path('table_petite/', table_petite, name='table_petite'),  # Tableau de bord
    path('profil/', parametres , name='profil'),
    path('produits/',gestion_produits , name = 'produits'),
    path('detail_produits/<int:produit_id>/', detail_produits, name='detail_produits'),
    path('poster_commentaire/<int:produit_id>/', poster_commentaire, name='poster_commentaire'),
    path('panier/<int:utilisateur_id>/', afficher_produits_panier, name='panier'),
    path('afficher_produit/<int:produit_id>/utilisateur/<int:utilisateur_id>/', afficher_produit, name='afficher_produit'),
    path('sliders/',gestion_slider, name = 'sliders'),
    path('gestion_boutique/',gestion_boutique ,name='gestion_boutique'),
    path('localisation/',gestion_localisation, name = 'localisation'),
    path('get-total-panier/<int:user_id>/', get_total_panier, name='get-total-panier'),
    path('site/' , site , name = 'site'),
    path('boutiques/<int:boutique_id>/html_contenu/', boutique_contenu, name='boutique_contenu'),  # Route pour le contenu HTML d'une boutique
    path('platForm/' , plat_forme , name = 'platForm'),
    path('rechercher-produits/', rechercher_produits, name='rechercher-produits'),
    path('ajouter_produit_au_panier/<int:produit_id>/',ajouter_produit_au_panier, name='ajouter_produit_au_panier'),
    path('ajouter_variante_au_panier/<int:variante_id>/', ajouter_variante_au_panier, name='ajouter_variante_au_panier'),
    path('reinitialiser-panier/', reinitialiser_panier, name='reinitialiser_panier'),
    path('obtenir-panier/', obtenir_panier, name='obtenir_panier'),
    path('statut_validation_compte/', statut_validation_compte, name='statut_validation_compte'),
    path('obtenir_panier_table/', obtenir_panier_table, name='obtenir_panier_table'),
    path('retirer_produit/<int:produit_id>/', retirer_produit_du_panier, name='retirer_produit'),
    path('retirer_variante/<int:variante_id>/',retirer_variante_du_panier, name='retirer_variante'),
    path('envoyer-commande/<int:user_id>/', envoyer_commande, name='envoyer_commande'),
    path('recherche-produit/<int:utilisateur_id>/', rechercher_produits, name='recherche_produit'),
    path('commandes_utilisateur/',commandes_utilisateur, name='commandes_utilisateur'),
    path('update_status/',update_utilisateur_status, name='update_status'),
    path('produits-sans-variante/<int:utilisateur_id>/',produits_sans_variante, name='produits_sans_variante'),
    path('rechercher-boutiques/', rechercher_boutiques_ajax, name='rechercher_boutiques'),
    path('statistiques-commandes/', statistiques_commandes, name='statistiques_commandes'),
    path('vente_list/', vente_list, name='vente_list'),
    path('update_quantite/', mise_a_jour_quantite, name='update_quantite'),
    # Route pour la page d'accueil du site, utilisant la vue home
    path('', home, name='accueil'),
    
# Vue pour afficher le formulaire de réinitialisation du mot de passe
    path('password-reset/',  demander_reinitialisation, name='password_reset'),
    path('afficher_session_id/', afficher_session_id, name='afficher_session_id'),

    # Vue qui affiche un message après l'envoi de l'email
    path('renitialisation_mail/', renitialisation_mail, name='renitialisation_mail'),

    # Vue pour la confirmation de la réinitialisation du mot de passe
    path('password_reset_confirm/<uidb64>/<token>/', reset_password, name='password_reset_confirm'),

    # Vue de confirmation après la réinitialisation du mot de passe
    path('password_reset_complete/', password_reset_complete, name='password_reset_complete'),
]

handler404 = 'shop.views.custom_404'


# Configuration pour servir les fichiers médias en mode DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
