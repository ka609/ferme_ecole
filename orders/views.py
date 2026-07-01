from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Cart, CartItem, Order, OrderItem, Payment
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    OrderSerializer,
    OrderItemSerializer,
    PaymentSerializer
)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(client=self.request.user)


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # client voit ses commandes
        if user.role == "CLIENT":
            return Order.objects.filter(client=user)

        # admin/gestionnaire voient tout
        return Order.objects.all()


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]