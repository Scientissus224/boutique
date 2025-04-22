from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Avg
from shop.models import Commentaire, Produit,Boutique,Localisation
from django.db.models import Avg
from django.urls import reverse
import re

# Fonction pour valider l'email
def valider_email(email):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA0-9-.]+$)"
    if not re.match(email_regex, email):
        raise ValidationError("L'email fourni n'est pas valide.")

# Fonction pour envoyer l'email de notification
def envoyer_email_commentaire(boutique, produit_nom,produit_image, commentaire, note, utilisateur_mail):
    subject = f"Commentaire sur la boutique {boutique}"
    note = note if note is not None else 0  # Mettre 0 si la note est absente
    etoiles = [1, 2, 3, 4, 5]

    # Charger le template d'email avec les données
    html_message = render_to_string('commentaire.html', {
        'boutique': boutique,
        'produit_nom': produit_nom,  # Ajout du nom du produit
        'produit_image':produit_image,
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





def poster_commentaire(request, produit_identifiant):
    produit = get_object_or_404(Produit, identifiant=produit_identifiant)
    utilisateur = produit.utilisateur
    boutique_id = get_object_or_404(Boutique, utilisateur_id=utilisateur.id)
    localisation = Localisation.objects.filter(utilisateur=utilisateur).first()
    boutique = utilisateur.nom_boutique
    utilisateur_mail = utilisateur.email
    produit_nom = produit.nom
    produit_image = produit.image.url if produit.image else None

    if request.method == "POST":
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Gestion AJAX
            try:
                commentaire = request.POST.get('comment', '').strip()
                note = request.POST.get('rating', None)
                image_profil = request.FILES.get('image_profil')

                if not commentaire:
                    return JsonResponse({
                        'success': False,
                        'message': "Le champ commentaire est obligatoire."
                    }, status=400)

                try:
                    note = int(note) if note is not None else 0
                except ValueError:
                    note = 0

                # D'abord envoyer l'email
                email_envoye = envoyer_email_commentaire(boutique, produit_nom, produit_image, commentaire, note, utilisateur_mail)
                
                if not email_envoye:
                    return JsonResponse({
                        'success': False,
                        'message': "Erreur lors de l'envoi de l'email. Le commentaire n'a pas été enregistré."
                    }, status=500)

                # Ensuite créer le commentaire seulement si l'email est envoyé
                nouveau_commentaire = Commentaire.objects.create(
                    utilisateur=utilisateur,
                    produit=produit,
                    commentaire=commentaire,
                    note=note,
                    image_profil=image_profil if image_profil else None
                )

                return JsonResponse({
                    'success': True,
                    'message': "Votre commentaire a été ajouté avec succès et l'email a été envoyé !",
                    'redirect': reverse('poster_commentaire', args=[produit.identifiant])
                })

            except ValidationError as e:
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=400)
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f"Erreur : {e}"
                }, status=500)

        # Gestion non-AJAX (fallback)
        try:
            commentaire = request.POST.get('comment', '').strip()
            note = request.POST.get('rating', None)
            image_profil = request.FILES.get('image_profil')

            if not commentaire:
                messages.error(request, "Le champ commentaire est obligatoire.")
                return redirect('poster_commentaire', produit_identifiant=produit.identifiant)

            try:
                note = int(note) if note is not None else 0
            except ValueError:
                note = 0

            # D'abord envoyer l'email
            email_envoye = envoyer_email_commentaire(boutique, produit_nom, produit_image, commentaire, note, utilisateur_mail)
            
            if not email_envoye:
                messages.error(request, "Erreur lors de l'envoi de l'email. Le commentaire n'a pas été enregistré.")
                return redirect('poster_commentaire', produit_identifiant=produit.identifiant)

            # Ensuite créer le commentaire seulement si l'email est envoyé
            Commentaire.objects.create(
                utilisateur=utilisateur,
                produit=produit,
                commentaire=commentaire,
                note=note,
                image_profil=image_profil if image_profil else None
            )

            messages.success(request, "Votre commentaire a été ajouté avec succès!")
            return redirect('poster_commentaire', produit_identifiant=produit.identifiant)

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Erreur : {e}")

        return redirect('poster_commentaire', produit_identifiant=produit.identifiant)

    # Récupération des commentaires existants
    commentaires = Commentaire.objects.filter(produit=produit).order_by('-date_commentaire') 
    moyenne_notes = commentaires.aggregate(Avg('note'))['note__avg'] or 0
    etoiles_moyenne = round(moyenne_notes)
    etoiles_range = range(1, 6)

    for commentaire in commentaires:
        commentaire.etoiles = '★' * commentaire.note + '☆' * (5 - commentaire.note)

    return render(request, "commentaires.html", {
        "produit": produit,
        "commentaires": commentaires,
        'utilisateur_email': utilisateur.email,
        'utilisateur_numero': utilisateur.numero,
        "localisation": localisation,
        'logo': utilisateur.logo_boutique.url if utilisateur.logo_boutique else None,
        'shop_name': utilisateur.nom_boutique,
        "moyenne_notes": moyenne_notes,
        "etoiles_moyenne": etoiles_moyenne,
        "etoiles_range": etoiles_range,
        'user_id': utilisateur.id,
        "home_boutique": reverse('boutique_contenu', args=[boutique_id.identifiant]),
        'boutique_id': boutique_id.pk,
        'utilisateur_identifiant': utilisateur.identifiant_unique
    })