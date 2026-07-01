from django.contrib import admin
from .models import Delivery


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "livreur",
        "status",
        "delivery_address",
        "created_at",
    )

    list_filter = ("status",)
    search_fields = ("order__id", "livreur__username", "client_phone")