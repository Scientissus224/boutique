from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from shop.models import Boutique

def get_boutique_html_path(boutique_identifiant):
    """
    Génère le chemin dynamique vers le contenu HTML d'une boutique en utilisant l'identifiant textuel.
    """
    return reverse('boutique_contenu', args=[boutique_identifiant])

def boutique_contenu(request, boutique_identifiant):
    """
    Vue pour afficher le contenu HTML spécifique d'une boutique en utilisant l'identifiant textuel.
    """
    boutique = get_object_or_404(Boutique, identifiant=boutique_identifiant)  # Recherche par identifiant au lieu de l'ID
    context = {
        "html_contenu": boutique.html_contenu,
        "nom_boutique": f"Boutique {boutique.utilisateur.nom_complet}",
        "boutique": boutique,  # Ajout de l'objet boutique complet au contexte
    }
    return render(request, 'boutique_wrapper.html', context)