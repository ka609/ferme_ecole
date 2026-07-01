from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Producteur, Notification


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        ("Rôle & Infos supplémentaires", {
            "fields": ("role", "phone", "address", "photo")
        }),
    )

    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email", "phone")


@admin.register(Producteur)
class ProducteurAdmin(admin.ModelAdmin):
    list_display = ("user", "specialite", "localisation", "actif")
    list_filter = ("actif",)
    search_fields = ("user__username", "specialite")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "receiver", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read")
    search_fields = ("title", "message", "receiver__username")