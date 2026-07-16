"""
catalog/serializers.py

Sérialisation du catalogue :
- Catégories
- Certifications
- Produits
- Images produits
"""


from rest_framework import serializers


from .models import (
    Categorie,
    Certification,
    Produit,
    ProduitImage,
)





# Catégorie
class CategorieSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Categorie


        fields = (
            "id",
            "nom",
            "description",
        )


        read_only_fields = (
            "id",
        )







# Certification
class CertificationSerializer(
    serializers.ModelSerializer
):

    producteur_nom = serializers.CharField(

        source="producteur.nom_exploitation",

        read_only=True,

    )


    est_active = serializers.ReadOnlyField()



    class Meta:

        model = Certification


        fields = (

            "id",

            "producteur",
            "producteur_nom",

            "type",

            "numero",

            "document",

            "date_debut",

            "date_fin",

            "statut",

            "valide_par",

            "date_validation",

            "est_active",

        )


        read_only_fields = (

            "id",

            "date_validation",

            "est_active",

        )








# Image produit
class ProduitImageSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = ProduitImage


        fields = (

            "id",

            "image",

        )


        read_only_fields = (

            "id",

        )








# Produit complet
class ProduitSerializer(
    serializers.ModelSerializer
):


    producteur_nom = serializers.CharField(

        source="producteur.nom_exploitation",

        read_only=True,

    )


    categorie_nom = serializers.CharField(

        source="categorie.nom",

        read_only=True,

    )



    images = ProduitImageSerializer(

        many=True,

        read_only=True,

    )



    note_moyenne = serializers.FloatField(

        source="moyenne_avis",

        read_only=True,

    )



    nombre_avis = serializers.IntegerField(

        source="total_avis",

        read_only=True,

    )





    class Meta:

        model = Produit



        fields = (

            "id",


            "producteur",

            "producteur_nom",



            "categorie",

            "categorie_nom",



            "nom",

            "description",



            "prix",

            "unite",

            "stock",



            "type_produit",



            "image",

            "images",



            "valide",

            "valide_par",

            "date_validation",



            "disponible",



            "date_creation",

            "date_modification",



            "note_moyenne",

            "nombre_avis",

        )



        read_only_fields = (

            "id",

            "valide_par",

            "date_validation",

            "date_creation",

            "date_modification",

            "note_moyenne",

            "nombre_avis",

        )









# Produit public
class ProduitPublicSerializer(
    serializers.ModelSerializer
):


    producteur = serializers.CharField(

        source="producteur.nom_exploitation",

        read_only=True,

    )



    categorie = serializers.CharField(

        source="categorie.nom",

        read_only=True,

    )



    images = ProduitImageSerializer(

        many=True,

        read_only=True,

    )



    note_moyenne = serializers.FloatField(

        source="moyenne_avis",

        read_only=True,

    )



    nombre_avis = serializers.IntegerField(

        source="total_avis",

        read_only=True,

    )





    class Meta:

        model = Produit



        fields = (

            "id",


            "producteur",

            "categorie",


            "nom",

            "description",


            "prix",

            "unite",

            "stock",


            "type_produit",


            "image",

            "images",

            "disponible",

            "note_moyenne",

            "nombre_avis",

        )