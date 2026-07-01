from rest_framework import serializers
from .models import Production


class ProductionSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(source="product.name", read_only=True)
    producteur_name = serializers.CharField(source="producteur.user.username", read_only=True)

    class Meta:
        model = Production
        fields = [
            "id",
            "producteur",
            "producteur_name",
            "product",
            "product_name",
            "quantity",
            "unit",
            "production_date",
            "reception_date",
            "status",
            "observation",
        ]