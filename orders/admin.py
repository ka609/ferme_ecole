from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, Payment


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("client", "created_at")
    search_fields = ("client__username",)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity")
    search_fields = ("product__name",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "total_amount",
        "status",
        "payment_method",
        "created_at",
    )

    list_filter = ("status", "payment_method")
    search_fields = ("client__username",)
    inlines = [OrderItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "amount", "status", "created_at")
    list_filter = ("status",)