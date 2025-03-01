from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Utilisateur,
    NavbarSettings,
    UtilisateurTemporaire,
    Produit,
    Devise,
    SliderImage,
    Localisation,
    LocalImages,
    Commande,
    DetailCommande,
    Commentaire,
    Message,
    BoutiqueSettings,
    BoutiqueNavCusor,
    InformationsSupplementaires,
    InformationsSupplementairesTemporaire,
    Client,
    Variante,
    Tag,
    ProduitImage,
    Boutique,
    SupportClient,
    Vente,

)

# Configuration de l'administration pour le modèle Utilisateur
class UtilisateurAdmin(UserAdmin):
    # Liste des champs à afficher dans l'interface d'administration
    list_display = ('identifiant_unique', 'nom_complet', 'nom_boutique', 'email', 'produits_vendus', 'is_active', 'is_staff', 'date_joined', 'statut_validation_compte')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('identifiant_unique', 'email', 'nom_complet', 'nom_boutique', 'produits_vendus')  # Mise à jour ici
    ordering = ('identifiant_unique',)

    # Définir les champs à afficher dans les formulaires de création et de modification
    fieldsets = (
        (None, {'fields': ('username', 'password')}),  # Les champs de base
        ('Informations personnelles', {'fields': ('identifiant_unique', 'nom_complet', 'email', 'nom_boutique', 'numero', 'produits_vendus', 'statut_validation_compte')}),  # Mise à jour ici
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),  # Permissions
        ('Dates', {'fields': ('last_login', 'date_joined')}),  # Dates
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),  # Les champs pour la création
        ('Informations personnelles', {'fields': ('identifiant_unique', 'nom_complet', 'email', 'nom_boutique', 'numero', 'produits_vendus')}),  # Mise à jour ici
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
    list_display = ('nom', 'prix', 'disponible', 'quantite_stock', 'utilisateur', 'reference', 'mise_en_avant', 'date_ajout')
    list_filter = ('disponible', 'utilisateur', 'etat', 'tags', 'mise_en_avant')
    search_fields = ('nom', 'description', 'utilisateur__nom_complet', 'reference')
    ordering = ('nom',)
    list_editable = ('disponible', 'mise_en_avant')  # Ajout de mise_en_avant pour modification rapide
    filter_horizontal = ('tags',)  # Pour un champ M2M (Many-to-Many) comme les tags

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
    list_display = ('utilisateur', 'lien_maps', 'ville', 'quartier', 'repere')  # Ajout du champ 'repere'
    search_fields = ('utilisateur__nom_complet', 'ville', 'quartier', 'repere')  # Ajout du champ 'repere'

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


@admin.register(DetailCommande)
class DetailCommandeAdmin(admin.ModelAdmin):
    list_display = ('commande', 'produit', 'quantite')
    search_fields = ('commande__nom_client', 'produit__nom')

@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'produit', 'date_commentaire', 'note')
    list_filter = ('date_commentaire', 'utilisateur', 'produit')
    search_fields = ('utilisateur__nom_complet', 'commentaire', 'produit__nom')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('nom_utilisateur', 'sujet', 'date_message', 'utilisateur')
    list_filter = ('date_message', 'utilisateur')
    search_fields = ('nom_utilisateur', 'sujet', 'utilisateur__nom_complet')
    ordering = ('-date_message',)
#---------------------------Gestion des styles du site-------------------------------------
      #Gestion du fond de couleur de le NavBar:
@admin.register(NavbarSettings)
class NavbarSettingsAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'couleur_fond')  # Affiche l'utilisateur et la couleur de fond choisie
    search_fields = ('utilisateur__username', 'utilisateur__email')  # Recherche par nom d'utilisateur et email
    list_filter = ('couleur_fond',)  # Filtre par couleur de fond
    
@admin.register(BoutiqueSettings)
class BoutiqueSettingsAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'couleur_texte')  # Affiche l'utilisateur et la couleur de texte choisie
    search_fields = ('utilisateur__username', 'utilisateur__email')  # Recherche par nom d'utilisateur et email
    list_filter = ('couleur_texte',)  # Filtre par couleur de texte
    
@admin.register(BoutiqueNavCusor)
class BoutiqueSettingsAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'couleur_texte_cursor')  # Affiche l'utilisateur et la couleur de texte choisie
    search_fields = ('utilisateur__username', 'utilisateur__email')  # Recherche par nom d'utilisateur et email
    list_filter = ('couleur_texte_cursor',)  # Filtre par couleur de texte
    
#-------------------------------------Génération de la boutique ---------------------  

@admin.register(Boutique)
class BoutiqueAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'publier', 'date_publication', 'premium')  # Afficher utilisateur, statut de publication, date de publication et premium
    search_fields = ('utilisateur__nom', 'description', 'premium')  # Permet de rechercher par nom de l'utilisateur, description et premium
    list_filter = ('publier', 'date_publication', 'premium')  # Ajoute des filtres pour le statut, la date de publication et premium
    readonly_fields = ('date_publication',)  # Rendre la date de publication non modifiable

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
