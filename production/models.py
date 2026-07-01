from django.db import models
from accounts.models import Producteur
from products.models import Product


class Production(models.Model):
    """
    Production réalisée par un producteur et réceptionnée par la FERME-ÉCOLE.

    Cette production sert à alimenter le stock du produit commercialisable.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "En attente"
        RECEIVED = "RECEIVED", "Réceptionnée"
        REJECTED = "REJECTED", "Refusée"

    producteur = models.ForeignKey(
        Producteur,
        on_delete=models.CASCADE,
        related_name="productions"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="productions"
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    unit = models.CharField(
        max_length=20,
        help_text="kg, litre, sac..."
    )

    production_date = models.DateField()

    reception_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    # Qui a validé la réception (gestionnaire de stock)
    validated_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validated_productions"
    )

    observation = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-production_date"]
        verbose_name = "Production"
        verbose_name_plural = "Productions"

    def __str__(self):
        return f"{self.producteur.user.get_full_name()} - {self.product.name} ({self.quantity} {self.unit})"