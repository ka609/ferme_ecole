"""
market/views.py

Gestion :
- paniers
- commandes
- paiements
- versements
- livraisons
- commissions
- sociétés de livraison
"""


from django.db import transaction

from django.shortcuts import get_object_or_404


from rest_framework import (
    permissions,
    status,
    viewsets,
)


from rest_framework.decorators import action

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated



from accounts.models import Role

from catalog.models import Produit


from .models import (
    Panier,
    PanierArticle,
    Commande,
    Paiement,
    Versement,
    SocieteLivraison,
    Livraison,
    Commission,
    StatutLivraison,
)


from django.core.exceptions import ValidationError as DjangoValidationError


from .serializers import (
    PanierSerializer,
    AjouterPanierArticleSerializer,
    CommandeSerializer,
    CreationCommandeSerializer,
    PaiementSerializer,
    VersementSerializer,
    SocieteLivraisonSerializer,
    LivraisonSerializer,
    CommissionSerializer,
)



# =====================================================
# PERMISSIONS
# =====================================================


class IsClient(permissions.BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role == Role.CLIENT
        )



class IsProducteur(permissions.BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role == Role.PRODUCTEUR
        )



class IsLivreur(permissions.BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role == Role.LIVREUR
        )



class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role == Role.ADMIN
        )



# =====================================================
# PANIER
# =====================================================


class PanierViewSet(viewsets.ModelViewSet):

    serializer_class = PanierSerializer


    permission_classes = [
        IsClient
    ]


    def get_queryset(self):

        return Panier.objects.filter(
            client=self.request.user
        ).prefetch_related(
            "articles"
        )



    @action(
        detail=False,
        methods=["post"]
    )
    def ajouter(
        self,
        request
    ):

        serializer = AjouterPanierArticleSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )


        produit = serializer.validated_data["produit"]


        if not Produit.objects.visibles_publiquement().filter(
            id=produit.id
        ).exists():

            return Response(
                {
                    "detail": "Produit non disponible."
                },
                status=status.HTTP_400_BAD_REQUEST
            )


        if hasattr(request.user, "producteur"):

            if produit.producteur == request.user.producteur:

                return Response(
                    {
                        "detail":
                        "Un producteur ne peut pas acheter ses propres produits."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )


        panier, created = Panier.objects.get_or_create(
            client=request.user,
            producteur=produit.producteur
        )


        PanierArticle.objects.update_or_create(
            panier=panier,
            produit=produit,
            defaults={
                "quantite":
                    serializer.validated_data["quantite"],
                "prix":
                    produit.prix,
            }
        )


        return Response(
            PanierSerializer(panier).data,
            status=status.HTTP_201_CREATED
        )



# =====================================================
# ARTICLES PANIER
# =====================================================


class PanierArticleViewSet(viewsets.ModelViewSet):

    serializer_class = AjouterPanierArticleSerializer

    permission_classes = [
        IsClient
    ]


    def get_queryset(self):

        return PanierArticle.objects.filter(
            panier__client=self.request.user
        )



# =====================================================
# COMMANDES
# =====================================================


class CommandeViewSet(viewsets.ModelViewSet):

    serializer_class = CommandeSerializer


    def get_queryset(self):

        user = self.request.user


        if user.role == Role.CLIENT:

            return Commande.objects.filter(
                client=user
            )


        if user.role == Role.PRODUCTEUR:

            return Commande.objects.filter(
                producteur=user.producteur
            )


        if user.role == Role.LIVREUR:

            return Commande.objects.filter(
                livraison__livreur=user
            )


        return Commande.objects.all()



    def get_serializer_class(self):

        if self.action == "create":

            return CreationCommandeSerializer

        return CommandeSerializer



# =====================================================
# LIVRAISONS
# =====================================================


class LivraisonViewSet(viewsets.ModelViewSet):

    serializer_class = LivraisonSerializer


    def get_queryset(self):

        user = self.request.user


        if user.role == Role.LIVREUR:

            return Livraison.objects.filter(
                livreur=user
            )


        # BUG corrigé : un CLIENT n'avait aucun moyen de voir sa propre
        # livraison (queryset vide par défaut) — nécessaire pour l'écran
        # "suivi de commande" et pour confirmer_reception ci-dessous.
        if user.role == Role.CLIENT:

            return Livraison.objects.filter(
                commande__client=user
            )


        if user.role == Role.ADMIN:

            return Livraison.objects.all()


        return Livraison.objects.none()



    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsLivreur]
    )
    def disponibles(
        self,
        request
    ):
        """Pool : livraisons pas encore prises en charge par un livreur."""

        livraisons = Livraison.objects.filter(
            livreur__isnull=True,
            statut=StatutLivraison.EN_ATTENTE
        )


        return Response(
            LivraisonSerializer(
                livraisons,
                many=True
            ).data
        )



    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsLivreur]
    )
    @transaction.atomic
    def prendre(
        self,
        request,
        pk=None
    ):
        """Un livreur prend la livraison depuis le pool (premier arrivé, premier servi)."""

        livraison = get_object_or_404(
            Livraison.objects.select_for_update(),
            id=pk
        )


        try:
            livraison.prendre_en_charge(request.user)

        except DjangoValidationError as e:

            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


        return Response(
            LivraisonSerializer(livraison).data
        )



    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsLivreur]
    )
    def relacher(
        self,
        request,
        pk=None
    ):
        """Le livreur ne peut plus assurer la livraison : retour au pool."""

        livraison = get_object_or_404(
            Livraison,
            id=pk,
            livreur=request.user
        )


        try:
            livraison.relacher()

        except DjangoValidationError as e:

            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


        return Response(
            LivraisonSerializer(livraison).data
        )



    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsLivreur]
    )
    def livrer(
        self,
        request,
        pk=None
    ):
        """
        Le LIVREUR déclare avoir livré ("Commande livrée").
        Ne valide PAS la commission — voir confirmer_reception ci-dessous.
        """

        livraison = get_object_or_404(
            Livraison,
            id=pk,
            livreur=request.user
        )


        try:
            livraison.marquer_livree()

        except DjangoValidationError as e:

            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


        return Response(
            LivraisonSerializer(livraison).data
        )



    @action(
        detail=True,
        methods=["post"]
    )
    def confirmer_reception(
        self,
        request,
        pk=None
    ):
        """
        Le CLIENT confirme avoir reçu sa commande ("Commande reçue") —
        seule action qui valide la commission du livreur (voir
        Livraison.confirmer_reception -> commission.valider()).
        Un ADMIN peut confirmer à la place du client si celui-ci ne
        répond pas / refuse.
        """

        user = request.user


        if user.role == Role.CLIENT:

            livraison = get_object_or_404(
                Livraison,
                id=pk,
                commande__client=user
            )


        elif user.role == Role.ADMIN:

            livraison = get_object_or_404(
                Livraison,
                id=pk
            )


        else:

            return Response(
                {
                    "detail":
                    "Seul le client concerné ou un administrateur peut confirmer la réception."
                },
                status=status.HTTP_403_FORBIDDEN
            )


        try:
            livraison.confirmer_reception(user)

        except DjangoValidationError as e:

            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


        return Response(
            {
                "message":
                "Réception confirmée. Commission du livreur validée.",
                "livraison":
                LivraisonSerializer(livraison).data,
            }
        )



