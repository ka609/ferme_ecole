from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Category, Product, StockMovement
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    StockMovementSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Clients voient produits actifs seulement
        """
        user = self.request.user

        if user.role == "CLIENT":
            return Product.objects.filter(is_active=True)

        return Product.objects.all()


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all().order_by("-created_at")
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]