"""
accounts/views.py

Gestion :
- inscription
- connexion JWT
- profil utilisateur
- utilisateurs
- producteurs
- notifications
- journal d'activité
- paramètres
"""

from django.contrib.auth import authenticate

from rest_framework import generics, permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    Utilisateur,
    Producteur,
    Notification,
    JournalActivite,
    Parametre,
)
from catalog.models import Produit
from market.models import Commande

from .serializers import (
    UtilisateurSerializer,
    RegisterSerializer,
    LoginSerializer,
    ProducteurSerializer,
    ProducteurCreateSerializer,
    NotificationSerializer,
    JournalActiviteSerializer,
    ParametreSerializer,
)


# =====================================================
# INSCRIPTION
# =====================================================

class RegisterView(generics.CreateAPIView):

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):

        user = serializer.save()

        JournalActivite.objects.create(
            utilisateur=user,
            action="inscription",
            objet=f"Utilisateur#{user.id}",
        )


# =====================================================
# CONNEXION
# =====================================================

class LoginView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request):

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )

        if not user:

            return Response(
                {
                    "detail": "Nom utilisateur ou mot de passe incorrect."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:

            return Response(
                {
                    "detail": "Compte désactivé."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)

        JournalActivite.objects.create(
            utilisateur=user,
            action="connexion",
        )

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UtilisateurSerializer(user).data,
            }
        )


# =====================================================
# PROFIL
# =====================================================

class ProfileView(generics.RetrieveUpdateAPIView):

    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):

        user = serializer.save()

        JournalActivite.objects.create(
            utilisateur=user,
            action="modification_profil",
        )


# =====================================================
# UTILISATEURS
# =====================================================

class UtilisateurViewSet(viewsets.ModelViewSet):

    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.IsAdminUser]


# =====================================================
# PRODUCTEURS
# =====================================================

class ProducteurViewSet(viewsets.ModelViewSet):

    queryset = Producteur.objects.select_related("utilisateur")
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):

        if self.action in ["create", "update", "partial_update"]:
            return ProducteurCreateSerializer

        return ProducteurSerializer

    def get_permissions(self):

        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            return [permissions.IsAdminUser()]

        return [permissions.AllowAny()]


# =====================================================
# NOTIFICATIONS
# =====================================================

class NotificationViewSet(viewsets.ModelViewSet):

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        return Notification.objects.filter(
            utilisateur=self.request.user
        )

    @action(
        detail=True,
        methods=["patch"],
    )
    def read(self, request, pk=None):

        notification = self.get_object()

        notification.lu = True
        notification.save()

        return Response(
            {
                "message": "Notification marquée comme lue."
            }
        )


# =====================================================
# JOURNAL D'ACTIVITE
# =====================================================

class JournalActiviteViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = JournalActivite.objects.select_related(
        "utilisateur"
    )

    serializer_class = JournalActiviteSerializer
    permission_classes = [permissions.IsAdminUser]


# =====================================================
# PARAMETRES
# =====================================================

class ParametreViewSet(viewsets.ModelViewSet):

    queryset = Parametre.objects.all()
    serializer_class = ParametreSerializer
    permission_classes = [permissions.IsAdminUser]

    # =====================================================
    # STATISTIQUES PRODUCTEUR
    # =====================================================

class ProducteurStatistiqueViewSet(viewsets.ViewSet):

    permission_classes = [
        permissions.IsAuthenticated
        ]

    def list(self, request):

            try:
                producteur = Producteur.objects.get(
                    utilisateur=request.user
                )

            except Producteur.DoesNotExist:

                return Response(
                    {
                        "detail": "Profil producteur introuvable."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            produits = Produit.objects.filter(
                producteur=producteur
            )

            commandes = Commande.objects.filter(
                lignes__produit__producteur=producteur
            ).distinct()

            data = {

                "nombre_produits":
                    produits.count(),

                "produits_valides":
                    produits.filter(
                        valide=True
                    ).count(),

                "produits_disponibles":
                    produits.filter(
                        disponible=True
                    ).count(),

                "stock_total":
                    sum(
                        produit.stock
                        for produit in produits
                    ),

                "nombre_commandes":
                    commandes.count(),

            }

            return Response(data)