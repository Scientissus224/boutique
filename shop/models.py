from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser
from django.db import models
import uuid
from django.db.models import Sum
from decimal import Decimal, InvalidOperation
from datetime import timedelta
from django.utils.timezone import now
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from .const_models import (
    TEXT_COLOR_NAV,
    TEXT_COLOR_NAV_CUSOR,
    COULEURS,
    TYPE_BOUTIQUE_CHOICES,
    SOURCE_DECOUVERTE_CHOICES,
    PRODUITS_VENDUS_CHOICES
)
# -----------------------
# Gestionnaire d'utilisateurs personnalisé
# -----------------------
class UtilisateurManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Crée et retourne un utilisateur avec un email et un mot de passe.
        """
        if not email:
            raise ValueError('L\'utilisateur doit avoir un email')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Crée et retourne un superutilisateur avec un email et un mot de passe.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


# -----------------------
# Modèle utilisateur personnalisé
# -----------------------
STATUT_CHOICES = [
        ('attente', 'Attente'),
        ('valider', 'Valider'),
        ('invalider', 'Invalider'),
    ]
class Utilisateur(AbstractUser):
    identifiant_unique = models.CharField(max_length=100, unique=True, default='warabaguinee224')  # Valeur par défaut ajoutée
    nom_complet = models.CharField(max_length=200)
    numero = models.CharField(max_length=15, unique=True)
    nom_boutique = models.CharField(max_length=200, unique=True)
    email = models.EmailField(unique=True)
    statut_validation_compte = models.CharField(
        max_length=10,
        choices=STATUT_CHOICES,
        default='attente',  # Valeur par défaut 'attente'
    )
    
    # Champ produits_vendus ajouté
    produits_vendus = models.CharField(
        max_length=225,  # Limite de 225 caractères
        default=None,  # Valeur par défaut de None
        blank=True  # Le champ peut être laissé vide
    )

    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='utilisateur_set', 
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='utilisateur_permissions', 
        blank=True
    )

    objects = UtilisateurManager()

    def __str__(self):
        return f"{self.nom_complet} - {self.nom_boutique}"

    # Utilisation de l'email comme identifiant
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom_complet', 'nom_boutique']  # Champs requis pour les superutilisateurs
    
class UtilisateurTemporaire(models.Model):
    identifiant_unique= models.CharField(max_length=100, unique=True, default='identifiant_par_defaut')
    email = models.EmailField(unique=True)
    nom_complet = models.CharField(max_length=200, db_index=True)
    numero = models.CharField(max_length=15)
    nom_boutique = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    token = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.nom_complet} {self.nom_boutique}'

    
class InformationsSupplementaires(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE)
    type_boutique = models.CharField(max_length=50, choices=TYPE_BOUTIQUE_CHOICES)
    # Ajout d'une valeur par défaut pour le champ produits_vendus
    produits_vendus = models.CharField(
        max_length=241, 
        choices=PRODUITS_VENDUS_CHOICES, 
        default='vetements'  # Remplace 'vetements' par une valeur par défaut de ton choix
    )
    source_decouverte = models.CharField(max_length=100, choices=SOURCE_DECOUVERTE_CHOICES)

    def __str__(self):
        return f"Informations pour {self.utilisateur.nom_boutique}"


class InformationsSupplementairesTemporaire(models.Model):
    utilisateur_temporaire = models.OneToOneField(UtilisateurTemporaire, on_delete=models.CASCADE)
    type_boutique = models.CharField(max_length=50, choices=TYPE_BOUTIQUE_CHOICES)
    # Ajout d'une valeur par défaut pour le champ produits_vendus
    produits_vendus = models.CharField(
        max_length=241, 
        choices=PRODUITS_VENDUS_CHOICES, 
        default='vetements'  # Remplace 'vetements' par une valeur par défaut de ton choix
    )
    source_decouverte = models.CharField(max_length=100, choices=SOURCE_DECOUVERTE_CHOICES)

    def __str__(self):
        return f"Informations pour {self.utilisateur_temporaire.nom_boutique}"
    


class ClientManager(BaseUserManager):
    def create_client(self, email, nom_complet, telephone, adresse, password=None):
        """
        Crée et enregistre un client avec un email, un nom complet, un téléphone,
        une adresse et un mot de passe.
        """
        if not email:
            raise ValueError('L\'email est obligatoire')
        email = self.normalize_email(email)
        
        # Création du client
        client = self.model(
            email=email, 
            nom_complet=nom_complet, 
            telephone=telephone, 
            adresse=adresse
        )
        
        # Assigner le mot de passe
        client.set_password(password)
        client.save(using=self._db)
        return client


class Client(AbstractUser):
    """
    Modèle d'un client avec des informations personnalisées.
    Utilisation de l'email commeidentifiant_uniqueprincipal.
    """

    nom_complet = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    adresse = models.CharField(max_length=255)
    telephone = models.CharField(max_length=15, unique=True)

    # Ajout du champ username pour permettre la création de l'utilisateur
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)

    # Gestionnaire personnalisé
    objects = ClientManager()

    # Attributs nécessaires pour l'authentification
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom_complet', 'telephone']

    def save(self, *args, **kwargs):
        if not self.username:
            # Si le champ username est vide, on utilise l'email comme username
            self.username = self.email.split('@')[0]  # Par exemple, utiliser la première partie de l'email
        super(Client, self).save(*args, **kwargs)

    def __str__(self):
        return self.nom_complet

    # Relations personnalisées pour les groupes et permissions
    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='client_groups',  # Relation inverse personnalisée pour les groupes
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='client_permissions',  # Relation inverse personnalisée pour les permissions
        blank=True
    )
                       # -----------------------Modèle Produit-----------------------
 
# Définir les choix pour l'état du produit
NEUF = 'neuf'
OCCASION = 'occasion'
RECONDITIONNE = 'reconditionne'

ETAT_CHOICES = [
    (NEUF, 'Neuf'),
    (OCCASION, 'Occasion'),
    (RECONDITIONNE, 'Reconditionné'),
]


class Produit(models.Model):
    # Définir les choix pour l'état du produit
    NEUF = 'Neuf'
    OCCASION = 'Occasion'
    RECONDITIONNE = 'Reconditionné'
    
    ETAT_CHOICES = [
        (NEUF, 'Neuf'),
        (OCCASION, 'Occasion'),
        (RECONDITIONNE, 'Reconditionné'),
    ]

    OUI = 'Oui'
    NON = 'Non'
    
    MISE_EN_AVANT_CHOICES = [
        (OUI, 'Oui'),
        (NON, 'Non'),
    ]

    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="produits")
    nom = models.CharField(max_length=200)  # Nom du produit
    description = models.TextField()  # Description détaillée
    image = models.ImageField(upload_to='produits/', null=True, blank=True)  # Image principale
    prix = models.DecimalField(max_digits=10, decimal_places=2)  # Prix du produit
    disponible = models.BooleanField(default=True)  # Statut de disponibilité du produit
    panier = models.BooleanField(default=False)  # Champ pour savoir si le produit est dans le panier
    quantite_stock = models.PositiveIntegerField(default=0)  # Quantité en stock
    reference = models.CharField(max_length=100, null=True, blank=True)  # Référence du produit (optionnel)
    marque = models.CharField(max_length=100, null=True, blank=True)  # Marque du produit
    date_ajout = models.DateTimeField(auto_now_add=True, null=True)  # Date d'ajout du produit
    poids = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Poids du produit
    dimensions = models.CharField(max_length=200, null=True, blank=True)  # Dimensions du produit
    etat = models.CharField(max_length=50, choices=ETAT_CHOICES, default=NEUF)  # État du produit
    video_promotionnelle = models.URLField(null=True, blank=True)  # URL de vidéo promotionnelle
    tags = models.ManyToManyField('Tag', related_name="produits", blank=True)  # Tags associés
    mise_en_avant = models.CharField(max_length=3, choices=MISE_EN_AVANT_CHOICES, default=NON)  # Produit mis en avant ou non

    def clean(self):
        """Validation des dimensions et du poids."""
        if self.poids and self.poids <= 0:
            raise ValidationError(_('Le poids doit être supérieur à zéro.'))
        
        if self.dimensions:
            # Validation du format des dimensions (LxHxP)
            parts = self.dimensions.split('x')
            if len(parts) != 3 or not all(part.strip().isdigit() for part in parts):
                raise ValidationError(_('Le format des dimensions doit être sous la forme "LxHxP", avec des chiffres uniquement.'))

    def get_absolute_url(self):
        return reverse('detail_produits', kwargs={'produit_id': self.pk})
    
    def get_produit_url(self):
        return reverse('afficher_produit', kwargs={'produit_id': self.pk, 'utilisateur_id': self.utilisateur.pk})

    def produit_panier_id(self):
        return reverse('ajouter_au_panier', kwargs={'produit_id': self.pk})

    def produit_retire_panier_id(self):
        return reverse('retirer_au_panier', kwargs={'produit_id': self.pk})

    def ajuster_prix_dynamiquement(self):
        """ Ajuste le prix en fonction du stock et de la demande """
        ventes_recents = self.ventes.filter(date_vente__gte=now() - timedelta(days=30)).aggregate(total_vendu=Sum('quantite_vendue'))['total_vendu'] or 0
        if ventes_recents > 50:
            self.prix = self.prix * 1.1  # Augmenter le prix si la demande est élevée
        elif ventes_recents < 10:
            self.prix = self.prix * 0.9  # Réduire le prix si la demande est faible
        self.save()

    def mise_en_avant_auto(self):
        """ Met en avant les produits qui se vendent bien ou sont en faible stock """
        if self.quantite_stock <= 5:  # Si le stock est faible
            self.mise_en_avant = self.OUI
            self.save()
        elif self.ventes.filter(date_vente__gte=now() - timedelta(days=30)).aggregate(total_vendu=Sum('quantite_vendue'))['total_vendu'] > 30:
            self.mise_en_avant = self.OUI
            self.save()
    
    def update_stock(self):
        """ Mise à jour du stock basé sur les ventes """
        ventes_recentes = self.ventes.filter(date_vente__gte=now() - timedelta(days=30)).aggregate(total_vendu=Sum('quantite_vendue'))['total_vendu'] or 0
        if ventes_recentes > self.quantite_stock * 0.8:
            self.mise_en_avant_auto()  # Mettre en avant le produit si les ventes sont élevées

    def __str__(self):
        return f'{self.nom} - {self.marque if self.marque else "Marque inconnue"}'

    class Meta:
        ordering = ['-date_ajout']



class Vente(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="ventes")
    produit = models.ForeignKey(Produit, on_delete=models.SET_NULL, null=True, blank=True, related_name="ventes")
    nom_produit = models.CharField(max_length=200)  # Sauvegarde du nom du produit
    image_produit = models.ImageField(upload_to='ventes/', null=True, blank=True)  # Image du produit vendu
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Prix d'achat
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Prix de vente
    statut = models.BooleanField(default=False) 
    quantite_vendue = models.PositiveIntegerField(default=0)  # Quantité vendue
    date_vente = models.DateTimeField(auto_now_add=True)  # Date de la vente

    @classmethod
    def top_produits(cls, utilisateur, limite=5):
        """Retourne les 5 produits les plus vendus avec leurs images, en regroupant les produits répétés"""
        
        # Regrouper les produits par leur nom, prix, et image, et calculer la somme des quantités vendues
        ventes = (
            cls.objects.filter(utilisateur=utilisateur)
            .values('nom_produit', 'image_produit', 'produit__prix')  # Regroupement par nom, prix et image du produit
            .annotate(total_vendu=Sum('quantite_vendue'))  # Somme des quantités vendues
            .order_by('-total_vendu')[:limite]  # Trier par quantité vendue
        )
        
        # Ajouter l'URL de l'image pour chaque produit
        for vente in ventes:
            # On recherche l'image du produit à partir de son nom et de son prix
            produit = Produit.objects.filter(nom=vente['nom_produit'], prix=vente['produit__prix']).first()
            if produit:
                vente['image_url'] = produit.image.url if produit.image else None
        
        return ventes

    @classmethod
    def produits_a_recommander(cls, utilisateur, limite=5):
        """ Retourne les produits qui se vendent bien mais qui pourraient bientôt manquer de stock avec leur image """
        produits_rapides = (
            cls.objects.filter(utilisateur=utilisateur)
            .values('produit', 'nom_produit', 'image_produit')
            .annotate(total_vendu=Sum('quantite_vendue'))
            .order_by('-total_vendu')[:limite]
        )

        recommandations = []
        for produit in produits_rapides:
            p = Produit.objects.filter(id=produit['produit']).first()
            if p and p.quantite_stock <= 5:  # Seuil critique pour réapprovisionnement
                produit['image_url'] = p.image.url if p.image else None
                recommandations.append(produit)
        
        return recommandations

    def update_stock(self):
        """ Mise à jour du stock du produit après chaque vente """
        if self.produit and isinstance(self.produit.quantite_stock, int) and self.produit.quantite_stock >= self.quantite_vendue:
            self.produit.quantite_stock -= self.quantite_vendue

            # Si le stock est épuisé, on met disponible à False
            if self.produit.quantite_stock == 0:
                self.produit.disponible = False

            self.produit.save()
        else:
            raise ValueError("Le stock est insuffisant pour cette vente.")


    def save(self, *args, **kwargs):
        """ Enregistrer la vente et mettre à jour le stock """
        try:
            if self.prix_achat is not None:
                self.prix_achat = Decimal(str(self.prix_achat).strip()) if isinstance(self.prix_achat, (int, float, str)) else self.prix_achat
            if self.prix_vente is not None:
                self.prix_vente = Decimal(str(self.prix_vente).strip()) if isinstance(self.prix_vente, (int, float, str)) else self.prix_vente
        except InvalidOperation:
            raise ValueError("Les prix doivent être des nombres valides (entiers ou décimaux).")
        
        self.quantite_vendue = int(self.quantite_vendue)

        if self.produit and isinstance(self.produit.quantite_stock, int) and self.produit.quantite_stock < self.quantite_vendue:
            raise ValueError("Stock insuffisant pour cette vente.")

        super().save(*args, **kwargs)
        self.update_stock()

    def __str__(self):
        return f'Vente de {self.nom_produit} ({self.quantite_vendue}x) par {self.utilisateur}'

    class Meta:
        ordering = ['-date_vente']
        verbose_name = "Vente"
        verbose_name_plural = "Ventes"



class ProduitImage(models.Model):
    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    produit = models.ForeignKey(Produit, related_name='images', on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(Utilisateur, related_name='produit_images', on_delete=models.CASCADE, default=None)
    image = models.ImageField(upload_to='details/')
    date_ajout = models.DateTimeField(default=timezone.now)

    def clean(self):
        """
        Validation personnalisée pour limiter le nombre d'images par produit
        et vérifier les propriétés des fichiers téléchargés.
        """
        if not self.produit:
            raise ValidationError(_('Chaque image doit être associée à un produit.'))

        # Vérification du nombre d'images pour le produit
        if self.produit.images.count() > 4:
            raise ValidationError(_('Un produit ne peut pas avoir plus de 4 images.'))

        if self.image:
            # Vérification de la taille maximale de l'image (5 Mo)
            if self.image.size > 5 * 1024 * 1024:  # Taille maximale de 5 Mo
                raise ValidationError(_('La taille de l\'image ne doit pas dépasser 5 Mo.'))

    def save(self, *args, **kwargs):
        self.full_clean()  # Appelle clean() pour effectuer les validations
        super().save(*args, **kwargs)  # Appel de save() de la classe parente pour sauvegarder l'image

class Variante(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name="variantes")
    taille = models.CharField(max_length=20, null=True, blank=True)  # Taille de la variante (ex : S, M, L)
    panier = models.BooleanField(default=False)
    
    couleur = models.CharField(
        max_length=7,  # Longueur du code hexadécimal (#RRGGBB)
        choices=COULEURS,  # Limite les choix à ces couleurs
        null=True,
        blank=True,
        default='',  # Valeur par défaut : aucune couleur
    )  # Couleur de la variante (en hexadécimal)
    
    
    image = models.ImageField(upload_to='variante/', null=True, blank=True)  # Image principale
    prix = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Prix spécifique à la variante
    quantite_stock = models.PositiveIntegerField(default=0,null=True,blank=True)  # Quantité disponible pour cette variante
    reference = models.CharField(max_length=100, blank=True, null=True)  # Référence spécifique à la variante

    def __str__(self):
        return f"{self.produit.nom} - {self.taille or ''} - {self.couleur or ''}"
    def variante_panier_id(self):
        return reverse('ajouter_au_panier_variante', kwargs={'variante_id': self.pk})
    def variante_retirer_panier_id(self):
        return reverse('retirer_au_panier_variante', kwargs={'variante_id': self.pk})

# Gestion des tags
class Tag(models.Model):
    nom = models.CharField(max_length=50, unique=True)  # Nom du tag (ex : "promo", "nouveauté")
    
    def __str__(self):
        return self.nom



                  # -----------------------Modèle De devise -----------------------


class Devise(models.Model):
    # Liste des devises avec les symboles uniquement
    DEVICES_CHOICES = [
        ('GNF', 'GNF'),
        ('FCFA', 'FCFA'),
        ('$', 'USD'),
        ('€', 'EUR'),
        ('₦', 'NGN'),
        ('Esc', 'CVE'),
        ('FCE', 'FCE'),
        ('L$', 'LCF'),
        # Ajoutez d'autres devises avec leurs symboles si nécessaire
    ]

    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="devise")
    devise = models.CharField(max_length=10, choices=DEVICES_CHOICES, default='GNF')

    def __str__(self):
        return self.devise  # Renvoie uniquement la devise, pas un tuple

# -----------------------
# Modèle pour les sliders
# -----------------------
class SliderImage(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="slider_images")
    image = models.ImageField(upload_to='sliders/')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


# -----------------------
# Modèle Localisation du site
# -----------------------
class Localisation(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="localisations")
    lien_maps = models.CharField(max_length=1000)  # Lien vers la localisation Google Maps
    ville = models.CharField(max_length=100, null=True, blank=True)
    quartier = models.CharField(max_length=100, null=True, blank=True)
    repere = models.CharField(max_length=255, null=True, blank=True)  # Champ pour le repère

    class Meta:
        unique_together = ('utilisateur',)

    def __str__(self):
        return f"{self.lien_maps} ({self.ville}, {self.quartier}, Repère: {self.repere})"

# -----------------------
# Modèle  des images de Localisation du site
# -----------------------
class LocalImages(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="images_localisation")
    image = models.ImageField(upload_to='images_localisation/')

    def __str__(self):
        return f"Image de {self.utilisateur.nom_complet} - {self.image.url}"  # Affiche l'utilisateur et l'URL de l'image
# -----------------------
class Commande(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="commandes")
    nom_client = models.CharField(max_length=200)
    numero_client = models.CharField(max_length=15)
    date_commande = models.DateTimeField(auto_now_add=True, db_index=True)
    html_contenu = models.TextField(blank=True)
    STATUT_CHOICES = [
        ('En attente', 'En attente'),
        ('En cours', 'En cours'),
        ('Livrée', 'Livrée'),
        ('Annulée', 'Annulée')
    ]
    statut = models.CharField(
        max_length=50,
        default='En attente',
        choices=STATUT_CHOICES,
    )
    lieu_de_livraison = models.CharField(max_length=255, blank=True, null=True)
    date_enregistrement = models.DateTimeField(auto_now_add=True, null=True)  # Nouveau champ

    def __str__(self):
        return f"Commande {self.pk} - {self.nom_client}"



# -----------------------
# Modèle pour les détails des commandes
# -----------------------
class DetailCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name="details_commande")
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom} (Commande {self.commande.pk})"


# -----------------------

class Commentaire(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="commentaires")
    produit = models.ForeignKey('Produit', on_delete=models.CASCADE, related_name="commentaires", default=1)  # Id produit par défaut
    commentaire = models.TextField()
    image_profil = models.ImageField(upload_to='profil_images/', null=True, blank=True)  # Image de profil
    date_commentaire = models.DateTimeField(auto_now_add=True)
    note = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Note entre 1 et 5 étoiles",
    )

# -----------------------
# Modèle pour recevoir les messages des utilisateurs
# -----------------------
class Message(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="messages")
    nom_utilisateur = models.CharField(max_length=200)
    email_utilisateur = models.EmailField()
    sujet = models.CharField(max_length=200)
    message = models.TextField()
    date_message = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message de {self.nom_utilisateur} - {self.sujet}"
    
#-------------------------------------Gestion des styles du site -------------------------------------
          #1 Gestion des couleurs de fond de la NavBar
class NavbarSettings(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="navbar_settings")
    couleur_fond = models.CharField(
        max_length=200,  # Hexa couleur : #RRGGBB
        choices=[
            ('#FFFFFF', 'Blanc'),
            ('#000000', 'Noir'),
            ('#FF5733', 'Orange'),
            ('#33FF57', 'Vert'),
            ('#3357FF', 'Bleu'),
            ('#FFD700', 'Jaune'),
            ('#800080', 'Violet'),
            ('#FFC0CB', 'Rose'),
            ('#D3D3D3', 'Gris clair'),

            # Mélanges de couleurs
            ('#3498DB', 'Bleu'),
            ('#FF5733', 'Orange vif'),
            ('#1ABC9C', 'Turquoise'),
            ('#E74C3C', 'Rouge'),
            ('#9B59B6', 'Violet'),
            ('#F39C12', 'Jaune'),
            ('#F39C12', 'Jaune'),

            # Couleurs foncées
            ('#333333', 'Gris foncé'),
            ('#212121', 'Noir charbon'),
            ('#1A1A1A', 'Gris ardoise foncé'),
            ('#2C3E50', 'Bleu marine foncé'),
            ('#34495E', 'Gris bleu foncé'),
            ('#555555', 'Gris moyen foncé'),
            ('#7F8C8D', 'Gris ardoise'),
            ('#6A1B9A', 'Violet foncé'),
            ('#9B59B6', 'Violet prune'),
            ('#8E44AD', 'Violet foncé'),
            ('#E74C3C', 'Rouge foncé'),
            ('#C0392B', 'Rouge bordeaux'),
            ('#D35400', 'Orange brûlé'),
            ('#F39C12', 'Jaune foncé'),
            ('#16A085', 'Vert foncé'),
            ('#27AE60', 'Vert forêt foncé'),
            ('#2980B9', 'Bleu foncé'),
            ('#1ABC9C', 'Turquoise foncé'),

            # Dégradés
            ('linear-gradient(to right, #FF7F50, #FF1493)', 'Dégradé Rose-Orangé'),
            ('linear-gradient(to right, #2980B9, #8E44AD)', 'Dégradé Bleu-Violet'),
            ('linear-gradient(to right, #F39C12, #F1C40F)', 'Dégradé Jaune-Or'),

            # Couleurs complémentaires
            ('#27AE60', 'Vert'),
            ('#2C3E50', 'Bleu marine'),
            ('#FFDAB9', 'Pêche'),
            ('#BDC3C7', 'Gris clair'),
        ],
        default='#FFFFFF',  # Valeur par défaut
    )

    def __str__(self):
        return f"Paramètres navbar de {self.utilisateur.username}"



class BoutiqueSettings(models.Model):
    utilisateur = models.ForeignKey('Utilisateur', on_delete=models.CASCADE, related_name="boutique_settings")
    
    # Couleur de l'écriture
    couleur_texte = models.CharField(
        max_length=200,
        choices=TEXT_COLOR_NAV,
        default='#000000'
    )

    def __str__(self):
        return f"Paramètres de la boutique de {self.utilisateur.username}"
    
class BoutiqueNavCusor(models.Model):
    utilisateur = models.ForeignKey('Utilisateur', on_delete=models.CASCADE, related_name="boutique_cusor_nav")
    
    # Couleur de l'écriture
    couleur_texte_cursor = models.CharField(
        max_length=200,
        choices=TEXT_COLOR_NAV_CUSOR,
        default='#000000'
    )

    def __str__(self):
        return f"Paramètres de la boutique de {self.utilisateur.username}"
    
#-------------------------------------------Génération de la boutique----------------------------------




class Boutique(models.Model):
    utilisateur = models.OneToOneField(
        Utilisateur,  # Référence au modèle Utilisateur existant
        on_delete=models.CASCADE,
        related_name="boutique",  # Utilisez un seul nom de relation
    )
    description = models.TextField(blank=True)  # Description de la boutique
    publier = models.BooleanField(default=False)  # Statut de publication (False = chargé)
    html_contenu = models.TextField(blank=True)  # Contenu HTML généré
    logo = models.ImageField(upload_to="logos/", null=True, blank=True)  # Logo de la boutique
    premium = models.BooleanField(default=False)  # Champ premium ajouté, par défaut False
    
    statut_publication = models.CharField(
        max_length=20,
        choices=[("chargé", "Chargé"), ("publié", "Publié")],  # Deux valeurs possibles
        default="chargé",  # Valeur par défaut
    )
    date_publication = models.DateTimeField(null=True, blank=True)  # Date de publication
    produits_vendus = models.CharField(
        max_length=250,  # Limite de 250 caractères
        default="non",  # Valeur par défaut "non"
        blank=True  # Le champ peut être laissé vide si nécessaire
    )

    class Meta:
        db_table = 'shop_boutique'
        managed = True  # Pour laisser Django gérer la création et la mise à jour de la table

    def __str__(self):
        return f"Boutique de {self.utilisateur.nom_complet}"

    def publier_boutique(self):
        """
        Publie la boutique et met à jour la date de publication.
        """
        self.publier = True
        self.statut_publication = "publié"  # Met à jour le statut à "publié"
        self.date_publication = timezone.now()
        self.save()

    def depublier_boutique(self):
        """
        Dépublie la boutique et supprime la date de publication.
        """
        self.publier = False
        self.statut_publication = "chargé"  # Met à jour le statut à "chargé"
        self.date_publication = None  # Enlever la date de publication si la boutique est dépubliée
        self.save()

    @staticmethod
    def get_html_contenu_par_utilisateur(utilisateur_id):
        """
        Récupère le contenu HTML associé à un utilisateur spécifique.
        """
        try:
            boutique = Boutique.objects.get(utilisateur_id=utilisateur_id)
            return boutique.html_contenu
        except Boutique.DoesNotExist:
            return None

#-------------------------------------------Gestion des personnels du support client-----------------------------------


class SupportClientManager(BaseUserManager):
    def create_user(self, email, nom, role, profil, password=None):
        if not email:
            raise ValueError("L'email est requis")
        
        # Création de l'utilisateur sans la vérification de l'email
        user = self.model(
            email=self.normalize_email(email),
            nom=nom,
            role=role,
            profil=profil
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nom, role, profil, password=None):
        user = self.create_user(
            email=email,
            nom=nom,
            role=role,
            profil=profil,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class SupportClient(AbstractBaseUser):
    ROLES = [
        ('responsable_support', 'Responsable Support'),
        ('assistant_support', 'Assistant Support'),
        ('technicien_support', 'Technicien Support'),
    ]

    VALIDATION_COMPTE = [
        ('accordé', 'Accordé'),
        ('non accordé', 'Non accordé'),
    ]

    nom = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=ROLES)
    validation_compte = models.CharField(max_length=20, choices=VALIDATION_COMPTE)
    profil = models.ImageField(upload_to='profiles/', null=True, blank=True)  # Champ image
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = SupportClientManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'role', 'profil']

    def __str__(self):
        return self.nom

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def save(self, *args, **kwargs):
        # Vérification si l'email existe déjà dans la table Utilisateur
        if Utilisateur.objects.filter(email=self.email).exists():
            raise ValidationError(f"L'email {self.email} existe déjà dans la base de données.")
        
        super().save(*args, **kwargs)
