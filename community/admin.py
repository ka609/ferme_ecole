from django.contrib import admin

from .models import (
    Avis,
    SujetForum,
    ReponseForum,
    Formation,
    SuiviFormation,
)


# Gestion des avis
@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):

    list_display = (
        "produit",
        "client",
        "note",
        "date",
    )

    list_filter = (
        "note",
        "date",
    )

    search_fields = (
        "produit__nom",
        "client__email",
        "commentaire",
    )

    autocomplete_fields = (
        "produit",
        "client",
    )

    readonly_fields = (
        "date",
    )


# Gestion des sujets forum
@admin.register(SujetForum)
class SujetForumAdmin(admin.ModelAdmin):

    list_display = (
        "titre",
        "auteur",
        "epingle",
        "ferme",
        "date",
    )

    list_filter = (
        "epingle",
        "ferme",
        "date",
    )

    search_fields = (
        "titre",
        "contenu",
        "auteur__email",
    )

    autocomplete_fields = (
        "auteur",
    )

    readonly_fields = (
        "date",
    )


# Gestion des réponses forum
@admin.register(ReponseForum)
class ReponseForumAdmin(admin.ModelAdmin):

    list_display = (
        "sujet",
        "auteur",
        "date",
    )

    list_filter = (
        "date",
    )

    search_fields = (
        "contenu",
        "auteur__email",
        "sujet__titre",
    )

    autocomplete_fields = (
        "sujet",
        "auteur",
    )

    readonly_fields = (
        "date",
    )


# Gestion des formations
@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):

    list_display = (
        "titre",
        "publie_par",
        "date",
    )

    search_fields = (
        "titre",
        "description",
    )

    list_filter = (
        "date",
    )

    autocomplete_fields = (
        "publie_par",
    )

    readonly_fields = (
        "date",
    )


# Gestion des suivis formation
@admin.register(SuiviFormation)
class SuiviFormationAdmin(admin.ModelAdmin):

    list_display = (
        "formation",
        "producteur",
        "progression",
        "terminee",
        "date",
    )

    list_filter = (
        "terminee",
        "date",
    )

    search_fields = (
        "formation__titre",
        "producteur__nom_exploitation",
    )

    autocomplete_fields = (
        "formation",
        "producteur",
    )

    readonly_fields = (
        "date",
    )