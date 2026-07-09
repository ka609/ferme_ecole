"""
community/serializers.py

Sérialisation communautaire :
- Avis
- Forum
- Formations
- Suivi des formations
"""

from rest_framework import serializers

from .models import (
    Avis,
    SujetForum,
    ReponseForum,
    Formation,
    SuiviFormation,
)


# Avis produit
class AvisSerializer(serializers.ModelSerializer):

    client_nom = serializers.CharField(
        source="client.nom_complet",
        read_only=True,
    )

    produit_nom = serializers.CharField(
        source="produit.nom",
        read_only=True,
    )

    class Meta:
        model = Avis

        fields = (
            "id",
            "produit",
            "produit_nom",
            "client",
            "client_nom",
            "note",
            "commentaire",
            "date",
        )

        read_only_fields = (
            "id",
            "client",
            "date",
        )


# Sujet forum
class SujetForumSerializer(serializers.ModelSerializer):

    auteur_nom = serializers.CharField(
        source="auteur.nom_complet",
        read_only=True,
    )

    nombre_reponses = serializers.IntegerField(
        source="reponses.count",
        read_only=True,
    )

    class Meta:
        model = SujetForum

        fields = (
            "id",
            "auteur",
            "auteur_nom",
            "titre",
            "contenu",
            "epingle",
            "ferme",
            "nombre_reponses",
            "date",
        )

        read_only_fields = (
            "id",
            "auteur",
            "date",
        )


# Réponse forum
class ReponseForumSerializer(serializers.ModelSerializer):

    auteur_nom = serializers.CharField(
        source="auteur.nom_complet",
        read_only=True,
    )

    class Meta:
        model = ReponseForum

        fields = (
            "id",
            "sujet",
            "auteur",
            "auteur_nom",
            "contenu",
            "date",
        )

        read_only_fields = (
            "id",
            "auteur",
            "date",
        )


# Formation
class FormationSerializer(serializers.ModelSerializer):

    auteur_nom = serializers.CharField(
        source="publie_par.nom_complet",
        read_only=True,
    )

    class Meta:
        model = Formation

        fields = (
            "id",
            "titre",
            "description",
            "document",
            "video",
            "publie_par",
            "auteur_nom",
            "date",
        )

        read_only_fields = (
            "id",
            "publie_par",
            "date",
        )


# Suivi formation
class SuiviFormationSerializer(serializers.ModelSerializer):

    producteur_nom = serializers.CharField(
        source="producteur.nom_exploitation",
        read_only=True,
    )

    formation_titre = serializers.CharField(
        source="formation.titre",
        read_only=True,
    )

    class Meta:
        model = SuiviFormation

        fields = (
            "id",
            "formation",
            "formation_titre",
            "producteur",
            "producteur_nom",
            "progression",
            "terminee",
            "date",
        )

        read_only_fields = (
            "id",
            "terminee",
            "date",
        )

    def validate_progression(self, value):

        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "La progression doit être comprise entre 0 et 100."
            )

        return value