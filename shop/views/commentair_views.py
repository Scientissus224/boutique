from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.db.models import Avg
from shop.models import Commentaire, Produit,Boutique
from django.db.models import Avg
import re

# Fonction pour valider l'email
def valider_email(email):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA0-9-.]+$)"
    if not re.match(email_regex, email):
        raise ValidationError("L'email fourni n'est pas valide.")

# Fonction pour envoyer l'email de notification
def envoyer_email_commentaire(boutique, produit_nom, commentaire, note, utilisateur_mail):
    subject = f"Commentaire sur la boutique {boutique}"
    note = note if note is not None else 0  # Mettre 0 si la note est absente
    etoiles = [1, 2, 3, 4, 5]

    # Charger le template d'email avec les données
    html_message = render_to_string('commentaire.html', {
        'boutique': boutique,
        'produit_nom': produit_nom,  # Ajout du nom du produit
        'commentaire': commentaire,
        'note': note,
        'etoiles': etoiles,
    })

    # Création et envoi de l'email
    email_message = EmailMessage(subject, html_message, to=[utilisateur_mail])
    email_message.content_subtype = "html"

    # Envoi sécurisé avec gestion d'erreurs
    try:
        email_message.send(fail_silently=False)
        return True  # Succès
    except Exception as e:
        print(f"Erreur d'envoi d'email : {e}")
        return False  # Échec





def poster_commentaire(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    utilisateur = produit.utilisateur  # Utilisateur du produit (le vendeur)
     # Récupérer la boutique lié à cet utilisateur
    boutique_id = get_object_or_404(Boutique, utilisateur_id=utilisateur.id)
    boutique = utilisateur.nom_boutique
    utilisateur_mail = utilisateur.email
    produit_nom = produit.nom  # Nom du produit à inclure dans l'email

    if request.method == "POST":
        try:
            # Récupération des données du formulaire
            commentaire = request.POST.get('comment', '').strip()
            note = request.POST.get('rating', None)
            image_profil = request.FILES.get('image_profil')

            # Validation des champs obligatoires
            if not commentaire:
                messages.error(request, "Le champ commentaire est obligatoire.")
                return redirect('poster_commentaire', produit_id=produit_id)  # Redirection avec produit_id

            # Validation de la note
            try:
                note = int(note) if note is not None else 0
            except ValueError:
                note = 0

            # Envoi de l'email avant l'enregistrement du commentaire
            email_envoye = envoyer_email_commentaire(boutique, produit_nom, commentaire, note, utilisateur_mail)
            
            if not email_envoye:
                messages.error(request, "Erreur lors de l'envoi de l'email. Le commentaire n'a pas été enregistré.")
                return redirect('poster_commentaire', produit_id=produit_id)  # Redirection avec produit_id

            # Sauvegarde du commentaire SEULEMENT si l'email est bien envoyé
            Commentaire.objects.create(
                utilisateur=utilisateur,
                produit=produit,  # Lien avec le produit
                commentaire=commentaire,
                note=note,
                image_profil=image_profil if image_profil else None  # Si une image est envoyée, l'ajouter, sinon None
            )

            messages.success(request, "Votre commentaire a été ajouté avec succès !")
            return redirect('poster_commentaire', produit_id=produit_id)  # Redirection avec produit_id

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
            print(e)

        return redirect('poster_commentaire', produit_id=produit_id)  # Redirection avec produit_id

    # Récupération des commentaires existants pour affichage
    commentaires = Commentaire.objects.filter(produit=produit).order_by('-date_commentaire') 

    # Calcul de la moyenne des notes des commentaires
    moyenne_notes = commentaires.aggregate(Avg('note'))['note__avg'] or 0  # Si pas de commentaires, la moyenne est 0

    # Calcul des étoiles pour l'affichage de la moyenne
    etoiles_moyenne = round(moyenne_notes)  # Arrondir la moyenne à l'entier le plus proche

    # Plage pour les étoiles
    etoiles_range = range(1, 6)

    # Calcul des étoiles pour chaque commentaire
    for commentaire in commentaires:
        commentaire.etoiles = '★' * commentaire.note + '☆' * (5 - commentaire.note)

    return render(request, "commentaires.html", {
        "produit": produit,  # Passer le produit pour l'affichage de l'image et de la description
        "commentaires": commentaires,
        "moyenne_notes": moyenne_notes,
        "etoiles_moyenne": etoiles_moyenne,  # Passer la moyenne des étoiles calculées
        "etoiles_range": etoiles_range,  # Passer la plage des étoiles pour l'affichage dans le template
        'user_id':utilisateur.id,
        'boutique_id':boutique_id.pk
    })