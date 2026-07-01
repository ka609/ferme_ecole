from rest_framework.permissions import BasePermission


# =========================
# 🔑 ADMIN UNIQUEMENT
# =========================
class IsAdminUser(BasePermission):
    """
    Accès réservé au superuser Django (administrateur système)
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser


# =========================
# 💼 GESTIONNAIRE STOCK
# =========================
class IsStockManager(BasePermission):
    """
    Gestionnaire de stock (via role)
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "STOCK"
        )


# =========================
# 📊 GESTIONNAIRE COMMERCIAL
# =========================
class IsCommercialManager(BasePermission):
    """
    Supervision des ventes et commandes
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "COMMERCIAL"
        )


# =========================
# 🚚 LIVREUR
# =========================
class IsLivreur(BasePermission):
    """
    Accès livreur (admin Django)
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "LIVREUR"
        )


# =========================
# 👤 CLIENT
# =========================
class IsClient(BasePermission):
    """
    Accès client Flutter
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "CLIENT"
        )


# =========================
# 🌱 PRODUCTEUR
# =========================
class IsProducteur(BasePermission):
    """
    Accès producteur Flutter
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "PRODUCTEUR"
        )


# =========================
# 🔓 MIX ROLE (ADMIN + COMMERCIAL + STOCK)
# =========================
class IsStaffInternal(BasePermission):
    """
    Personnel interne de la FERME-ÉCOLE
    (admin Django hors superuser logique métier)
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["STOCK", "COMMERCIAL", "LIVREUR"]
        )