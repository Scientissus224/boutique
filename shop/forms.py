# forms.py
from django import forms
from datetime import time, datetime
from django.core.validators import RegexValidator 
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .const_models import COULEURS
from django.core.exceptions import ValidationError
from .models import (
    Utilisateur,
    SupportClient,
    Produit,
    SliderImage,
    Localisation,
    LocalImages,
    Devise,
   InformationsSupplementairesTemporaire,
   Client,
   ProduitImage,
   Tag,
   Variante,
   Boutique,
   


)

#---------------------------------Gestion d'inscription pour les Utilisateurs------------------------------------
class InscriptionUtilisateurForm(UserCreationForm):
    nom_complet = forms.CharField(
        max_length=200,
        required=True,
        label="Nom complet",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre nom complet',
            'pattern': r"^[a-zA-ZÀ-ÿ' -]+$",  # Lettres, accents, espaces, apostrophes, tirets
            'title': "Le nom complet ne doit contenir que des lettres, des espaces ou des caractères spéciaux valides."
        })
    )
    numero = forms.CharField(
        max_length=15,
        required=True,
        label="Numéro de téléphone",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre numéro de téléphone',
            'pattern': r'^\d{9,15}$',  # Seulement des chiffres entre 9 et 15 caractères
            'title': "Le numéro de téléphone doit comporter entre 9 et 15 chiffres."
        })
    )
    nom_boutique = forms.CharField(
        max_length=200,
        required=True,
        label="Nom de la boutique",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez le nom de votre boutique',
            'pattern': r'^[a-zA-ZÀ-ÿ0-9\' -]+$',  # Lettres, chiffres, accents, espaces, apostrophes, tirets
            'title': "Le nom de la boutique peut contenir des lettres, chiffres et caractères spéciaux valides."
        })
    )
    email = forms.EmailField(
        required=True,
        label="Adresse email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre adresse email'
        })
    )

    class Meta:
        model = Utilisateur
        fields = ['nom_complet', 'numero', 'nom_boutique', 'email', 'password1', 'password2']
        widgets = {
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez votre mot de passe',
                'pattern': r'^(?=.*[A-Z])(?=.*\d)[A-Za-z\d@#$%^&+=!]{8,}$',  # Minimum 8 caractères, une majuscule, un chiffre
                'title': "Le mot de passe doit contenir au moins 8 caractères, une majuscule, et un chiffre."
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Confirmez votre mot de passe'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if any(model.objects.filter(email=email).exists() for model in [Utilisateur, Client, SupportClient]):

            raise ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        if Utilisateur.objects.filter(numero=numero).exists() or Client.objects.filter(telephone=numero).exists():
            raise ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return numero

#---------------------------------Gestion de la mise à jour des Utilisateurs ------------------------------------
class MiseAJourUtilisateurForm(UserChangeForm):
    """
    Formulaire pour la mise à jour des informations de l'utilisateur,
    sans la gestion du mot de passe.
    """

    class Meta:
        model = Utilisateur
        fields = ['nom_complet', 'numero', 'nom_boutique', 'email', 'logo_boutique']  # Ajout du champ logo_boutique

    def __init__(self, *args, **kwargs):
        """
        Initialisation du formulaire. Permet de pré-remplir les champs avec la valeur stockée dans la session, si disponible.
        """
        self.request = kwargs.pop('request', None)  # Accepter la requête dans l'init
        super().__init__(*args, **kwargs)

        # Supprimer le champ mot de passe du formulaire
        self.fields.pop('password', None)

    def clean_email(self):
        """
        Vérifier si l'email existe déjà pour un autre utilisateur.
        """
        email = self.cleaned_data.get('email')
        if Utilisateur.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Cet email est déjà utilisé par un autre utilisateur.")
        return email

    def clean_numero(self):
        """
        Vérifier si le numéro de téléphone existe déjà pour un autre utilisateur.
        """
        numero = self.cleaned_data.get('numero')
        if Utilisateur.objects.filter(numero=numero).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ce numéro de téléphone est déjà utilisé par un autre utilisateur.")
        return numero

    def save(self, commit=True):
        """
        Sauvegarder les informations de l'utilisateur sans modifier le mot de passe.
        """
        user = super().save(commit=False)

        # Si un logo est fourni et a été modifié, il est mis à jour
        if 'logo_boutique' in self.changed_data:
            logo = self.cleaned_data.get('logo_boutique')
            if logo:
                user.logo_boutique = logo

        # Le mot de passe ne sera pas mis à jour, donc on ne s'en occupe plus
        if commit:
            user.save()
        return user
#---------------------------------Gestion des infos supplementaires-----------------------------------


class InformationsSupplementairesForm(forms.ModelForm):
    class Meta:
        model = InformationsSupplementairesTemporaire
        fields = ['type_boutique', 'produits_vendus', 'source_decouverte']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Définir les classes pour les champs
        self.fields['type_boutique'].widget.attrs.update({'class': 'form-control'})
        
        # Champ de la liste déroulante pour produits_vendus
        self.fields['produits_vendus'].widget.attrs.update({'class': 'form-control'})
        
        # Champ source_decouverte
        self.fields['source_decouverte'].widget.attrs.update({'class': 'form-control'})

#---------------------------------Gestion de l'inscription des Clients-----------------------------------
class InscriptionClientForm(UserCreationForm):
    nom_complet = forms.CharField(
        max_length=200,
        required=True,
        label="Nom complet",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre nom complet',
            'pattern': r"^[a-zA-ZÀ-ÿ' -]+$",
            'title': "Le nom complet ne doit contenir que des lettres, des espaces ou des caractères spéciaux valides."
        })
    )
    telephone = forms.CharField(
        max_length=15,
        required=True,
        label="Numéro de téléphone",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre numéro de téléphone',
            'pattern': r'^\d{9,15}$',
            'title': "Le numéro de téléphone doit comporter entre 9 et 15 chiffres."
        })
    )
    adresse = forms.CharField(
        max_length=200,
        required=True,
        label="Adresse",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre adresse',
            'title': "L'adresse ne doit pas dépasser 200 caractères."
        })
    )
    email = forms.EmailField(
        required=True,
        label="Adresse email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre adresse email',
            'title': "Veuillez entrer une adresse email valide."
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre mot de passe',
            'pattern': r'^(?=.*[A-Z])(?=.*\d)(?=.*[@#$%^&+=!])[A-Za-z\d@#$%^&+=!]{8,}$',
            'title': "Le mot de passe doit contenir au moins 8 caractères, une majuscule, un chiffre, et un caractère spécial."
        }),
        label="Mot de passe",
        required=True,
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmez votre mot de passe',
            'title': "Veuillez confirmer votre mot de passe."
        }),
        label="Confirmation du mot de passe",
        required=True,
    )

    class Meta:
        model = Utilisateur
        fields = ['nom_complet', 'telephone', 'adresse', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Utilisateur.objects.filter(email=email).exists() or Client.objects.filter(email=email).exists():
            raise ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone and (not telephone.isdigit() or len(telephone) < 9 or len(telephone) > 15):
            raise ValidationError("Le numéro de téléphone doit comporter entre 9 et 15 chiffres.")
        if Utilisateur.objects.filter(numero=telephone).exists() or Client.objects.filter(telephone=telephone).exists():
            raise ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return telephone

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                self.add_error('password2', "Les mots de passe ne correspondent pas.")
        
        return cleaned_data
#---------------------------------Gestion des Produits------------------------------------
class ProduitForm(forms.ModelForm):
    etat = forms.ChoiceField(
        label='État',
        choices=Produit.ETAT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    mise_en_avant = forms.ChoiceField(
        label='Mettre en avant',
        choices=Produit.MISE_EN_AVANT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Champ pour l'image principale
    image = forms.ImageField(
        required=False,
        label='Image principale',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    # Autres champs du produit
    nom = forms.CharField(
        label='Nom du produit', 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        label='Description', 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    prix = forms.DecimalField(
        label='Prix', 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    ancien_prix = forms.DecimalField(
        label='Ancien Prix', 
        required=False,  # Optionnel si le produit n'est pas en promo
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    quantite_stock = forms.IntegerField(
        label='Quantité en stock', 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    reference = forms.CharField(
        label='Référence', 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    marque = forms.CharField(
        label='Marque', 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    poids = forms.DecimalField(
        label='Poids (kg)', 
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    dimensions = forms.CharField(
        label='Dimensions', 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Tags (Champ ManyToMany pour les tags associés)
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}), 
        required=False
    )

    # Vidéo promotionnelle (URL)
    video_promotionnelle = forms.URLField(
        label='Vidéo promotionnelle', 
        required=False, 
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )

    # Champ pour le type du produit (Promo, Populaire, Nouveauté)
    type_produit = forms.ChoiceField(
        label='Type de produit',
        choices=Produit.TYPE_PRODUIT_CHOICES,
        required=False,  # Optionnel
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Produit
        fields = [
            'nom', 'description', 'prix', 'ancien_prix', 'quantite_stock', 'reference', 
            'marque', 'poids', 'dimensions', 'etat', 'mise_en_avant', 'video_promotionnelle', 
            'tags', 'image', 'type_produit'
        ]

    def __init__(self, *args, **kwargs):
        self.utilisateur = kwargs.pop('utilisateur', None)  # Utilisateur connecté passé dans les arguments
        super().__init__(*args, **kwargs)

    def clean_prix(self):
        prix = self.cleaned_data.get('prix')
        if prix:
            prix_str = str(prix)
            if '.' in prix_str:
                before_decimal, after_decimal = prix_str.split('.')
            else:
                before_decimal = prix_str
                after_decimal = ''
            
            # Vérifier si la partie avant la virgule a plus de 10 chiffres
            if len(before_decimal) > 10:
                raise ValidationError("Le prix ne peut pas avoir plus de 10 chiffres avant la virgule.")
        return prix

    def clean_quantite_stock(self):
        quantite_stock = self.cleaned_data.get('quantite_stock')
        if quantite_stock is not None and quantite_stock <= 0:
            raise ValidationError("La quantité en stock doit être supérieure à zéro.")
        # Vérifier si la quantité a plus de 5 chiffres
        if quantite_stock and len(str(quantite_stock)) > 5:
            raise ValidationError("La quantité en stock ne peut pas avoir plus de 5 chiffres.")
        return quantite_stock

    def clean(self):
        cleaned_data = super().clean()
        poids = cleaned_data.get('poids')
        dimensions = cleaned_data.get('dimensions')

        if poids and poids <= 0:
            self.add_error('poids', 'Le poids doit être supérieur à zéro.')

        if dimensions:
            if not all(dim.isdigit() for dim in dimensions.replace('x', '').split()):
                self.add_error('dimensions', 'Le format des dimensions doit être sous la forme "LxHxP", avec des chiffres uniquement.')

        return cleaned_data

    def save(self, commit=True):
        produit = super().save(commit=False)
        if self.utilisateur:
            produit.utilisateur = self.utilisateur  # Associer l'utilisateur au produit
        if commit:
            produit.save()

        return produit



class ProduitEditForm(forms.ModelForm):
    # Champs avec des choix prédéfinis
    etat = forms.ChoiceField(
        label='État',
        choices=Produit.ETAT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    mise_en_avant = forms.ChoiceField(
        label='Mettre en avant',
        choices=Produit.MISE_EN_AVANT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    type_produit = forms.ChoiceField(
        label='Type de produit',
        choices=Produit.TYPE_PRODUIT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Champ image avec prévisualisation
    image = forms.ImageField(
        required=False,
        label='Image principale',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'onchange': 'previewImage(this)'
        })
    )

    # Champs texte
    nom = forms.CharField(
        label='Nom du produit', 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom du produit'
        })
    )
    
    description = forms.CharField(
        label='Description', 
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 3,
            'placeholder': 'Description détaillée du produit'
        })
    )

    # Champs numériques
    prix = forms.DecimalField(
        label='Prix', 
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        })
    )
    
    ancien_prix = forms.DecimalField(
        label='Ancien Prix (promo)', 
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        })
    )
    
    quantite_stock = forms.IntegerField(
        label='Quantité en stock', 
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0'
        })
    )
    
    poids = forms.DecimalField(
        label='Poids (kg)', 
        required=False, 
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.001',
            'min': '0'
        })
    )

    # Autres champs
    reference = forms.CharField(
        label='Référence', 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Référence unique'
        })
    )
    
    marque = forms.CharField(
        label='Marque', 
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Marque du produit'
        })
    )
    
    dimensions = forms.CharField(
        label='Dimensions (LxHxP en cm)', 
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 20x15x10'
        })
    )
    
    video_promotionnelle = forms.URLField(
        label='Vidéo promotionnelle (URL)', 
        required=False, 
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://example.com/video'
        })
    )

    # Champ ManyToMany avec style amélioré
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        required=False,
        label='Tags associés'
    )

    class Meta:
        model = Produit
        fields = [
            'nom', 'description', 'prix', 'ancien_prix', 'quantite_stock', 
            'reference', 'marque', 'poids', 'dimensions', 'etat', 
            'mise_en_avant', 'video_promotionnelle', 'tags', 'image', 
            'type_produit'
        ]
        help_texts = {
            'ancien_prix': 'Remplir uniquement si le produit est en promotion',
            'type_produit': 'Catégorie spéciale du produit',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des initial values si nécessaire
        if self.instance.pk:
            self.fields['image'].initial = self.instance.image
            self.fields['tags'].initial = self.instance.tags.all()

    def clean_prix(self):
        prix = self.cleaned_data.get('prix')
        if prix is not None:
            if prix <= 0:
                raise ValidationError("Le prix doit être supérieur à zéro.")
            if len(str(prix).split('.')[0]) > 10:
                raise ValidationError("Le prix ne peut pas dépasser 10 chiffres avant la virgule.")
        return prix

    def clean_ancien_prix(self):
        ancien_prix = self.cleaned_data.get('ancien_prix')
        prix = self.cleaned_data.get('prix')
        
        if ancien_prix and prix:
            if ancien_prix <= prix:
                raise ValidationError("L'ancien prix doit être supérieur au prix actuel pour une promotion.")
        return ancien_prix

    def clean_dimensions(self):
        dimensions = self.cleaned_data.get('dimensions')
        if dimensions:
            parts = dimensions.split('x')
            if len(parts) != 3 or not all(part.strip().isdigit() for part in parts):
                raise ValidationError('Format invalide. Utilisez "LxHxP" avec des nombres (ex: 20x15x10).')
        return dimensions

    def clean(self):
        cleaned_data = super().clean()
        # Validation croisée supplémentaire si nécessaire
        return cleaned_data

    def save(self, commit=True):
        produit = super().save(commit=False)
        if commit:
            produit.save()
            self.save_m2m()  # Important pour les relations ManyToMany comme les tags
        return produit

     #---------------------------Autres images du Produit ----------------------------

class ProduitImageForm(forms.ModelForm):
    class Meta:
        model = ProduitImage
        fields = ['image']  # On ne permet de remplir que l'image

    def __init__(self, *args, **kwargs):
        # On récupère l'utilisateur et le produit depuis les kwargs
        self.utilisateur = kwargs.pop('utilisateur', None)
        self.produit = kwargs.pop('produit', None)
        super(ProduitImageForm, self).__init__(*args, **kwargs)

        # Si l'utilisateur et le produit sont fournis, les associer à l'instance
        if self.utilisateur:
            self.instance.utilisateur = self.utilisateur
        if self.produit:
            self.instance.produit = self.produit

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Validation personnalisée pour la taille de l'image
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('La taille de l\'image ne doit pas dépasser 5 Mo.')
        return image

    def clean(self):
        cleaned_data = super().clean()
        produit = cleaned_data.get('produit')

        # Validation pour vérifier le nombre d'images
        if produit and produit.images.count() > 4:
            raise forms.ValidationError('Un produit ne peut pas avoir plus de 4 images.')
        
        return cleaned_data


    #---------------------------Variantes du Produit ----------------------------
class VarianteForm(forms.ModelForm):
    # Champ pour la taille de la variante (ex : S, M, L)
    taille = forms.CharField(
        required=False,
        max_length=20,
        label='Taille',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # Champ pour la couleur de la variante
    couleur = forms.ChoiceField(
        required=False,
        choices=COULEURS,  # Liste des couleurs définies dans le modèle
        label='Couleur',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Champ pour l'image de la variante
    image = forms.ImageField(
        required=True,
        label='Image de la variante',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    # Champ pour le prix spécifique à la variante
    prix = forms.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=2,
        label='Prix',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    # Champ pour la quantité en stock
    quantite_stock = forms.IntegerField(
        required=True,
        min_value=0,
        label='Quantité en stock',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    # Champ pour la référence spécifique à la variante
    reference = forms.CharField(
        required=False,
        max_length=100,
        label='Référence',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Variante
        fields = ['taille', 'couleur', 'image', 'prix', 'quantite_stock', 'reference']

    def __init__(self, *args, **kwargs):
        self.produit = kwargs.pop('produit', None)  # Passer le produit dans les arguments
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        reference = cleaned_data.get('reference')

        # Validation pour garantir l'unicité de la référence de la variante
        if reference and Variante.objects.filter(reference=reference).exists():
            self.add_error('reference', _('Cette référence est déjà utilisée pour une autre variante.'))

        return cleaned_data

    def save(self, commit=True):
        variante = super().save(commit=False)

        # Lier la variante au produit
        if self.produit:
            variante.produit = self.produit

        if commit:
            variante.save()

        return variante
#---------------------------------Gestion des Sliders------------------------------------

class SliderImageForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = SliderImage
        fields = ['image', 'title', 'description']  # Champs à afficher dans le formulaire

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Associer l'utilisateur connecté
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        slider_image = super().save(commit=False)
        if self.user:
            slider_image.utilisateur = self.user  # Associer l'image du slider à l'utilisateur connecté
        if commit:
            slider_image.save()  # Sauvegarder l'image
        return slider_image
    
#---------------------------------Gestion de la Localisation------------------------------------: 

class LocalisationForm(forms.ModelForm):
    # Validation regex pour le lien Google Maps
    lien_maps = forms.CharField(
        validators=[RegexValidator(
            regex=r'^<iframe src="https://www\.google\.com/maps/embed\?pb=.*" width="\d+" height="\d+" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>$',
            message="Le lien doit être un iframe Google Maps valide"
        )],
        widget=forms.Textarea(attrs={
            'placeholder': 'Collez ici votre iframe Google Maps',
            'class': 'form-control'
        }),
        label="Lien Maps"
    )

    # Ajout du champ 'repere'
    repere = forms.CharField(
        max_length=255, 
        required=False, 
        widget=forms.TextInput(attrs={
            'placeholder': 'Ajouter un repère (facultatif)',
            'class': 'form-control'
        }),
        label="Repère"
    )

    # Génération des choix d'heures toutes les 15 minutes
    HEURE_CHOICES = [(time(h, m).strftime('%H:%M'), time(h, m).strftime('%H:%M')) 
                    for h in range(24) for m in (0, 15, 30, 45)]

    # Champs pour les horaires avec widgets améliorés
    heure_ouverture = forms.ChoiceField(
        choices=HEURE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select time-select',
            'data-toggle': 'select2'
        }),
        label="Heure d'ouverture"
    )
    heure_fermeture = forms.ChoiceField(
        choices=HEURE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select time-select',
            'data-toggle': 'select2'
        }),
        label="Heure de fermeture"
    )
    ouvert_24h = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'ouvert_24h_checkbox',
            'onchange': 'toggleHeureFields()'
        }),
        label="Ouvert 24h/24"
    )
    ferme_jour_ferie = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Fermé les jours fériés",
        initial=True
    )

    class Meta:
        model = Localisation
        fields = ['lien_maps', 'ville', 'quartier', 'repere', 
                 'jour_ouverture', 'jour_fermeture', 
                 'heure_ouverture', 'heure_fermeture', 
                 'ouvert_24h', 'ferme_jour_ferie']
        widgets = {
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'quartier': forms.TextInput(attrs={'class': 'form-control'}),
            'jour_ouverture': forms.Select(attrs={'class': 'form-select'}),
            'jour_fermeture': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if hasattr(self.Meta.model, 'JOURS_SEMAINE'):
            self.fields['jour_ouverture'].choices = self.Meta.model.JOURS_SEMAINE
            self.fields['jour_fermeture'].choices = self.Meta.model.JOURS_SEMAINE
        
        # Initialisation des champs heure si ouvert 24h/24
        if self.instance and self.instance.ouvert_24h:
            self.fields['heure_ouverture'].required = False
            self.fields['heure_fermeture'].required = False
            self.fields['heure_ouverture'].widget.attrs['disabled'] = True
            self.fields['heure_fermeture'].widget.attrs['disabled'] = True

        # Si instance existe, formater les heures au format HH:MM
        if self.instance and self.instance.heure_ouverture:
            self.initial['heure_ouverture'] = self.instance.heure_ouverture.strftime('%H:%M')
        if self.instance and self.instance.heure_fermeture:
            self.initial['heure_fermeture'] = self.instance.heure_fermeture.strftime('%H:%M')

    def clean(self):
        cleaned_data = super().clean()
        
        # Ne pas valider l'unicité si c'est une mise à jour (user n'est pas défini)
        if hasattr(self, 'user') and self.user and Localisation.objects.filter(utilisateur=self.user).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise ValidationError("Vous avez déjà une localisation enregistrée.")
        
        ouvert_24h = cleaned_data.get('ouvert_24h', False)
        heure_ouverture = cleaned_data.get('heure_ouverture')
        heure_fermeture = cleaned_data.get('heure_fermeture')
        
        if not ouvert_24h:
            if not heure_ouverture or not heure_fermeture:
                raise ValidationError("Les heures sont requises si non ouvert 24h/24.")
            
            # Convertir les chaînes HH:MM en objets time pour comparaison
            try:
                h_ouv = datetime.strptime(heure_ouverture, '%H:%M').time()
                h_fer = datetime.strptime(heure_fermeture, '%H:%M').time()
                if h_ouv >= h_fer:
                    raise ValidationError("L'heure de fermeture doit être après l'heure d'ouverture.")
            except ValueError:
                raise ValidationError("Format d'heure invalide. Utilisez HH:MM.")
        else:
            # Nettoyer les heures si ouvert 24h/24
            cleaned_data['heure_ouverture'] = None
            cleaned_data['heure_fermeture'] = None

        return cleaned_data

    def save(self, commit=True):
        localisation = super().save(commit=False)
        if hasattr(self, 'user') and self.user:
            localisation.utilisateur = self.user
        
        # Gestion cohérente des heures pour 24h/24
        if localisation.ouvert_24h:
            localisation.heure_ouverture = None
            localisation.heure_fermeture = None
        else:
            # Convertir les chaînes HH:MM en objets time
            if self.cleaned_data.get('heure_ouverture'):
                localisation.heure_ouverture = datetime.strptime(
                    self.cleaned_data['heure_ouverture'], '%H:%M'
                ).time()
            if self.cleaned_data.get('heure_fermeture'):
                localisation.heure_fermeture = datetime.strptime(
                    self.cleaned_data['heure_fermeture'], '%H:%M'
                ).time()
            
        if commit:
            localisation.save()
        return localisation
class MiseAJourLocalisationForm(LocalisationForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Supprimer le validateur d'unicité pour le lien maps
        self.fields['lien_maps'].validators = []

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
    
    #---------------------------------Gestion de la Localisation------------------------------------
class LocalImagesForm(forms.ModelForm):
    """
    Formulaire pour la gestion des images de localisation.
    """

    class Meta:
        model = LocalImages
        fields = ['image']  # Seul champ à traiter : l'image

    def __init__(self, *args, **kwargs):
        """
        Initialisation du formulaire. On peut éventuellement ajouter des paramètres personnalisés ici.
        """
        super().__init__(*args, **kwargs)

    def clean_image(self):
        """
        Validation de l'image, pour s'assurer qu'elle est bien au format attendu.
        """
        image = self.cleaned_data.get('image')
        if image:
            # On peut ajouter des validations supplémentaires, par exemple vérifier le type ou la taille de l'image
            # Exemple : accepter uniquement des images de type PNG, JPEG, etc.
            if image.content_type not in ['image/jpeg', 'image/png', 'image/gif']:
                raise forms.ValidationError("Seules les images JPEG, PNG ou GIF sont autorisées.")
        return image
#---------------------------------Gestion de la Devise------------------------------------
class DeviseUpdateForm(forms.ModelForm):
    class Meta:
        model = Devise
        fields = ['devise']  # On ne permet de mettre à jour que la devise

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Récupérer 'user' et le retirer des kwargs
        super(DeviseUpdateForm, self).__init__(*args, **kwargs)
        
        # Limiter les devises à celles associées à l'utilisateur connecté (par défaut GNF)
        if user:
            self.instance.utilisateur = user
        
    def save(self, commit=True):
        # Récupérer l'ancienne valeur de la devise avant la mise à jour
        old_devise = self.instance.devise

        # Mettre à jour l'instance avec la nouvelle devise
        devise_instance = super(DeviseUpdateForm, self).save(commit=False)
        devise_instance.utilisateur = self.instance.utilisateur  # L'utilisateur connecté

        if commit:
            devise_instance.save()

        # Retourner l'ancienne devise après la mise à jour
        return old_devise
 
#-------------------------------Gestion Publier le site --------------------------------------------

class BoutiqueUpdateForm(forms.ModelForm):
    titre = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Donnez un titre accrocheur à votre boutique...',
            'class': 'form-control title-input',
        }),
        required=False,
        label="Titre de votre boutique",
        help_text="Ex: 'Ma belle boutique de mode' ou 'Les délices de chez nous'"
    )
    publier = forms.BooleanField(
        required=False,
        label="Publier"
    )
    logo = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False,
        label="Couverture boutique"
    )
    statut_publication = forms.ChoiceField(
        choices=[('chargé', 'Chargé'), ('publié', 'Publié')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label="Statut de publication"
    )

    class Meta:
        model = Boutique
        fields = ['titre', 'publier', 'logo', 'statut_publication']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Associer l'utilisateur connecté
        super().__init__(*args, **kwargs)

        # Pré-remplir les champs avec les valeurs existantes si le statut est "chargé"
        if self.instance and self.instance.statut_publication == "chargé":
            self.fields['titre'].initial = self.instance.titre

    def clean(self):
        cleaned_data = super().clean()

        statut_publication = cleaned_data.get('statut_publication')
        titre = cleaned_data.get('titre', '').strip()
        logo = cleaned_data.get('logo')

        if statut_publication == "publié":
            # Les champs titre et logo doivent être obligatoires si "publié"
            if not titre:
                self.add_error('titre', 'Un titre attrayant est requis pour publier la boutique.')
            if not logo:
                self.add_error('Couverture boutique', 'La Couverture boutique est requis pour publier la boutique.')
        elif statut_publication == "chargé":
            # Utiliser les anciennes valeurs si elles ne sont pas fournies
            if not titre:
                cleaned_data['titre'] = self.instance.titre
            if not logo:
                cleaned_data['logo'] = self.instance.logo

        return cleaned_data

    def save(self, commit=True):
        boutique = super().save(commit=False)

        if self.user:
            boutique.utilisateur = self.user  # Associer la boutique à l'utilisateur connecté

        statut_publication = self.cleaned_data.get('statut_publication')

        if statut_publication == "publié":
            boutique.publier = True
        elif statut_publication == "chargé":
            boutique.publier = False

        if commit:
            boutique.save()  # Sauvegarder les modifications
        return boutique



