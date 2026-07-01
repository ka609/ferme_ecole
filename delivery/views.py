from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Delivery
from .serializers import DeliverySerializer


class DeliveryViewSet(viewsets.ModelViewSet):
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Client voit ses livraisons
        if user.role == "CLIENT":
            return Delivery.objects.filter(order__client=user)

        # Livreur voit ses livraisons
        if user.role == "LIVREUR":
            return Delivery.objects.filter(livreur=user)

        # Admin / commercial / stock voient tout
        return Delivery.objects.all()