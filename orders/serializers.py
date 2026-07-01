from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, Payment
from products.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_name", "quantity"]


class CartSerializer(serializers.ModelSerializer):

    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "client", "items", "created_at"]


class OrderItemSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "client",
            "total_amount",
            "status",
            "payment_method",
            "delivery_address",
            "phone",
            "items",
            "created_at",
        ]


class PaymentSerializer(serializers.ModelSerializer):

    order_id = serializers.IntegerField(source="order.id", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "order_id",
            "amount",
            "transaction_id",
            "status",
            "created_at",
        ]