"""
community/views.py

Gestion communautaire :
- Avis produits
- Forum
- Formations
- Suivi formations producteurs
"""


from rest_framework import (
    permissions,
    serializers,
    viewsets
)

from rest_framework.response import Response


from .models import (
    Avis,
    SujetForum,
    ReponseForum,
    Formation,
    SuiviFormation,
)


from .serializers import (
    AvisSerializer,
    SujetForumSerializer,
    ReponseForumSerializer,
    FormationSerializer,
    SuiviFormationSerializer,
)


from accounts.models import Role



# =====================================================
# PERMISSIONS
# =====================================================


class IsAdmin(permissions.BasePermission):

    def has_permission(
        self,
        request,
        view
    ):

        return (
            request.user.is_authenticated
            and request.user.role == Role.ADMIN
        )



class IsProducteur(permissions.BasePermission):

    def has_permission(
        self,
        request,
        view
    ):

        return (
            request.user.is_authenticated
            and request.user.role == Role.PRODUCTEUR
        )



# =====================================================
# AVIS PRODUITS
# =====================================================


class AvisViewSet(viewsets.ModelViewSet):

    serializer_class = AvisSerializer


    def get_queryset(self):

        return Avis.objects.select_related(
            "client",
            "produit"
        )


    def get_permissions(self):

        if self.action in [
            "list",
            "retrieve"
        ]:

            return [
                permissions.AllowAny()
            ]

        return [
            permissions.IsAuthenticated()
        ]



    def perform_create(
        self,
        serializer
    ):

        user = self.request.user


        if user.role != Role.CLIENT:

            raise serializers.ValidationError(
                "Seuls les clients peuvent publier un avis."
            )


        produit = serializer.validated_data["produit"]


        from market.models import LigneCommande


        achat = LigneCommande.objects.filter(
            commande__client=user,
            produit=produit,
            commande__statut="LIVREE"
        ).exists()



        if not achat:

            raise serializers.ValidationError(
                "Vous devez avoir acheté ce produit avant de publier un avis."
            )



        if produit.producteur.utilisateur == user:

            raise serializers.ValidationError(
                "Un producteur ne peut pas noter son propre produit."
            )



        serializer.save(
            client=user
        )



    def perform_update(
        self,
        serializer
    ):

        if serializer.instance.client != self.request.user:

            raise serializers.ValidationError(
                "Vous ne pouvez pas modifier cet avis."
            )


        serializer.save()



    def perform_destroy(
        self,
        instance
    ):

        if instance.client != self.request.user:

            raise serializers.ValidationError(
                "Vous ne pouvez pas supprimer cet avis."
            )


        instance.delete()



# =====================================================
# FORUM
# =====================================================


class SujetForumViewSet(viewsets.ModelViewSet):

    queryset = SujetForum.objects.select_related(
        "auteur"
    )

    serializer_class = SujetForumSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]


    def perform_create(
        self,
        serializer
    ):

        serializer.save(
            auteur=self.request.user
        )



class ReponseForumViewSet(viewsets.ModelViewSet):

    serializer_class = ReponseForumSerializer


    def get_permissions(self):

        if self.action in [
            "list",
            "retrieve"
        ]:

            return [
                permissions.AllowAny()
            ]

        return [
            permissions.IsAuthenticated()
        ]



    def get_queryset(self):

        sujet_id = self.request.query_params.get(
            "sujet"
        )


        queryset = ReponseForum.objects.all()


        if sujet_id:

            queryset = queryset.filter(
                sujet_id=sujet_id
            )


        return queryset



    def perform_create(
        self,
        serializer
    ):

        serializer.save(
            auteur=self.request.user
        )



# =====================================================
# FORMATIONS
# =====================================================


class FormationViewSet(viewsets.ModelViewSet):

    queryset = Formation.objects.select_related(
        "publie_par"
    )

    serializer_class = FormationSerializer



    def get_permissions(self):

        if self.action in [
            "list",
            "retrieve"
        ]:

            return [
                permissions.AllowAny()
            ]


        return [
            IsAdmin()
        ]



    def perform_create(
        self,
        serializer
    ):

        serializer.save(
            publie_par=self.request.user
        )



# =====================================================
# SUIVI FORMATION PRODUCTEUR
# =====================================================


class SuiviFormationViewSet(viewsets.ModelViewSet):

    serializer_class = SuiviFormationSerializer

    permission_classes = [
        IsProducteur
    ]



    http_method_names = [
        "get",
        "put",
        "patch"
    ]



    def get_queryset(self):

        return SuiviFormation.objects.filter(
            producteur=self.request.user.producteur
        )



    def perform_update(
        self,
        serializer
    ):

        progression = serializer.validated_data.get(
            "progression",
            0
        )


        serializer.save(
            terminee=(progression == 100)
        )