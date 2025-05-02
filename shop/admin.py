from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import (
    Utilisateur,
    UtilisateurTemporaire,
    Produit,
    Devise,
    SliderImage,
    Localisation,
    LocalImages,
    Commande,
    Commentaire,
    InformationsSupplementaires,
    InformationsSupplementairesTemporaire,
    Client,
    Variante,
    Tag,
    ProduitImage,
    Boutique,
    SupportClient,
    Vente,
    VenteAttente,
    Abonnement,
    HistoriqueAbonnement,

)

# Configuration de l'administration pour le modèle Utilisateur
class UtilisateurAdmin(UserAdmin):
    # Liste des champs à afficher dans l'interface d'administration
    list_display = ('identifiant_unique', 'nom_complet', 'nom_boutique', 'email', 'produits_vendus', 'logo_boutique', 'is_active', 'is_staff', 'date_joined', 'statut_validation_compte')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('identifiant_unique', 'email', 'nom_complet', 'nom_boutique', 'produits_vendus')  # Mise à jour ici
    ordering = ('identifiant_unique',)

    # Définir les champs à afficher dans les formulaires de création et de modification
    fieldsets = (
        (None, {'fields': ('username', 'password')}),  # Les champs de base
        ('Informations personnelles', {'fields': ('identifiant_unique', 'nom_complet', 'email', 'nom_boutique', 'numero', 'produits_vendus', 'statut_validation_compte', 'logo_boutique')}),  # Mise à jour ici
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),  # Permissions
        ('Dates', {'fields': ('last_login', 'date_joined')}),  # Dates
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),  # Les champs pour la création
        ('Informations personnelles', {'fields': ('identifiant_unique', 'nom_complet', 'email', 'nom_boutique', 'numero', 'produits_vendus', 'statut_validation_compte', 'logo_boutique')}),  # Mise à jour ici
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),  # Permissions
        ('Dates', {'fields': ('last_login', 'date_joined')}),  # Dates
    )


@admin.register(UtilisateurTemporaire)
class UtilisateurTemporaireAdmin(admin.ModelAdmin):
    list_display = ('identifiant_unique', 'email', 'nom_complet', 'numero', 'nom_boutique', 'created_at')
    search_fields = ('identifiant_unique', 'email', 'nom_complet', 'numero', 'nom_boutique')
    list_filter = ('created_at',)

# Enregistrement du modèle Utilisateur dans l'admin
admin.site.register(Utilisateur, UtilisateurAdmin)

@admin.register(InformationsSupplementaires)
class InformationsSupplementairesAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'type_boutique', 'source_decouverte', 'produits_vendus')
    search_fields = ('utilisateur__nom_boutique', 'utilisateur__nom_complet', 'type_boutique', 'source_decouverte')
    list_filter = ('type_boutique', 'source_decouverte')
    ordering = ('utilisateur',)

@admin.register(InformationsSupplementairesTemporaire)
class InformationsSupplementairesTemporaireAdmin(admin.ModelAdmin):
    # Affichage des colonnes dans la liste
    list_display = ('utilisateur_temporaire', 'type_boutique', 'source_decouverte', 'produits_vendus')

    # Champs de recherche dans l'admin
    search_fields = ('utilisateur_temporaire__nom_boutique', 'utilisateur_temporaire__nom_complet', 'type_boutique', 'source_decouverte')

    # Filtres pour faciliter la recherche
    list_filter = ('type_boutique', 'source_decouverte')

    # Ordre de tri par défaut dans l'admin
    ordering = ('utilisateur_temporaire',)
    
# Enregistrement des autres modèles dans l'admin

class ClientAdmin(UserAdmin):
    # Liste des champs à afficher dans l'interface d'administration
    list_display = ('email', 'nom_complet', 'telephone', 'adresse', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('email', 'nom_complet', 'telephone')
    ordering = ('email',)

    # Définir les champs à afficher dans les formulaires de création et de modification
    fieldsets = (
        (None, {'fields': ('email', 'password')}),  # Champs de base
        ('Informations personnelles', {'fields': ('nom_complet', 'adresse', 'telephone')}),  # Informations personnelles
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),  # Permissions
        ('Dates', {'fields': ('last_login', 'date_joined')}),  # Dates de connexion
    )

    # Champs à afficher lors de la création d'un utilisateur
    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2')}),  # Champs de base
        ('Informations personnelles', {'fields': ('nom_complet', 'adresse', 'telephone')}),  # Informations personnelles
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),  # Permissions
        ('Dates', {'fields': ('last_login', 'date_joined')}),  # Dates de connexion
    )

