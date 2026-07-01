from django.db import models
from accounts.models import User
from products.models import Product


class Cart(models.Model):
    """
    Panier du client avant commande.
    """

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="carts"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Panier de {self.client.username}"


class CartItem(models.Model):
    """
    Produit dans le panier.
    """

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Order(models.Model):
    """
    Commande passée par un client.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "En attente"
        CONFIRMED = "CONFIRMED", "Confirmée"
        PAID = "PAID", "Payée"
        PREPARING = "PREPARING", "En préparation"
        SHIPPED = "SHIPPED", "Expédiée"
        DELIVERED = "DELIVERED", "Livrée"
        CANCELLED = "CANCELLED", "Annulée"

    class PaymentMethod(models.TextChoices):
        MOBILE_MONEY = "MOBILE_MONEY", "Mobile Money"
        CASH = "CASH", "Paiement à la livraison"

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices
    )

    delivery_address = models.TextField()

    phone = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Commande #{self.id} - {self.client.username}"


class OrderItem(models.Model):
    """
    Détail des produits dans une commande.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Payment(models.Model):
    """
    Paiement d'une commande.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "En attente"
        SUCCESS = "SUCCESS", "Réussi"
        FAILED = "FAILED", "Échoué"

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Paiement commande #{self.order.id}"