from django.contrib import admin
from .models import Production


@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = (
        "producteur",
        "product",
        "quantity",
        "status",
        "production_date",
        "reception_date",
    )

    list_filter = ("status", "production_date")
    search_fields = ("producteur__user__username", "product__name")