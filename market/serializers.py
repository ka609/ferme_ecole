# market/serializers.py

from django.db import transaction
from rest_framework import serializers
from catalog.models import Produit
from django.core.validators import MinValueValidator

from .models import (
    Panier,
    PanierArticle,
    Commande,
    LigneCommande,
    Paiement,
    Versement,
    SocieteLivraison,
    Livraison,
    Commission,
)


class PanierArticleSerializer(serializers.ModelSerializer):

    produit_nom = serializers.CharField(
        source="produit.nom",
        read_only=True
    )


    sous_total = serializers.SerializerMethodField()


    class Meta:

        model = PanierArticle

        fields = [
            "id",
            "produit",
            "produit_nom",
            "quantite",
            "prix",
            "sous_total",
        ]


        read_only_fields = [
            "id",
            "prix",
            "sous_total",
        ]


    def get_sous_total(
        self,
        obj
    ):

        return obj.prix * obj.quantite


class PanierSerializer(serializers.ModelSerializer):
    articles = PanierArticleSerializer(
        many=True,
        read_only=True
    )

    producteur_nom = serializers.CharField(
        source="producteur.nom_exploitation",
        read_only=True
    )

    class Meta:
        model = Panier
        fields = [
            "id",
            "client",
            "producteur",
            "producteur_nom",
            "articles",
            "date_creation",
        ]
        read_only_fields = [
            "client",
            "producteur",
            "date_creation",
        ]


class AjouterPanierArticleSerializer(serializers.ModelSerializer):

    class Meta:

        model = PanierArticle


        fields = [
            "produit",
            "quantite",
        ]



    def validate(
        self,
        attrs
    ):

        panier = self.context.get(
            "panier"
        )


        produit = attrs["produit"]



        if panier and not panier.peut_ajouter(produit):

            raise serializers.ValidationError(
                "Un panier ne peut contenir que les produits d'un seul producteur."
            )


        return attrs



    def create(
        self,
        validated_data
    ):

        produit = validated_data["produit"]


        validated_data["prix"] = produit.prix


        return super().create(
            validated_data
        )
class LigneCommandeSerializer(serializers.ModelSerializer):

    produit_nom = serializers.CharField(
        source="produit.nom",
        read_only=True
    )


    sous_total = serializers.SerializerMethodField()


    class Meta:

        model = LigneCommande

        fields = [
            "id",
            "produit",
            "produit_nom",
            "quantite",
            "prix",
            "sous_total",
        ]


        read_only_fields = [
            "id",
            "prix",
            "sous_total",
        ]


    def get_sous_total(self, obj):

        return obj.prix * obj.quantite





class CommandeSerializer(serializers.ModelSerializer):

    lignes = LigneCommandeSerializer(
        many=True,
        read_only=True
    )


    client_nom = serializers.CharField(
        source="client.nom_complet",
        read_only=True
    )


    producteur_nom = serializers.CharField(
        source="producteur.nom_exploitation",
        read_only=True
    )



    class Meta:

        model = Commande

        fields = [
            "id",
            "numero",
            "client",
            "client_nom",
            "producteur",
            "producteur_nom",
            "livreur",
            "adresse_livraison",
            "montant_total",
            "statut",
            "date_commande",
            "lignes",
        ]


        read_only_fields = [
            "id",
            "numero",
            "client",
            "livreur",
            "montant_total",
            "date_commande",
        ]







class CreationLigneCommandeSerializer(serializers.Serializer):

    produit = serializers.PrimaryKeyRelatedField(

        queryset=Produit.objects.all()

    )


    quantite = serializers.IntegerField(

        validators=[
            MinValueValidator(1)
        ]

    )







class CreationCommandeSerializer(serializers.ModelSerializer):

    lignes = CreationLigneCommandeSerializer(

        many=True

    )



    class Meta:

        model = Commande

        fields = [

            "producteur",

            "adresse_livraison",

            "lignes",

        ]



    def validate(self, attrs):

        producteur = attrs["producteur"]


        for ligne in attrs["lignes"]:

            produit = ligne["produit"]


            if produit.producteur != producteur:

                raise serializers.ValidationError(

                    "Tous les produits doivent appartenir au même producteur."

                )


        return attrs





    @transaction.atomic
    def create(self, validated_data):

        user = self.context["request"].user


        lignes_data = validated_data.pop(
            "lignes"
        )


        commande = Commande.objects.create(

            client=user,

            **validated_data

        )


        montant_total = 0



        for ligne in lignes_data:

            produit = ligne["produit"]

            quantite = ligne["quantite"]



            LigneCommande.objects.create(

                commande=commande,

                produit=produit,

                quantite=quantite,

                prix=produit.prix,

            )


            montant_total += produit.prix * quantite



        commande.montant_total = montant_total

        commande.save()



        Livraison.objects.create(

            commande=commande

        )



        return commande


class PaiementSerializer(serializers.ModelSerializer):
    commande_numero = serializers.CharField(
        source="commande.numero",
        read_only=True
    )

    class Meta:
        model = Paiement
        fields = [
            "id",
            "commande",
            "commande_numero",
            "montant",
            "moyen",
            "reference",
            "statut",
            "date_paiement",
            "date_creation",
        ]

        read_only_fields = [
            "statut",
            "date_paiement",
            "date_creation",
        ]


class VersementSerializer(serializers.ModelSerializer):
    producteur_nom = serializers.CharField(
        source="producteur.nom_exploitation",
        read_only=True
    )

    commande_numero = serializers.CharField(
        source="commande.numero",
        read_only=True
    )

    class Meta:
        model = Versement
        fields = [
            "id",
            "producteur",
            "producteur_nom",
            "commande",
            "commande_numero",
            "montant",
            "commission_plateforme",
            "montant_net",
            "statut",
            "date",
            "date_versement",
        ]

        read_only_fields = [
            "montant_net",
            "date",
            "date_versement",
        ]


class SocieteLivraisonSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocieteLivraison
        fields = [
            "id",
            "nom",
            "responsable",
            "telephone",
            "email",
            "adresse",
            "actif",
        ]


class LivraisonSerializer(serializers.ModelSerializer):
    commande_numero = serializers.CharField(
        source="commande.numero",
        read_only=True,
    )

    client_nom = serializers.CharField(
        source="commande.client.nom_complet",
        read_only=True,
    )

    client_telephone = serializers.CharField(
        source="commande.client.telephone",
        read_only=True,
    )

    adresse_livraison = serializers.CharField(
        source="commande.adresse_livraison",
        read_only=True,
    )

    montant_total = serializers.DecimalField(
        source="commande.montant_total",
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    livreur_nom = serializers.CharField(
        source="livreur.nom_complet",
        read_only=True,
    )

    class Meta:
        model = Livraison
        fields = [
            "id",
            "commande",
            "commande_numero",
            "client_nom",
            "client_telephone",
            "adresse_livraison",
            "montant_total",
            "livreur",
            "livreur_nom",
            "societe",
            "statut",
            "date_prise",
            "date_livraison",
            "confirmee_par",
            "date_confirmation",
        ]

class CommissionSerializer(serializers.ModelSerializer):
    livreur_nom = serializers.CharField(
        source="livreur.nom_complet",
        read_only=True
    )

    class Meta:
        model = Commission

        fields = [
            "id",
            "livraison",
            "livreur",
            "livreur_nom",
            "montant",
            "statut",
        ]

        read_only_fields = [
            "montant",
            "statut",
        ]