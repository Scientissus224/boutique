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
   reinitialiser_compteurs,
   obtenir_panier_table,
   retirer_du_panier,
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
    obtenir_produits_ajax,
    ajouter_produit_aux_likes, 
    retirer_produit_des_likes,
    obtenir_like,
     likes_site,
     obtenir_produits_likes,
     demo_interactive,
    get_csrf_token,
   gestion_produits_utilisateurs,
   gestion_utilisateurs_boutiques,
      


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
    path('poster_commentaire/<uuid:produit_identifiant>/', poster_commentaire, name='poster_commentaire'),
    path('panier/<str:utilisateur_identifiant>/', afficher_produits_panier, name='panier'),
    path('afficher_produit/<uuid:produit_identifiant>/<str:utilisateur_identifiant>/', afficher_produit, name='afficher_produit'),
    path('sliders/',gestion_slider, name = 'sliders'),
    path('gestion_boutique/',gestion_boutique ,name='gestion_boutique'),
    path('localisation/',gestion_localisation, name = 'localisation'),
    path('get-total-panier/<int:user_id>/', get_total_panier, name='get-total-panier'),
    path('site/' , site , name = 'site'),
  # Route pour le contenu HTML d'une boutique
    path('platForm/' , plat_forme , name = 'platForm'),
    path('rechercher-produits/', rechercher_produits, name='rechercher-produits'),
    path('ajouter_produit_au_panier/<int:produit_id>/',ajouter_produit_au_panier, name='ajouter_produit_au_panier'),
    path('ajouter_variante_au_panier/<int:variante_id>/', ajouter_variante_au_panier, name='ajouter_variante_au_panier'),
    path('reinitialiser-panier/', reinitialiser_panier, name='reinitialiser_panier'),
    path('obtenir_panier/', obtenir_panier, name='obtenir_panier'),
    path('obtenir_like/', obtenir_like, name='obtenir_like'),
    path('reinitialiser_compteurs/', reinitialiser_compteurs, name='reinitialiser_compteurs'),
    path('statut_validation_compte/', statut_validation_compte, name='statut_validation_compte'),
    path('obtenir_panier_table/', obtenir_panier_table, name='obtenir_panier_table'),
    path('obtenir_produits_likes/', obtenir_produits_likes, name='obtenir_produits_likes'),
    path('retirer-du-panier/<int:item_id>/<str:item_type>/', retirer_du_panier, name='retirer_du_panier'),
    path('envoyer-commande/<int:user_id>/', envoyer_commande, name='envoyer_commande'),
    path('commandes_utilisateur/',commandes_utilisateur, name='commandes_utilisateur'),
    path('update_status/',update_utilisateur_status, name='update_status'),
    path('produits-sans-variante/<int:utilisateur_id>/',produits_sans_variante, name='produits_sans_variante'),
    path('rechercher_boutiques_ajax/', rechercher_boutiques_ajax, name='rechercher_boutiques_ajax'),
    path('statistiques-commandes/', statistiques_commandes, name='statistiques_commandes'),
    path('vente_list/', vente_list, name='vente_list'),
    path('update_quantite/', mise_a_jour_quantite, name='update_quantite'),
    path('demo/WarabaGuinee/', demo_interactive, name='demo/WarabaGuinee'),
    path('produits/ajax/<int:utilisateur_id>/', obtenir_produits_ajax, name='obtenir_produits_ajax'),
    path('produits/recherche/<int:utilisateur_id>/', rechercher_produits, name='recherche_produit'),
    path('ajouter-aux-likes/<int:produit_id>/', ajouter_produit_aux_likes, name='ajouter_aux_likes'),
    path('retirer-des-likes/<int:produit_id>/', retirer_produit_des_likes, name='retirer_des_likes'),
    path('utilisateur/<str:utilisateur_identifiant>/likes/', likes_site, name='likes_site'),
    path('get-csrf-token/',get_csrf_token, name='get_csrf_token'),
    path('gestion-produits-utilisateurs/', gestion_produits_utilisateurs, name='gestion_produits_utilisateurs'),
    path('gestion-utilisateurs/', gestion_utilisateurs_boutiques, name='gestion_utilisateurs_boutiques'),
    
    # Route pour la page d'accueil du site, utilisant la vue home
    path('', home, name='accueil'),
    
# Vue pour afficher le formulaire de réinitialisation du mot de passe
    path('password-reset/',  demander_reinitialisation, name='password_reset'),

    # Vue qui affiche un message après l'envoi de l'email
    path('renitialisation_mail/', renitialisation_mail, name='renitialisation_mail'),

    # Vue pour la confirmation de la réinitialisation du mot de passe
    path('password_reset_confirm/<uidb64>/<token>/', reset_password, name='password_reset_confirm'),

    # Vue de confirmation après la réinitialisation du mot de passe
    path('password_reset_complete/', password_reset_complete, name='password_reset_complete'),
    path('<str:boutique_identifiant>/', boutique_contenu, name='boutique_contenu'),
]

handler404 = 'shop.views.custom_404'


# Configuration pour servir les fichiers statiques et médias en mode DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

