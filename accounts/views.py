from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from .models import Producteur, Notification
from .serializers import UserSerializer, ProducteurSerializer, NotificationSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    Admin only (gestion utilisateurs)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class ProducteurViewSet(viewsets.ModelViewSet):
    """
    Gestion des producteurs (créés par admin)
    """
    queryset = Producteur.objects.all()
    serializer_class = ProducteurSerializer
    permission_classes = [IsAuthenticated]


class NotificationViewSet(viewsets.ModelViewSet):
    """
    Notifications envoyées à tous les acteurs
    """
    queryset = Notification.objects.all().order_by("-created_at")
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(receiver=user).order_by("-created_at")