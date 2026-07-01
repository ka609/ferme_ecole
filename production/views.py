from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Production
from .serializers import ProductionSerializer


class ProductionViewSet(viewsets.ModelViewSet):
    queryset = Production.objects.all().order_by("-created_at")
    serializer_class = ProductionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Producteur voit uniquement ses productions
        if hasattr(user, "producteur_profile"):
            return Production.objects.filter(producteur=user.producteur_profile)

        return Production.objects.all()