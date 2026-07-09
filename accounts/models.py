"""
accounts/models.py

Gestion :
- Utilisateurs
- Producteurs
- Notifications
- Journal d'activité
- Paramètres plateforme
"""

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator
)
from django.db import models
from django.utils.translation import gettext_lazy as _



# =====================================================
# ROLES
# =====================================================

class Role(models.TextChoices):

    ADMIN = "ADMIN", _("Administrateur")
    PRODUCTEUR = "PRODUCTEUR", _("Producteur")
    CLIENT = "CLIENT", _("Client")
    LIVREUR = "LIVREUR", _("Livreur")



# =====================================================
# TYPES CLIENT
# =====================================================

class TypeClient(models.TextChoices):

    RESTAURANT = "RESTAURANT", _("Restaurant")
    REVENDEUR = "REVENDEUR", _("Revendeur / Transformateur")
    AUTRE = "AUTRE", _("Autre")



# =====================================================
# UTILISATEUR
# =====================================================

class Utilisateur(AbstractUser):

    email = models.EmailField(
        _("adresse email"),
        unique=True
    )

    nom = models.CharField(
        max_length=100
    )

    prenom = models.CharField(
        max_length=100
    )

    telephone = models.CharField(
        max_length=20,
        unique=True
    )


    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
        db_index=True
    )


    type_client = models.CharField(
        max_length=20,
        choices=TypeClient.choices,
        null=True,
        blank=True,
        help_text="Utilisé uniquement pour les comptes CLIENT."
    )


    autre_precision = models.CharField(
        max_length=100,
        blank=True,
        help_text="Précision si le type client est AUTRE."
    )


    photo = models.ImageField(
        upload_to="utilisateurs/photos/",
        blank=True,
        null=True
    )


    adresse = models.TextField(
        blank=True,
        help_text="Lieu de résidence ou adresse de livraison."
    )


    actif = models.BooleanField(
        default=True,
        help_text="Permet de suspendre un compte."
    )


    premiere_connexion = models.BooleanField(
        default=False
    )


    date_creation = models.DateTimeField(
        auto_now_add=True
    )


    class Meta:

        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

        ordering = [
            "-date_creation"
        ]


        indexes = [

            models.Index(
                fields=["role"],
                name="idx_utilisateur_role"
            ),

            models.Index(
                fields=["role", "actif"],
                name="idx_utilisateur_role_actif"
            ),

        ]


        constraints = [

            models.CheckConstraint(

                condition=
                models.Q(role="CLIENT")
                |
                models.Q(type_client__isnull=True),

                name="type_client_uniquement_client"
            )

        ]



    def __str__(self):

        return (
            f"{self.username} - "
            f"{self.prenom} {self.nom}"
        )



    def clean(self):

        super().clean()


        if self.role == Role.CLIENT:


            if not self.type_client:

                raise ValidationError(
                    {
                        "type_client":
                        "Un client doit préciser son type."
                    }
                )


            if (
                self.type_client == TypeClient.AUTRE
                and not self.autre_precision
            ):

                raise ValidationError(
                    {
                        "autre_precision":
                        "Veuillez préciser votre activité."
                    }
                )


        elif self.type_client:

            raise ValidationError(
                {
                    "type_client":
                    "Ce champ est réservé aux clients."
                }
            )



    @property
    def nom_complet(self):

        return f"{self.prenom} {self.nom}"



# =====================================================
# PRODUCTEUR
# =====================================================

class Producteur(models.Model):

    """
    Profil producteur.

    Créé uniquement par ADMIN.
    """

    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name="producteur",
        limit_choices_to={
            "role": Role.PRODUCTEUR
        }
    )


    nom_exploitation = models.CharField(
        max_length=150
    )


    description = models.TextField(
        blank=True
    )


    date_creation = models.DateField(
        auto_now_add=True
    )



    class Meta:

        verbose_name = "Producteur"
        verbose_name_plural = "Producteurs"

        ordering = [
            "nom_exploitation"
        ]



    def __str__(self):

        return self.nom_exploitation



    def clean(self):

        if (
            self.utilisateur_id
            and self.utilisateur.role != Role.PRODUCTEUR
        ):

            raise ValidationError(
                "Le profil doit être lié à un utilisateur PRODUCTEUR."
            )



    @property
    def est_certifie_bio(self):

        from django.utils import timezone

        return self.certifications.filter(
            statut="VALIDEE",
            date_fin__gte=timezone.now().date()
        ).exists()



# =====================================================
# NOTIFICATIONS
# =====================================================

class Notification(models.Model):


    utilisateur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name="notifications"
    )


    titre = models.CharField(
        max_length=150
    )


    message = models.TextField()


    lu = models.BooleanField(
        default=False
    )


    date = models.DateTimeField(
        auto_now_add=True
    )



    class Meta:

        ordering = [
            "-date"
        ]



    def __str__(self):

        return self.titre



# =====================================================
# JOURNAL ACTIVITE
# =====================================================

class JournalActivite(models.Model):


    utilisateur = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_activite"
    )


    action = models.CharField(
        max_length=100
    )


    objet = models.CharField(
        max_length=150,
        blank=True
    )


    adresse_ip = models.GenericIPAddressField(
        null=True,
        blank=True
    )


    date = models.DateTimeField(
        auto_now_add=True
    )



    class Meta:

        ordering = [
            "-date"
        ]



# =====================================================
# PARAMETRES PLATEFORME
# =====================================================

class Parametre(models.Model):


    commission_plateforme = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )


    commission_livreur = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )


    devise = models.CharField(
        max_length=10,
        default="FCFA"
    )


    maintenance = models.BooleanField(
        default=False
    )



    class Meta:

        verbose_name = "Paramètre plateforme"



    def __str__(self):

        return "Paramètres plateforme"



    def save(self, *args, **kwargs):

        self.pk = 1
        super().save(*args, **kwargs)



    def delete(self, *args, **kwargs):

        pass



    @classmethod
    def charger(cls):

        obj, _ = cls.objects.get_or_create(
            pk=1
        )

        return obj