# Enregistrer le modèle et son admin
admin.site.register(Client, ClientAdmin)


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('identifiant', 'nom', 'prix', 'ancien_prix', 'type_produit', 'disponible', 'quantite_stock', 'utilisateur', 'reference', 'mise_en_avant', 'date_ajout')
    list_filter = ('disponible', 'utilisateur', 'etat', 'tags', 'mise_en_avant', 'type_produit')
    search_fields = ('nom', 'description', 'utilisateur__nom_complet', 'reference', 'identifiant')
    ordering = ('nom',)
    list_editable = ('disponible', 'mise_en_avant', 'type_produit', 'ancien_prix')
    filter_horizontal = ('tags',)
    readonly_fields = ('identifiant',)  # L'identifiant est en lecture seule

    fieldsets = (
        (None, {
            'fields': ('identifiant', 'utilisateur', 'nom', 'description', 'image')
        }),
        ('Détails du produit', {
            'fields': ('prix', 'ancien_prix', 'type_produit', 'quantite_stock', 'reference', 'marque')
        }),
        ('Caractéristiques', {
            'fields': ('poids', 'dimensions', 'etat', 'video_promotionnelle')
        }),
        ('Options', {
            'fields': ('disponible', 'mise_en_avant', 'tags')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """ Rend les champs promotionnels obligatoires si le produit est une promo """
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.type_produit == 'Promo':
            return readonly_fields
        return readonly_fields + ['ancien_prix']

@admin.register(VenteAttente)
class VenteAttenteAdmin(admin.ModelAdmin):
    list_display = ('nom_produit', 'utilisateur', 'produit', 'prix_achat', 'prix_vente', 'quantite_vendue', 'date_vente')
    search_fields = ('nom_produit', 'utilisateur__nom_complet', 'produit__nom')
    list_filter = ('date_vente', 'utilisateur') 
      
@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('nom_produit', 'utilisateur', 'prix_achat', 'prix_vente', 'quantite_vendue', 'statut', 'date_vente')
    list_filter = ('utilisateur', 'date_vente', 'statut')  # Ajout de filtre sur le statut
    search_fields = ('nom_produit', 'utilisateur__username', 'produit__nom')
    ordering = ('-date_vente',)

    readonly_fields = ('date_vente',)  # Enlever les propriétés calculées

    def get_queryset(self, request):
        """Optimisation de la requête pour éviter trop de jointures."""
        return super().get_queryset(request).select_related('utilisateur', 'produit')

# Enregistrement du modèle Variante
@admin.register(Variante)
class VarianteAdmin(admin.ModelAdmin):
    list_display = ('produit', 'taille', 'couleur', 'prix', 'quantite_stock', 'reference','image')
    list_filter = ('produit', 'taille', 'couleur')
    search_fields = ('produit__nom', 'reference', 'taille', 'couleur')
    ordering = ('produit', 'taille', 'couleur')
    
# Enregistrement du modèle Tag
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)
    ordering = ('nom',)
    
@admin.register(ProduitImage)
class ProduitImageAdmin(admin.ModelAdmin):
    list_display = ('produit', 'image',  'date_ajout')
    list_filter = ('produit', )
    search_fields = ('produit__nom',)
    ordering = ('produit', 'date_ajout')
    raw_id_fields = ('produit',)  # Permet de choisir un produit plus facilement dans la liste déroulante
@admin.register(Devise)
class DeviseAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'devise')  # Afficher les champs utilisateur et devise
    search_fields = ('utilisateur__nom_complet', 'devise')  # Permet de rechercher par nom d'utilisateur et devise
    list_filter = ('devise',)  # Ajoute un filtre pour les devises
@admin.register(SliderImage)
class SliderImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'utilisateur', 'image')
    search_fields = ('title', 'utilisateur__nom_complet')
    
    
