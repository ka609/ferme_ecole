from rest_framework import serializers
from .models import Delivery


class DeliverySerializer(serializers.ModelSerializer):

    order_id = serializers.IntegerField(source="order.id", read_only=True)
    livreur_name = serializers.CharField(source="livreur.username", read_only=True)

    class Meta:
        model = Delivery
        fields = [
            "id",
            "order",
            "order_id",
            "livreur",
            "livreur_name",
            "delivery_address",
            "client_phone",
            "status",
            "picked_at",
            "delivered_at",
            "delivery_note",
            "created_at",
        ]