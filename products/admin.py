from django.contrib import admin
from .models import Category, Product, StockMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "producteur", "price", "stock", "status", "is_active")
    list_filter = ("status", "category", "is_active")
    search_fields = ("name", "producteur__user__username")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("product", "movement_type", "quantity", "created_at")
    list_filter = ("movement_type",)
    search_fields = ("product__name",)