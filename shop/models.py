from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser
from django.db import models
import uuid
from django.db.models import Sum
from decimal import Decimal, InvalidOperation
from datetime import timedelta
import random
import string
from cloudinary.models import CloudinaryField
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils import timezone 
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta, date
from django.urls import reverse
from .const_models import (
    COULEURS,
    TYPE_BOUTIQUE_CHOICES,
    SOURCE_DECOUVERTE_CHOICES,
    PRODUITS_VENDUS_CHOICES
)

# -----------------------
# Gestionnaire d'utilisateurs personnalisé
# -----------------------
class UtilisateurManager(BaseUserManager):
    def create_user(self, identifiant_unique, email, password=None, **extra_fields):
        """
        Crée et retourne un utilisateur avec un identifiant_unique, email et mot de passe.
        """
        if not identifiant_unique:
            raise ValueError('L\'utilisateur doit avoir un identifiant unique')
        if not email:
            raise ValueError('L\'utilisateur doit avoir un email')
        
        email = self.normalize_email(email)
        user = self.model(
            identifiant_unique=identifiant_unique,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, identifiant_unique, email, password=None, **extra_fields):
        """
        Crée et retourne un superutilisateur avec un identifiant_unique, email et mot de passe.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(identifiant_unique, email, password, **extra_fields)


# -----------------------
# Modèle utilisateur personnalisé
# -----------------------
STATUT_CHOICES = [
        ('attente', 'Attente'),
        ('valider', 'Valider'),
        ('invalider', 'Invalider'),
    ]
def default_date_fin_essai():
    return date.today() + timedelta(days=90)

class Utilisateur(AbstractUser):
    identifiant_unique = models.CharField(max_length=100, unique=True)
    nom_complet = models.CharField(max_length=200)
    numero = models.CharField(max_length=15, unique=True)
    nom_boutique = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    
    statut_validation_compte = models.CharField(
        max_length=10,
        choices=STATUT_CHOICES,
        default='attente',
    )

    produits_vendus = models.CharField(
        max_length=225,
        default=None,
        blank=True
    )

    logo_boutique = CloudinaryField(
        'logos_boutiques',
        blank=True,
        null=True
    )

    # Période d'essai : modifiable, mais initialisée à 90 jours
    date_fin_essai = models.DateField(default=default_date_fin_essai)

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

    USERNAME_FIELD = 'identifiant_unique'
    REQUIRED_FIELDS = ['email', 'nom_complet', 'nom_boutique']

    @property
    def jours_restants_essai(self):
        """Retourne le nombre de jours restants jusqu'à la fin d'essai."""
        jours = (self.date_fin_essai - date.today()).days
        return max(jours, 0)

    def verifier_statut_essai(self):
        """Désactive l'utilisateur et sa boutique si la période d’essai est expirée."""

        if self.jours_restants_essai == 0 and self.is_active:
            self.is_active = False
            self.save()

            # Désactiver la boutique associée
            if hasattr(self, 'boutique'):
                self.boutique.depublier_boutique()
            
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

    PROMO = 'Promo'
    Aucun = 'Aucun'
    POPULAIRE = 'Populaire'
    NOUVEAUTE = 'Nouveauté'

    TYPE_PRODUIT_CHOICES = [
        (Aucun , 'Aucun'),
        (PROMO, 'Promo'),
        (POPULAIRE, 'Populaire'),
        (NOUVEAUTE, 'Nouveauté'),
    ]

    # Nouveau champ identifiant unique
    identifiant = models.UUIDField(editable=False, unique=True , null=True, default=uuid.uuid4)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="produits")
    nom = models.CharField(max_length=200)  # Nom du produit
    description = models.TextField()  # Description détaillée
    image =  CloudinaryField('produits', null=True, blank=True)  # Image principale
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

    # Ajout d'un champ pour le type du produit (promo, nouveauté, populaire)
    type_produit = models.CharField(max_length=10, choices=TYPE_PRODUIT_CHOICES, null=True, blank=True)

    # Champs pour la promotion
    ancien_prix = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Si c'est un nouveau produit (pas encore enregistré en base)
        if not self.pk and not self.identifiant:
            self.identifiant = uuid.uuid4()
        super().save(*args, **kwargs)
    
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
        try:
            if not self.utilisateur:
                return '#'
            return reverse('afficher_produit', kwargs={
                'produit_identifiant': self.identifiant,
                'utilisateur_identifiant': self.utilisateur.identifiant_unique
            })
        except Exception as e:
            print(f"[get_produit_url] Erreur pour produit {self.id} : {e}")
            return '#'

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



