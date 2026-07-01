from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Producteur, Notification

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "phone",
            "address",
        ]


class ProducteurSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Producteur
        fields = [
            "id",
            "user",
            "specialite",
            "localisation",
            "actif",
        ]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "is_read",
            "created_at",
        ]