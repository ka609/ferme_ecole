# catalog/views.py

# Imports Django
from django.utils import timezone

# Imports DRF
from rest_framework import (
    permissions,
    status,
    viewsets
)

from rest_framework.decorators import action
from rest_framework.response import Response


# Models
from .models import (
    Categorie,
    Certification,
    Produit,
    ProduitImage,
)


# Serializers
from .serializers import (
    CategorieSerializer,
    CertificationSerializer,
    ProduitSerializer,
    ProduitPublicSerializer,
    ProduitImageSerializer,
)


from accounts.models import Role


# Permission producteur
class IsProducteur(
    permissions.BasePermission
):

    def has_permission(
        self,
        request,
        view
    ):

        return (
            request.user.is_authenticated
            and request.user.role == Role.PRODUCTEUR
        )


# Permission admin
class IsAdmin(
    permissions.BasePermission
):

    def has_permission(
        self,
        request,
        view
    ):

        return (
            request.user.is_authenticated
            and request.user.role == Role.ADMIN
        )


# Gestion catégories
class CategorieViewSet(
    viewsets.ModelViewSet
):

    queryset = Categorie.objects.all()

    serializer_class = CategorieSerializer


    def get_permissions(self):

        if self.action in [
            "list",
            "retrieve"
        ]:
            return [
                permissions.AllowAny()
            ]

        if self.action in [
            "create",
            "update",
            "partial_update"
        ]:
            return [
                permissions.IsAuthenticated()
            ]

        return [
            IsAdmin()
        ]


# Gestion produits
class ProduitViewSet(
    viewsets.ModelViewSet
):

    queryset = Produit.objects.all()


    def get_serializer_class(self):

        if self.action in [
            "catalogue",
            "retrieve"
        ]:
            return ProduitPublicSerializer

        return ProduitSerializer



    def get_permissions(self):

        if self.action in [
            "catalogue",
            "retrieve"
        ]:
            return [
                permissions.AllowAny()
            ]

        if self.action == "validation":
            return [
                IsAdmin()
            ]

        return [
            IsProducteur()
        ]


    # Catalogue public
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[
            permissions.AllowAny
        ]
    )
    def catalogue(
        self,
        request
    ):

        produits = Produit.objects.visibles_publiquement()

        serializer = ProduitPublicSerializer(
            produits,
            many=True
        )

        return Response(
            serializer.data
        )


    # Produits du producteur
    @action(
        detail=False,
        methods=["get"]
    )
    def mes_produits(
        self,
        request
    ):

        produits = Produit.objects.filter(
            producteur__utilisateur=request.user
        )

        serializer = ProduitSerializer(
            produits,
            many=True
        )

        return Response(
            serializer.data
        )


    # Création produit
    def perform_create(
        self,
        serializer
    ):

        serializer.save(
            producteur=self.request.user.producteur
        )


    # Filtrage produits
    def get_queryset(self):

        if (
            self.request.user.is_authenticated
            and self.request.user.role == Role.PRODUCTEUR
        ):

            return Produit.objects.filter(
                producteur__utilisateur=self.request.user
            )

        return Produit.objects.all()


    # Mise à jour produit
    def perform_update(
        self,
        serializer
    ):

        serializer.save(
            valide=False,
            valide_par=None,
            date_validation=None
        )


    # Validation produit
    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[
            IsAdmin
        ]
    )
    def validation(
        self,
        request,
        pk=None
    ):

        produit = self.get_object()

        valide = request.data.get("valide")

        produit.valide = bool(valide)

        if produit.valide:

            produit.valide_par = request.user
            produit.date_validation = timezone.now()

        else:

            produit.valide_par = None
            produit.date_validation = None

        produit.save()

        return Response(
            ProduitSerializer(produit).data
        )


# Gestion certifications
class CertificationViewSet(
    viewsets.ModelViewSet
):

    queryset = Certification.objects.all()

    serializer_class = CertificationSerializer

    permission_classes = [
        IsAdmin
    ]


# Gestion images
class ProduitImageViewSet(
    viewsets.ModelViewSet
):

    queryset = ProduitImage.objects.all()

    serializer_class = ProduitImageSerializer

    permission_classes = [
        IsProducteur
    ]


    # Ajout image
    def perform_create(
        self,
        serializer
    ):

        produit_id = self.request.data.get(
            "produit"
        )

        produit = Produit.objects.get(
            id=produit_id,
            producteur__utilisateur=self.request.user
        )

        serializer.save(
            produit=produit
        )