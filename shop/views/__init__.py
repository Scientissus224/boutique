from .home_views import home , rechercher_boutiques_ajax
from .boutique_url_views import boutique_contenu, get_boutique_html_path

__all__ = ['home', 'boutique_contenu', 'get_boutique_html_path']  # Expose ces éléments pour les imports

from .table_views import table , table_petite, table_croissance,plat_forme
from .inscription_views import InscriptionUtilisateurView,InscriptionClientView
from .auth_views import activate
from .product_views import gestion_produits
from .slider_views import gestion_slider
from .localisation_views import gestion_localisation
from .site_views import site
from .login_views import login
from .parametres_views import parametres
from .logout_views import logout_view
from .question_utilisateurs import informations_supplementaires_view
from .produit_detail_views import detail_produits
from .commentair_views import poster_commentaire
from .produits_site import afficher_produit
from .views_panier import afficher_produits_panier
from .site_line_views import gestion_boutique
from .counter_panier_views import get_total_panier
from .panier_client_views import  ajouter_produit_au_panier ,afficher_session_id, ajouter_variante_au_panier,retirer_produit_du_panier,retirer_variante_du_panier
from .renitialiser_panier_views import reinitialiser_panier
from .panier_contenu import obtenir_panier
from .tableau_panier import  obtenir_panier_table
from .commande_views import envoyer_commande
from .rechercher_produits import rechercher_produits
from .commande_effectuer import commandes_utilisateur
from .produits_sans_variantes import produits_sans_variante
from .renitialisation_pass import (
    demander_reinitialisation,
    renitialisation_mail,
    reset_password,
    password_reset_complete
)
from .validation_compte_views import statut_validation_compte
from .support_client_views import update_utilisateur_status
from .statistique_commande import statistiques_commandes
from .vente_views import vente_list
from .new_quantite import mise_a_jour_quantite
from .custom_404_views import custom_404