class VenteAttente(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="ventes_attente")
    produit = models.ForeignKey(Produit, on_delete=models.SET_NULL, null=True, blank=True, related_name="ventes_attente")
    nom_produit = models.CharField(max_length=200)  # Sauvegarde du nom du produit
    image_produit =  CloudinaryField('vent', null=True, blank=True)  # Image du produit vendu
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Prix d'achat
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Prix de vente
    quantite_vendue = models.PositiveIntegerField(default=0)  # Quantité vendue
    date_vente = models.DateTimeField(auto_now_add=True)  # Date de la vente
    vue_par_boutiquier = models.BooleanField(default=False)

    def __str__(self):
        return f"[Attente] Vente de {self.nom_produit} ({self.quantite_vendue}x) par {self.utilisateur}"


class Vente(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="ventes")
    produit = models.ForeignKey(Produit, on_delete=models.SET_NULL, null=True, blank=True, related_name="ventes")
    nom_produit = models.CharField(max_length=200)  # Sauvegarde du nom du produit
    image_produit =  CloudinaryField('ventes', null=True, blank=True)  # Image du produit vendu
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Prix d'achat
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Prix de vente
    statut = models.BooleanField(default=False) 
    quantite_vendue = models.PositiveIntegerField(default=0)  # Quantité vendue
    date_vente = models.DateTimeField(auto_now_add=True)  # Date de la vente


    def update_stock(self):
        """ Mise à jour du stock du produit après chaque vente """
        if self.produit and isinstance(self.produit.quantite_stock, int):
            if self.produit.quantite_stock >= self.quantite_vendue:
                self.produit.quantite_stock -= self.quantite_vendue
                if self.produit.quantite_stock == 0:
                    self.produit.disponible = False
            else:
                # Stock insuffisant : désactivation produit + annulation vente
                self.produit.disponible = False
                self.statut = False  # Marquer la vente comme non valide

            self.produit.save()
        else:
            raise ValueError("Le stock du produit est invalide ou manquant.")

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

    def save(self, *args, **kwargs):
        """ Enregistrer la vente et mettre à jour le stock """

        # 💰 Validation des prix
        try:
            if self.prix_achat is not None:
                self.prix_achat = Decimal(str(self.prix_achat).strip()) if isinstance(self.prix_achat, (int, float, str)) else self.prix_achat
            if self.prix_vente is not None:
                self.prix_vente = Decimal(str(self.prix_vente).strip()) if isinstance(self.prix_vente, (int, float, str)) else self.prix_vente
        except InvalidOperation:
            raise ValueError("Les prix doivent être des nombres valides (entiers ou décimaux).")

        # 📦 Vérification de la quantité vendue
        self.quantite_vendue = int(self.quantite_vendue)

        # 📉 Vérification du stock
        if self.produit and isinstance(self.produit.quantite_stock, int):
            if self.produit.quantite_stock < self.quantite_vendue:
                self.produit.statut = False
                self.produit.save()
                raise ValueError("Stock insuffisant pour cette vente.")

        # 💾 Enregistrement de la vente et mise à jour du stock
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
    image =  CloudinaryField('details')
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
    
    
    image =  CloudinaryField('variante', null=True, blank=True)  # Image principale
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
    image =  CloudinaryField('sliders')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