@admin.register(Localisation)
class LocalisationAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'lien_maps', 'ville', 'quartier', 'repere', 'jour_ouverture', 'jour_fermeture', 'heure_ouverture', 'heure_fermeture')
    search_fields = ('ville', 'quartier', 'repere')
    list_filter = ('ville', 'quartier')
    fieldsets = (
        ('Localisation', {
            'fields': ('utilisateur', 'lien_maps', 'ville', 'quartier', 'repere')
        }),
        ('Horaires', {
            'fields': ('jour_ouverture', 'jour_fermeture', 'heure_ouverture', 'heure_fermeture', 'ouvert_24h', 'ferme_jour_ferie'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LocalImages)
class LocalImagesAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'image', 'get_image_preview')
    search_fields = ('utilisateur__nom_complet',)

    # Option pour afficher un aperçu de l'image dans l'interface d'administration
    def get_image_preview(self, obj):
        return f'<img src="{obj.image.url}" width="100" height="100" />' if obj.image else 'Aucune image'
    get_image_preview.allow_tags = True
    get_image_preview.short_description = 'Aperçu de l\'image'
    
@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('nom_client', 'date_commande', 'statut', 'utilisateur')
    list_filter = ('statut', 'utilisateur')
    search_fields = ('nom_client', 'numero_client', 'utilisateur__nom_complet')
    ordering = ('-date_commande',)


@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'produit', 'date_commentaire', 'note')
    list_filter = ('date_commentaire', 'utilisateur', 'produit')
    search_fields = ('utilisateur__nom_complet', 'commentaire', 'produit__nom')


 
#-------------------------------------Génération de la boutique ---------------------  
@admin.register(Boutique)
class BoutiqueAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'identifiant', 'publier', 'date_publication', 'premium')
    search_fields = ('utilisateur__nom', 'titre', 'premium', 'identifiant')  # Remplacement de description par titre
    list_filter = ('publier', 'date_publication', 'premium')
    readonly_fields = ('date_publication', 'identifiant')
    fieldsets = (
        (None, {
            'fields': ('utilisateur', 'identifiant', 'titre', 'logo')  # Remplacement de description par titre
        }),
        ('Statut', {
            'fields': ('publier', 'statut_publication', 'date_publication', 'premium')
        }),
        ('Contenu', {
            'fields': ('html_contenu', 'produits_vendus')  # Correction de la faute de frappe (produits_vendus)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """
        Rend certains champs en lecture seule si la boutique est publiée
        Version plus subtile qui permet certaines modifications même après publication
        """
        readonly_fields = list(super().get_readonly_fields(request, obj))
        
        if obj and obj.publier:
            # Champs qu'on veut verrouiller après publication
            locked_fields = [
                'utilisateur',       # Le propriétaire ne peut pas changer
                'statut_publication', # Doit utiliser les actions dédiées
                'identifiant'        # Déjà en readonly de base
            ]
            readonly_fields.extend(locked_fields)
            
            # Si premium, on verrouille aussi le statut premium
            if obj.premium:
                readonly_fields.append('premium')
        
        return tuple(set(readonly_fields))  # Évite les doublons

    def save_model(self, request, obj, form, change):
        """
        Gestion personnalisée de la sauvegarde pour la cohérence des données
        """
        if obj.publier and not obj.date_publication:
            obj.date_publication = timezone.now()
        super().save_model(request, obj, form, change)

    actions = ['publier_boutiques', 'depublier_boutiques']
    
    def publier_boutiques(self, request, queryset):
        """Action admin pour publier des boutiques"""
        updated = queryset.update(
            publier=True,
            statut_publication="publié",
            date_publication=timezone.now()
        )
        self.message_user(request, f"{updated} boutiques publiées avec succès.")
    
    def depublier_boutiques(self, request, queryset):
        """Action admin pour dépublier des boutiques"""
        updated = queryset.update(
            publier=False,
            statut_publication="chargé",
            date_publication=None
        )
        self.message_user(request, f"{updated} boutiques dépubliées avec succès.")
        
#-------------------------------------Gestion des personnels du support client --------------------- 

class SupportClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'role', 'validation_compte', 'is_active', 'is_admin')
    list_filter = ('role', 'validation_compte', 'is_active')
    search_fields = ('nom', 'email')
    ordering = ('nom',)

    fieldsets = (
        (None, {
            'fields': ('nom', 'email', 'role', 'profil', 'password')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_admin', 'validation_compte')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nom', 'email', 'role', 'profil', 'password', 'validation_compte')
        }),
    )

    filter_horizontal = ()
    list_per_page = 25

admin.site.register(SupportClient, SupportClientAdmin)

#Gestion des abonnements

@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    list_display = (
        'utilisateur',
        'date_debut',
        'date_fin',
        'montant',
        'est_premium',
        'actif',
        'methode_paiement',
        'reference_paiement',
        'cree_par',
    )
    list_filter = (
        'actif',
        'est_premium',
        'methode_paiement',
        'date_debut',
        'cree_par',
    )
    search_fields = (
        'utilisateur__nom_complet',
        'utilisateur__identifiant_unique',
        'reference_paiement',
    )
    ordering = ('-date_debut',)
    
    


@admin.register(HistoriqueAbonnement)
class HistoriqueAbonnementAdmin(admin.ModelAdmin):
    list_display = (
        'utilisateur',
        'abonnement',
        'action',
        'date_action',
        'effectue_par',
    )
    list_filter = (
        'action',
        'date_action',
        'effectue_par',
    )
    search_fields = (
        'utilisateur__nom_complet',
        'abonnement__id',
        'effectue_par__nom_complet',
        'details',
    )
    ordering = ('-date_action',)
    
