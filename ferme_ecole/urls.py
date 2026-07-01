from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Accounts
from accounts.views import UserViewSet, ProducteurViewSet, NotificationViewSet

# Products
from products.views import CategoryViewSet, ProductViewSet, StockMovementViewSet

# Production
from production.views import ProductionViewSet

# Orders
from orders.views import (
    CartViewSet,
    CartItemViewSet,
    OrderViewSet,
    OrderItemViewSet,
    PaymentViewSet,
)
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Delivery
from delivery.views import DeliveryViewSet


router = DefaultRouter()

# ================= ACCOUNTS =================
router.register(r"users", UserViewSet, basename="users")
router.register(r"producteurs", ProducteurViewSet, basename="producteurs")
router.register(r"notifications", NotificationViewSet, basename="notifications")

# ================= PRODUCTS =================
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"products", ProductViewSet, basename="products")
router.register(r"stock-movements", StockMovementViewSet, basename="stock-movements")

# ================= PRODUCTION =================
router.register(r"productions", ProductionViewSet, basename="productions")

# ================= ORDERS =================
router.register(r"carts", CartViewSet, basename="carts")
router.register(r"cart-items", CartItemViewSet, basename="cart-items")
router.register(r"orders", OrderViewSet, basename="orders")
router.register(r"order-items", OrderItemViewSet, basename="order-items")
router.register(r"payments", PaymentViewSet, basename="payments")

# ================= DELIVERY =================
router.register(r"deliveries", DeliveryViewSet, basename="deliveries")


urlpatterns = [
    path("admin/", admin.site.urls),

    # API ROOT
    path("api/", include(router.urls)),
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/verify/", TokenVerifyView.as_view(), name="token_verify"),
]