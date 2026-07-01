from django.db import models
from accounts.models import Producteur


class Category(models.Model):
    """
    Catégories des produits.
    Exemple : Légumes, Fruits, Miel, Céréales...
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Fiche produit publiée sur la plateforme.
    Créée par le gestionnaire de stock.
    """

    class Unit(models.TextChoices):
        KG = "kg", "Kilogramme"
        G = "g", "Gramme"
        L = "l", "Litre"
        ML = "ml", "Millilitre"
        SAC = "sac", "Sac"
        UNITE = "unite", "Unité"

    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Disponible"
        OUT_OF_STOCK = "OUT_OF_STOCK", "Rupture de stock"

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )

    producteur = models.ForeignKey(
        Producteur,
        on_delete=models.PROTECT,
        related_name="products"
    )

    name = models.CharField(max_length=150)
    description = models.TextField()

    image = models.ImageField(upload_to="products/")

    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, choices=Unit.choices, default=Unit.KG)

    # ⚠️ stock peut exister mais doit être mis à jour automatiquement
    stock = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Produit"
        verbose_name_plural = "Produits"

    def __str__(self):
        return self.name


class StockMovement(models.Model):
    """
    Historique des mouvements de stock.
    Permet de tracer toutes les entrées et sorties.
    """

    class MovementType(models.TextChoices):
        ENTRY = "ENTRY", "Entrée"
        EXIT = "EXIT", "Sortie"

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stock_movements"
    )

    movement_type = models.CharField(
        max_length=10,
        choices=MovementType.choices
    )

    quantity = models.PositiveIntegerField()

    reason = models.CharField(
        max_length=255,
        help_text="Production, Vente, Correction, Perte..."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"

    def __str__(self):
        return f"{self.product.name} - {self.movement_type} ({self.quantity})"