# -----------------------
# Modèle Localisation du site
# -----------------------
class Localisation(models.Model):
    # Jours de la semaine pour les horaires
    LUNDI = 'Lundi'
    MARDI = 'Mardi'
    MERCREDI = 'Mercredi'
    JEUDI = 'Jeudi'
    VENDREDI = 'Vendredi'
    SAMEDI = 'Samedi'
    DIMANCHE = 'Dimanche'
    
    JOURS_SEMAINE = [
        (LUNDI, 'Lundi'),
        (MARDI, 'Mardi'),
        (MERCREDI, 'Mercredi'),
        (JEUDI, 'Jeudi'),
        (VENDREDI, 'Vendredi'),
        (SAMEDI, 'Samedi'),
        (DIMANCHE, 'Dimanche'),
    ]

    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="localisations")
    lien_maps = models.CharField(max_length=1000)  # Lien vers la localisation Google Maps
    ville = models.CharField(max_length=100, null=True, blank=True)
    quartier = models.CharField(max_length=100, null=True, blank=True)
    repere = models.CharField(max_length=255, null=True, blank=True)  # Champ pour le repère
    
    # Champs pour les horaires
    jour_ouverture = models.CharField(
        max_length=10,
        choices=JOURS_SEMAINE,
        default=LUNDI,
        null=True,
        blank=True
    )
    jour_fermeture = models.CharField(
        max_length=10,
        choices=JOURS_SEMAINE,
        default=SAMEDI,
        null=True,
        blank=True
    )
    heure_ouverture = models.TimeField(null=True, blank=True)
    heure_fermeture = models.TimeField(null=True, blank=True)
    ouvert_24h = models.BooleanField(default=False)
    ferme_jour_ferie = models.BooleanField(default=True)

    class Meta:
        unique_together = ('utilisateur',)

    def __str__(self):
        return f"{self.lien_maps} ({self.ville}, {self.quartier}, Repère: {self.repere})"

# -----------------------
# Modèle  des images de Localisation du site
# -----------------------
class LocalImages(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="images_localisation")
    image =  CloudinaryField('images_localisation')

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

class Commentaire(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="commentaires")
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name="commentaires", default=1)  # Id produit par défaut
    commentaire = models.TextField()
    image_profil =  CloudinaryField('profil_images', null=True, blank=True)  # Image de profil
    date_commentaire = models.DateTimeField(auto_now_add=True)
    note = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Note entre 1 et 5 étoiles",
    )

    
#-------------------------------------------Génération de la boutique----------------------------------