# =====================================================
# PAIEMENTS
# =====================================================


class PaiementViewSet(viewsets.ModelViewSet):
    serializer_class = PaiementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "CLIENT":
            return Paiement.objects.filter(
                commande__client=user
            )

        if user.role == "PRODUCTEUR":
            return Paiement.objects.filter(
                commande__producteur__utilisateur=user
            )

        return Paiement.objects.all()
# =====================================================
# VERSEMENTS
# =====================================================


class VersementViewSet(viewsets.ModelViewSet):

    serializer_class = VersementSerializer


    def get_queryset(self):

        user = self.request.user


        if user.role == Role.PRODUCTEUR:

            return Versement.objects.filter(
                producteur=user.producteur
            )


        if user.role == Role.ADMIN:

            return Versement.objects.all()


        return Versement.objects.none()



# =====================================================
# SOCIETES LIVRAISON
# =====================================================


class SocieteLivraisonViewSet(viewsets.ModelViewSet):

    queryset = SocieteLivraison.objects.all()

    serializer_class = SocieteLivraisonSerializer

    permission_classes = [
        IsAdmin
    ]



# =====================================================
# COMMISSIONS
# =====================================================


class CommissionViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = CommissionSerializer


    def get_queryset(self):

        user = self.request.user


        if user.role == Role.LIVREUR:

            return Commission.objects.filter(
                livreur=user
            )


        if user.role == Role.ADMIN:

            return Commission.objects.all()


        return Commission.objects.none()