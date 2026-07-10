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
        _("Adresse email"),
        unique=True
    )


    nom = models.CharField(
        _("Nom"),
        max_length=100
    )


    prenom = models.CharField(
        _("Prénom"),
        max_length=100
    )


    telephone = models.CharField(
        _("Téléphone"),
        max_length=20,
        unique=True
    )


    role = models.CharField(
        _("Rôle"),
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
        db_index=True
    )


    type_client = models.CharField(
        _("Type client"),
        max_length=20,
        choices=TypeClient.choices,
        null=True,
        blank=True
    )


    autre_precision = models.CharField(
        _("Autre précision"),
        max_length=100,
        blank=True
    )


    photo = models.ImageField(
        _("Photo"),
        upload_to="utilisateurs/photos/",
        blank=True,
        null=True
    )


    adresse = models.TextField(
        _("Adresse"),
        blank=True
    )


    actif = models.BooleanField(
        _("Compte actif"),
        default=True
    )


    premiere_connexion = models.BooleanField(
        _("Première connexion"),
        default=False
    )


    date_creation = models.DateTimeField(
        _("Date création"),
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
                fields=[
                    "role"
                ]
            ),

            models.Index(
                fields=[
                    "role",
                    "actif"
                ]
            ),

        ]



    def __str__(self):

        return self.nom_complet



    @property
    def nom_complet(self):

        return f"{self.prenom} {self.nom}"



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
                    "Champ réservé aux clients."
                }
            )



# =====================================================
# PRODUCTEUR
# =====================================================

class Producteur(models.Model):


    utilisateur = models.OneToOneField(
        Utilisateur,
        verbose_name="Utilisateur",
        on_delete=models.CASCADE,
        related_name="producteur"
    )


    nom_exploitation = models.CharField(
        "Nom exploitation",
        max_length=150
    )


    description = models.TextField(
        "Description",
        blank=True
    )


    date_creation = models.DateField(
        "Date création",
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
        verbose_name="Utilisateur",
        on_delete=models.CASCADE,
        related_name="notifications"
    )


    titre = models.CharField(
        "Titre",
        max_length=150
    )


    message = models.TextField(
        "Message"
    )


    lu = models.BooleanField(
        "Lu",
        default=False
    )


    date = models.DateTimeField(
        "Date",
        auto_now_add=True
    )


    class Meta:

        verbose_name = "Notification"

        verbose_name_plural = "Notifications"

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
        verbose_name="Utilisateur",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="journal_activite"
    )


    action = models.CharField(
        "Action",
        max_length=100
    )


    objet = models.CharField(
        "Objet",
        max_length=150,
        blank=True
    )


    adresse_ip = models.GenericIPAddressField(
        "Adresse IP",
        null=True,
        blank=True
    )


    date = models.DateTimeField(
        "Date",
        auto_now_add=True
    )


    class Meta:

        verbose_name = "Journal activité"

        verbose_name_plural = "Journaux activités"

        ordering = [
            "-date"
        ]



    def __str__(self):

        return self.action



# =====================================================
# PARAMETRES PLATEFORME
# =====================================================

class Parametre(models.Model):


    commission_plateforme = models.DecimalField(
        "Commission plateforme (%)",
        max_digits=5,
        decimal_places=2,
        default=10,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )


    commission_livreur = models.DecimalField(
        "Commission livreur",
        max_digits=10,
        decimal_places=2,
        default=0
    )


    devise = models.CharField(
        "Devise",
        max_length=10,
        default="FCFA"
    )


    maintenance = models.BooleanField(
        "Mode maintenance",
        default=False
    )


    class Meta:

        verbose_name = "Paramètre plateforme"

        verbose_name_plural = "Paramètres plateforme"



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