class Boutique(models.Model):
    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name="boutique",
        verbose_name="Propriétaire",
    )
    identifiant = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="Identifiant unique généré automatiquement",
    )
    titre = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Titre de la boutique",
        help_text="Un titre accrocheur pour votre boutique (ex: 'Ma belle boutique de mode')"
    )
    publier = models.BooleanField(
        default=False,
        verbose_name="Publié"
    )
    html_contenu = models.TextField(
        blank=True,
        verbose_name="Contenu HTML"
    )
    logo = CloudinaryField(
        "logo",
        null=True,
        blank=True,
    )
    premium = models.BooleanField(
        default=False,
        verbose_name="Boutique premium"
    )
    statut_publication = models.CharField(
        max_length=20,
        choices=[("chargé", "Chargé"), ("publié", "Publié")],
        default="chargé",
        verbose_name="Statut"
    )
    date_publication = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de publication"
    )
    produits_vendus = models.CharField(
        max_length=250,
        default="non",
        blank=True,
        verbose_name="Produits vendus"
    )

    class Meta:
        db_table = 'shop_boutique'
        managed = True
        verbose_name = "Boutique"
        verbose_name_plural = "Boutiques"
        ordering = ['-date_publication']

    def __str__(self):
        return f"Boutique de {self.utilisateur.nom_complet}"

    def save(self, *args, **kwargs):
        """
        Génère un identifiant unique et élégant lors de la création de la boutique.
        """
        if not self.pk and not self.identifiant:
            self._generate_identifiant()
        
        super().save(*args, **kwargs)

    def _generate_identifiant(self):
        """Méthode séparée pour générer l'identifiant"""
        try:
            base = slugify(self.utilisateur.nom_complet.split()[0]).lower()
            suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            self.identifiant = f"{base}-{suffix}"
            
            while Boutique.objects.filter(identifiant=self.identifiant).exists():
                suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
                self.identifiant = f"{base}-{suffix}"
        except Exception as e:
            self.identifiant = f"boutique-{timezone.now().strftime('%Y%m%d%H%M%S')}"

    def get_absolute_url(self, domaine):
        """
        Retourne l'URL publique de la boutique en utilisant l'identifiant.
        """
        domain_str = str(domaine.domain) if hasattr(domaine, 'domain') else str(domaine)
        return f"{domain_str.rstrip('/')}/{self.identifiant}/"

    def publier_boutique(self):
        """
        Publie la boutique et met à jour la date de publication.
        """
        self.publier = True
        self.statut_publication = "publié"
        self.date_publication = timezone.now()
        self.save()

    def depublier_boutique(self):
        """
        Dépublie la boutique et supprime la date de publication.
        """
        self.publier = False
        self.statut_publication = "chargé"
        self.date_publication = None
        self.save()

    @property
    def est_publiee(self):
        """Propriété pour vérifier facilement le statut"""
        return self.statut_publication == "publié"

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
        
        # Normalisation de l'email
        email = self.normalize_email(email)
        
        # Création de l'utilisateur
        user = self.model(
            email=email,
            nom=nom,
            role=role,
            profil=profil
        )
        
        # Hachage du mot de passe avant sauvegarde
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
        ('verificateur_comptes', 'Vérificateur de Comptes'),
        ('controleur_produits', 'Contrôleur de Produits'),
        ('gestionnaire_comptes', 'Gestionnaire de Comptes'),
        ('gestionnaire_abonnements', 'Gestionnaire abonnement'),
    ]


    VALIDATION_COMPTE = [
        ('accordé', 'Accordé'),
        ('non accordé', 'Non accordé'),
    ]

    nom = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=ROLES)
    validation_compte = models.CharField(max_length=20, choices=VALIDATION_COMPTE)
    profil =  CloudinaryField('profiles', null=True, blank=True)
    password = models.CharField(max_length=255)  # Le mot de passe haché sera stocké ici
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
        if Utilisateur.objects.filter(email=self.email).exclude(pk=self.pk).exists():
            raise ValidationError(f"L'email {self.email} existe déjà dans la base de données.")
        
        # Si le mot de passe est en clair (pas encore haché), on le hache
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
            self.set_password(self.password)
        
        super().save(*args, **kwargs)
        
        
#-------------------------------------------Gestion des abonnements-----------------------------------      

class Abonnement(models.Model):
    # Types d'abonnement (choix mensuel, trimestriel, annuel)
    TYPE_CHOICES = [
        ('1M', '1 Mois'),
        ('2M', '2 Mois'),
        ('3M', '3 Mois'),
        ('4M', '4 Mois'),
        ('5M', '5 Mois'),
        ('6M', '6 Mois'),
        ('7M', '7 Mois'),
        ('8M', '8 Mois'),
        ('9M', '9 Mois'),
        ('10M', '10 Mois'),
        ('11M', '11 Mois'),
        ('12M', '12 Mois'),
    ]

    utilisateur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='abonnements'
    )
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField()
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    methode_paiement = models.CharField(max_length=50, blank=True, null=True)
    reference_paiement = models.CharField(max_length=100, blank=True, null=True)

    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.CharField(max_length=100, blank=True, null=True)

    type_abonnement = models.CharField(
        max_length=3,
        choices=TYPE_CHOICES,
        default='1M',
    )

    class Meta:
        ordering = ['-date_debut']
        verbose_name = "Abonnement"
        verbose_name_plural = "Abonnements"

    def __str__(self):
        return f"{self.utilisateur.nom_complet} | {self.type_abonnement} | {self.date_debut.date()} → {self.date_fin.date()}"

class HistoriqueAbonnement(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    abonnement = models.ForeignKey(Abonnement, on_delete=models.SET_NULL, null=True, blank=True)
    date_action = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100)
    effectue_par = models.ForeignKey(SupportClient, on_delete=models.SET_NULL, null=True)
    details = models.TextField()

    class Meta:
        ordering = ['-date_action']