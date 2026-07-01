from rest_framework import serializers
from .models import Category, Product, StockMovement


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class ProductSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(source="category.name", read_only=True)
    producteur_name = serializers.CharField(source="producteur.user.username", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "image",
            "price",
            "unit",
            "stock",
            "status",
            "is_active",
            "category",
            "category_name",
            "producteur",
            "producteur_name",
        ]


class StockMovementSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            "id",
            "product",
            "product_name",
            "movement_type",
            "quantity",
            "reason",
            "created_at",
        ]