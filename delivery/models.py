from django.db import models
from accounts.models import User
from orders.models import Order


class Delivery(models.Model):
    """
    Livraison des commandes aux clients.
    Gérée par le livreur via l'admin Django.
    Visible aussi par le client et les gestionnaires.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "En attente"
        ASSIGNED = "ASSIGNED", "Assignée"
        PICKED = "PICKED", "Récupérée"
        IN_TRANSIT = "IN_TRANSIT", "En cours de livraison"
        DELIVERED = "DELIVERED", "Livrée"
        FAILED = "FAILED", "Échec de livraison"
        CANCELLED = "CANCELLED", "Annulée"

    # Commande liée
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="delivery"
    )

    # Livreurs (connecté via admin Django)
    livreur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deliveries"
    )

    # Adresse de livraison (copie de la commande pour sécurité)
    delivery_address = models.TextField()

    # Contact client (utile pour le livreur)
    client_phone = models.CharField(max_length=20)

    # Statut de livraison
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    # Heure de départ
    picked_at = models.DateTimeField(null=True, blank=True)

    # Heure de livraison
    delivered_at = models.DateTimeField(null=True, blank=True)

    # Notes du livreur
    delivery_note = models.TextField(blank=True, null=True)

    # Coordonnées optionnelles (future évolution GPS)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Livraison"
        verbose_name_plural = "Livraisons"

    def __str__(self):
        return f"Livraison commande #{self.order.id} - {self.status}"