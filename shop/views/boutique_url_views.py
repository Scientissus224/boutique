from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from shop.models import Boutique

def get_boutique_html_path(boutique_id):
    """
    Génère le chemin dynamique vers le contenu HTML d'une boutique.
    """
    return reverse('boutique_contenu', args=[boutique_id])

def boutique_contenu(request, boutique_id):
    """
    Vue pour afficher le contenu HTML spécifique d'une boutique.
    """
    boutique = get_object_or_404(Boutique, id=boutique_id)  # Récupère la boutique ou lève une erreur 404
    context = {
        "html_contenu": boutique.html_contenu,  # Contenu HTML à afficher
        "nom_boutique": f"Boutique {boutique.utilisateur.nom_complet}",  # Nom de la boutique
    }
    return render(request, 'boutique_wrapper.html', context)
