"""
market/admin.py

Administration du marché :
- Paniers
- Commandes
- Paiements
- Versements
- Livraisons
- Commissions
"""

from django.contrib import admin

from .models import (
    Panier,
    PanierArticle,
    Commande,
    LigneCommande,
    Paiement,
    Versement,
    SocieteLivraison,
    Livraison,
    Commission,
)


# Gestion des paniers
@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):

    list_display = (
        "client",
        "producteur",
        "date_creation",
    )

    search_fields = (
        "client__email",
        "producteur__nom_exploitation",
    )

    autocomplete_fields = (
        "client",
        "producteur",
    )

    readonly_fields = (
        "date_creation",
    )


# Gestion des articles panier
@admin.register(PanierArticle)
class PanierArticleAdmin(admin.ModelAdmin):

    list_display = (
        "panier",
        "produit",
        "quantite",
        "prix",
        "sous_total",
    )

    search_fields = (
        "produit__nom",
        "panier__client__email",
    )

    autocomplete_fields = (
        "panier",
        "produit",
    )


# Gestion des commandes
@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):

    list_display = (
        "numero",
        "client",
        "producteur",
        "statut",
        "montant_total",
        "date_commande",
    )

    list_filter = (
        "statut",
        "date_commande",
    )

    search_fields = (
        "numero",
        "client__email",
        "producteur__nom_exploitation",
    )

    autocomplete_fields = (
        "client",
        "producteur",
        "livreur",
    )

    readonly_fields = (
        "numero",
        "montant_total",
        "date_commande",
    )


# Gestion des lignes commande
@admin.register(LigneCommande)
class LigneCommandeAdmin(admin.ModelAdmin):

    list_display = (
        "commande",
        "produit",
        "quantite",
        "prix",
        "sous_total",
    )

    search_fields = (
        "commande__numero",
        "produit__nom",
    )

    autocomplete_fields = (
        "commande",
        "produit",
    )

    readonly_fields = (
        "sous_total",
    )


# Gestion des paiements
@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):

    list_display = (
        "commande",
        "montant",
        "moyen",
        "statut",
        "date_paiement",
    )

    list_filter = (
        "moyen",
        "statut",
    )

    search_fields = (
        "commande__numero",
        "reference",
    )

    autocomplete_fields = (
        "commande",
    )

    readonly_fields = (
        "date_creation",
        "date_paiement",
    )


# Gestion des versements producteurs
@admin.register(Versement)
class VersementAdmin(admin.ModelAdmin):

    list_display = (
        "commande",
        "producteur",
        "montant",
        "commission_plateforme",
        "montant_net",
        "statut",
    )

    list_filter = (
        "statut",
        "date",
    )

    search_fields = (
        "commande__numero",
        "producteur__nom_exploitation",
    )

    autocomplete_fields = (
        "producteur",
        "commande",
    )

    readonly_fields = (
        "montant_net",
        "date",
        "date_versement",
    )


# Gestion des sociétés livraison
@admin.register(SocieteLivraison)
class SocieteLivraisonAdmin(admin.ModelAdmin):

    list_display = (
        "nom",
        "responsable",
        "telephone",
        "actif",
    )

    list_filter = (
        "actif",
    )

    search_fields = (
        "nom",
        "responsable",
        "telephone",
    )


# Gestion des livraisons
@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):

    list_display = (
        "commande",
        "livreur",
        "societe",
        "statut",
        "date_livraison",
    )

    list_filter = (
        "statut",
        "date_livraison",
    )

    search_fields = (
        "commande__numero",
        "livreur__email",
    )

    autocomplete_fields = (
        "commande",
        "livreur",
        "societe",
        "confirmee_par",
    )

    readonly_fields = (
        "date_prise",
        "date_livraison",
        "date_confirmation",
    )


# Gestion des commissions
@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):

    list_display = (
        "livraison",
        "livreur",
        "montant",
        "statut",
    )

    list_filter = (
        "statut",
    )

    search_fields = (
        "livreur__email",
        "livraison__commande__numero",
    )

    autocomplete_fields = (
        "livraison",
        "livreur",
    )