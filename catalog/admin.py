# catalog/admin.py

from django.contrib import admin

from .models import (
    Categorie,
    Certification,
    Produit,
    ProduitImage,
)


# Gestion des catégories
@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):

    list_display = (
        "nom",
        "description",
    )

    search_fields = (
        "nom",
    )

    ordering = (
        "nom",
    )


# Gestion des certifications
@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):

    list_display = (
        "producteur",
        "type",
        "statut",
        "date_debut",
        "date_fin",
        "est_active",
    )

    list_filter = (
        "statut",
        "date_debut",
        "date_fin",
    )

    search_fields = (
        "type",
        "numero",
        "producteur__nom_exploitation",
        "producteur__utilisateur__email",
    )

    autocomplete_fields = (
        "producteur",
    )

    readonly_fields = (
        "date_validation",
        "est_active",
    )


# Gestion des produits
@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):

    list_display = (
        "nom",
        "producteur",
        "categorie",
        "prix",
        "stock",
        "type_produit",
        "valide",
        "disponible",
        "date_creation",
    )

    list_filter = (
        "categorie",
        "type_produit",
        "valide",
        "disponible",
        "date_creation",
    )

    search_fields = (
        "nom",
        "producteur__nom_exploitation",
        "categorie__nom",
    )

    autocomplete_fields = (
        "producteur",
        "categorie",
        "valide_par",
    )

    readonly_fields = (
        "date_creation",
        "date_modification",
        "date_validation",
    )


# Gestion des images produits
@admin.register(ProduitImage)
class ProduitImageAdmin(admin.ModelAdmin):

    list_display = (
        "produit",
        "image",
    )

    search_fields = (
        "produit__nom",
    )

    autocomplete_fields = (
        "produit",
    )