from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import (
    Utilisateur,
    Producteur,
    Notification,
    JournalActivite,
    Parametre,
)

from .forms import (
    UtilisateurCreationForm,
    UtilisateurChangeForm,
)



# =====================================================
# UTILISATEUR
# =====================================================

@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):

    model = Utilisateur

    form = UtilisateurChangeForm
    add_form = UtilisateurCreationForm

    list_display = (
        "username",
        "nom_complet_admin",
        "email",
        "telephone",
        "role",
        "statut_compte",
        "is_staff",
    )

    list_filter = (
        "role",
        "actif",
        "is_staff",
        "is_superuser",
        "premiere_connexion",
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

    readonly_fields = (
        "date_creation",
        "last_login",
        "date_joined",
    )

    fieldsets = (

        (
            "Connexion",
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
            "Profil plateforme",
            {
                "fields": (
                    "role",
                    "type_client",
                    "autre_precision",
                )
            }
        ),

        (
            "État du compte",
            {
                "fields": (
                    "actif",
                    "premiere_connexion",
                )
            }
        ),

        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            }
        ),

        (
            "Dates",
            {
                "fields": (
                    "date_creation",
                    "last_login",
                    "date_joined",
                )
            }
        ),
    )

    add_fieldsets = (

        (
            "Créer utilisateur",
            {
                "classes": (
                    "wide",
                ),

                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "nom",
                    "prenom",
                    "email",
                    "telephone",
                    "role",
                    "type_client",
                    "autre_precision",
                ),
            },
        ),
    )

    @admin.display(
        description="Nom complet"
    )
    def nom_complet_admin(self, obj):

        return obj.nom_complet


    @admin.display(
        description="Statut"
    )
    def statut_compte(self, obj):

        if obj.actif:
            return format_html(
                '<span style="color:green;">{}</span>',
                "Actif"
            )

        return format_html(
            '<span style="color:red;">{}</span>',
            "Suspendu"
        )
# =====================================================
# PRODUCTEUR
# =====================================================

@admin.register(Producteur)
class ProducteurAdmin(admin.ModelAdmin):

    list_display = (
        "nom_exploitation",
        "utilisateur",
        "certification_bio",
        "date_creation",
    )

    list_filter = (
        "date_creation",
    )

    search_fields = (
        "nom_exploitation",
        "utilisateur__username",
        "utilisateur__email",
    )

    readonly_fields = (
        "date_creation",
        "certification_bio",
    )

    @admin.display(
        description="BIO SPG"
    )
    def certification_bio(self, obj):

        if obj.est_certifie_bio:
            return format_html(
                '<span style="color:green;">{}</span>',
                "Validée"
            )

        return format_html(
            '<span style="color:red;">{}</span>',
            "Non validée"
        )
# =====================================================
# NOTIFICATIONS
# =====================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):


    list_display = (

        "titre",
        "utilisateur",
        "statut",
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



    @admin.display(
        description="État"
    )
    def statut(self, obj):

        if obj.lu:

            return "Lue"

        return "Non lue"



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

        return not Parametre.objects.exists()



    def has_delete_permission(self, request, obj=None):

        return False