from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Utilisateur,
    Producteur,
    Notification,
    JournalActivite,
    Parametre,
)



# =====================================================
# UTILISATEUR
# =====================================================

@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):

    model = Utilisateur


    list_display = (
        "username",
        "nom",
        "prenom",
        "email",
        "telephone",
        "role",
        "actif",
        "is_staff",
    )


    list_filter = (
        "role",
        "actif",
        "is_staff",
        "is_superuser",
    )


    search_fields = (
        "username",
        "email",
        "nom",
        "prenom",
        "telephone",
    )


    ordering = (
        "-date_creation",
    )


    fieldsets = (

        (
            "Informations de connexion",
            {
                "fields": (
                    "username",
                    "password",
                )
            }
        ),


        (
            "Informations personnelles",
            {
                "fields": (
                    "nom",
                    "prenom",
                    "email",
                    "telephone",
                    "photo",
                    "adresse",
                )
            }
        ),


        (
            "Rôle plateforme",
            {
                "fields": (
                    "role",
                    "type_client",
                    "autre_precision",
                )
            }
        ),


        (
            "Permissions Django",
            {
                "fields": (
                    "is_active",
                    "actif",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            }
        ),


        (
            "Informations système",
            {
                "fields": (
                    "premiere_connexion",
                    "date_creation",
                    "last_login",
                    "date_joined",
                )
            }
        ),

    )


    readonly_fields = (
        "date_creation",
        "last_login",
        "date_joined",
    )



# =====================================================
# PRODUCTEUR
# =====================================================

@admin.register(Producteur)
class ProducteurAdmin(admin.ModelAdmin):


    list_display = (
        "nom_exploitation",
        "utilisateur",
        "date_creation",
        "est_certifie_bio",
    )


    search_fields = (
        "nom_exploitation",
        "utilisateur__username",
        "utilisateur__email",
    )


    list_filter = (
        "date_creation",
    )


    readonly_fields = (
        "date_creation",
        "est_certifie_bio",
    )



# =====================================================
# NOTIFICATIONS
# =====================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):


    list_display = (
        "titre",
        "utilisateur",
        "lu",
        "date",
    )


    list_filter = (
        "lu",
        "date",
    )


    search_fields = (
        "titre",
        "message",
        "utilisateur__username",
    )


    readonly_fields = (
        "date",
    )



# =====================================================
# JOURNAL ACTIVITE
# =====================================================

@admin.register(JournalActivite)
class JournalActiviteAdmin(admin.ModelAdmin):


    list_display = (
        "utilisateur",
        "action",
        "objet",
        "adresse_ip",
        "date",
    )


    list_filter = (
        "action",
        "date",
    )


    search_fields = (
        "utilisateur__username",
        "action",
        "objet",
    )


    readonly_fields = (
        "utilisateur",
        "action",
        "objet",
        "adresse_ip",
        "date",
    )



# =====================================================
# PARAMETRES
# =====================================================

@admin.register(Parametre)
class ParametreAdmin(admin.ModelAdmin):


    list_display = (
        "commission_plateforme",
        "commission_livreur",
        "devise",
        "maintenance",
    )


    readonly_fields = (
        "id",
    )


    def has_add_permission(self, request):

        """
        Un seul paramètre global existe.
        """

        return not Parametre.objects.exists()


    def has_delete_permission(self, request, obj=None):

        return False