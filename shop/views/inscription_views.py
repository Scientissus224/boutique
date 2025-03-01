from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from shop.forms import InscriptionUtilisateurForm, InscriptionClientForm , Client
from shop.models import UtilisateurTemporaire
from shop.token import generator_token
import logging
import random
import string

class InscriptionUtilisateurView(View):
    def get(self, request):
        """ Afficher le formulaire d'inscription """
        form = InscriptionUtilisateurForm()
        return render(request, 'inscription.html', {'form': form})

    def post(self, request):
        """ Traiter les données du formulaire d'inscription """
        form = InscriptionUtilisateurForm(request.POST)
        
        if form.is_valid():
            # Récupérer les données du formulaire
            nom_complet = form.cleaned_data['nom_complet']
            numero = form.cleaned_data['numero']
            nom_boutique = form.cleaned_data['nom_boutique']
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']

            try:
                # Vérifier si un utilisateur avec le même email existe déjà
                email_existant = UtilisateurTemporaire.objects.filter(email=email).first()

                if email_existant:
                    email_existant.delete()  # Supprimer l'utilisateur ayant le même email
                    print("Utilisateur avec cet email supprimé.")

                # Vérifier si un utilisateur avec les mêmes informations existe déjà
                utilisateur_existant = UtilisateurTemporaire.objects.filter(
                    email=email,
                    numero=numero,
                    nom_boutique=nom_boutique
                ).first()  # On prend le premier utilisateur trouvé

                if utilisateur_existant:
                    utilisateur_existant.delete()  # Supprimer l'utilisateur existant
                    print("Ancien utilisateur supprimé.")

                identifiant_unique = generate_readable_identifier(email)
                # Créer un utilisateur temporaire
                utilisateur_temporaire = UtilisateurTemporaire.objects.create(
                    identifiant_unique=identifiant_unique,
                    email=email,
                    nom_complet=nom_complet,
                    numero=numero,
                    nom_boutique=nom_boutique,
                    password=password1,
                )
                utilisateur_temporaire.save()

                # Générer un token unique pour cet utilisateur temporaire
                token = generator_token.make_token(utilisateur_temporaire)

                # Assigner le token généré à l'utilisateur temporaire
                utilisateur_temporaire.token = token
                utilisateur_temporaire.save()

                # Message de succès
                messages.success(request, 'Votre compte a été créé avec succès ! Pour finaliser votre inscription, veuillez renseigner les informations demandées ci-dessous.')


                # Rediriger vers la vue 'informations_supplementaires' avec l'ID de l'utilisateur temporaire
                return redirect('informations_supplementaires', utilisateur_temporaire_id=utilisateur_temporaire.id)

            except Exception as e:
                # En cas d'erreur lors de la création
                messages.error(request, f'Erreur lors de la création de votre compte : {e}')
                print(f'Erreur lors de la création de votre compte : {e}')
                return redirect('inscription')

        # Si le formulaire est invalide, afficher les erreurs
        return render(request, 'inscription.html', {'form': form})


# Configuration du logger
logger = logging.getLogger(__name__)

class InscriptionClientView(View):
    def get(self, request):
        """ Afficher le formulaire d'inscription """
        form = InscriptionClientForm()
        return render(request, 'inscription_client.html', {'form': form})

    def post(self, request):
        """ Traiter les données du formulaire d'inscription """
        form = InscriptionClientForm(request.POST)

        if form.is_valid():
            try:
                # Récupérer les données du formulaire
                nom_complet = form.cleaned_data['nom_complet']
                telephone = form.cleaned_data['telephone']
                adresse = form.cleaned_data['adresse']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password1']

                # Créer un client avec les données validées
                client = Client(
                    nom_complet=nom_complet,
                    telephone=telephone,
                    adresse=adresse,
                    email=email
                )
                # Utiliser set_password pour sécuriser le mot de passe
                client.set_password(password)
                client.is_active = True  # Activer le client après inscription
                client.save()

                # Message de succès
                messages.success(request, 'Votre compte a été créé et activé avec succès !')

                # Rediriger vers la page de connexion après l'inscription réussie
                return redirect('login')

            except Exception as e:
                # Enregistrer l'exception dans les logs
                logger.error(f"Erreur lors de la création du client : {str(e)}")
                # Gestion des exceptions inattendues
                messages.error(request, f'Une erreur inattendue est survenue : {str(e)}')
                return render(request, 'inscription_client.html', {'form': form})

        else:
            # Afficher les erreurs de validation dans le formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans le champ '{field}': {error}")

        return render(request, 'inscription_client.html', {'form': form})
    
# Fonction pour générer un identifiant unique
def generate_readable_identifier(email, platform_name="warabaGuinee"):
    """Génère un identifiant unique, lisible et facile à retenir."""
    if "@" not in email or len(email.split('@')[0]) < 6:
        raise ValueError("Email invalide ou trop court pour générer un identifiant.")

    email_prefix = email.split('@')[0]  # Récupère tout avant le @

    # Prend les 6 premières lettres du préfixe de l'email
    short_prefix = email_prefix[:6]

    # Ajoute 4 chiffres aléatoires pour assurer l'unicité
    random_numbers = ''.join(random.choices(string.digits, k=4))

    # Génère l'identifiant final
    return f"{platform_name}-{short_prefix}-{random_numbers}"

# Exemple d'utilisation
email = "exemple@gmail.com"
print(generate_readable_identifier(email))