from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Modèle utilisateur principal.
    Tous les acteurs de la plateforme utilisent ce modèle.
    """

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrateur"
        CLIENT = "CLIENT", "Client"
        PRODUCTEUR = "PRODUCTEUR", "Producteur"
        STOCK = "STOCK", "Gestionnaire de stock"
        COMMERCIAL = "COMMERCIAL", "Gestionnaire commercial"
        LIVREUR = "LIVREUR", "Livreur"

    role = models.CharField(
        max_length=20,
        choices=Role.choices
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True,
        null=True
    )

    photo = models.ImageField(
        upload_to="users/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["username"]
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"


class Producteur(models.Model):
    """
    Informations complémentaires d'un producteur.
    Le compte utilisateur est créé par l'administrateur.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="producteur"
    )

    specialite = models.CharField(
        max_length=150,
        help_text="Ex : Maraîchage, Apiculture, Céréales..."
    )

    localisation = models.CharField(
        max_length=255
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    actif = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__first_name"]
        verbose_name = "Producteur"
        verbose_name_plural = "Producteurs"

    def __str__(self):
        return self.user.get_full_name()


class Notification(models.Model):
    """
    Notifications envoyées aux utilisateurs.
    """

    class NotificationType(models.TextChoices):
        GENERAL = "GENERAL", "Générale"
        STOCK = "STOCK", "Stock"
        PRODUCTION = "PRODUCTION", "Production"
        ORDER = "ORDER", "Commande"
        PAYMENT = "PAYMENT", "Paiement"
        DELIVERY = "DELIVERY", "Livraison"

    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications_sent"
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications_received"
    )

    title = models.CharField(max_length=200)

    message = models.TextField()

    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.title} -> {self.receiver.username}"