"""
accounts/serializers.py

Sérialisation :
- Utilisateur
- Producteur
- Notification
- Journal activité
- Paramètres
"""

from rest_framework import serializers

from .models import (
    Utilisateur,
    Producteur,
    Notification,
    JournalActivite,
    Parametre,
    Role,
    TypeClient,
)



# =====================================================
# UTILISATEUR
# =====================================================

class UtilisateurSerializer(serializers.ModelSerializer):


    nom_complet = serializers.ReadOnlyField()


    class Meta:

        model = Utilisateur


        fields = (

            "id",

            "username",

            "email",

            "nom",

            "prenom",

            "nom_complet",

            "telephone",

            "role",

            "type_client",

            "autre_precision",

            "photo",

            "adresse",

            "actif",

            "premiere_connexion",

            "date_creation",

        )


        read_only_fields = (

            "id",

            "role",

            "actif",

            "date_creation",

            "premiere_connexion",

        )



    def validate(self, attrs):

        role = attrs.get(
            "role",
            getattr(
                self.instance,
                "role",
                Role.CLIENT
            )
        )


        type_client = attrs.get(
            "type_client",
            getattr(
                self.instance,
                "type_client",
                None
            )
        )


        autre_precision = attrs.get(
            "autre_precision",
            getattr(
                self.instance,
                "autre_precision",
                ""
            )
        )


        if role == Role.CLIENT:


            if not type_client:

                raise serializers.ValidationError(
                    {
                        "type_client":
                        "Un client doit préciser son type."
                    }
                )


            if (
                type_client == TypeClient.AUTRE
                and not autre_precision
            ):

                raise serializers.ValidationError(
                    {
                        "autre_precision":
                        "Veuillez préciser votre activité."
                    }
                )


        return attrs

# INSCRIPTION
class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    password_confirmation = serializers.CharField(
        write_only=True,
    )


    class Meta:

        model = Utilisateur

        fields = (

            "username",

            "email",

            "password",

            "password_confirmation",

            "nom",

            "prenom",

            "telephone",

            "role",

            "type_client",

            "autre_precision",

            "adresse",

        )


    def validate(self, attrs):

        if attrs["password"] != attrs["password_confirmation"]:

            raise serializers.ValidationError(
                {
                    "password":
                    "Les mots de passe ne correspondent pas."
                }
            )


        role = attrs.get("role")


        if role not in (
            Role.CLIENT,
            Role.LIVREUR,
        ):

            raise serializers.ValidationError(
                {
                    "role":
                    "Seuls les clients et les livreurs peuvent s'inscrire."
                }
            )


        if role == Role.CLIENT:

            type_client = attrs.get("type_client")

            if not type_client:

                raise serializers.ValidationError(
                    {
                        "type_client":
                        "Veuillez choisir un type de client."
                    }
                )


            if (
                type_client == TypeClient.AUTRE
                and not attrs.get("autre_precision")
            ):

                raise serializers.ValidationError(
                    {
                        "autre_precision":
                        "Veuillez préciser votre activité."
                    }
                )

        else:

            attrs["type_client"] = None
            attrs["autre_precision"] = ""


        return attrs


    def create(self, validated_data):

        validated_data.pop(
            "password_confirmation",
        )

        role = validated_data.pop(
            "role",
        )

        user = Utilisateur.objects.create_user(

            username=validated_data.pop("username"),

            email=validated_data.pop("email"),

            password=validated_data.pop("password"),

            role=role,

            **validated_data,

        )

        return user


# =====================================================
# LOGIN
# =====================================================

class LoginSerializer(serializers.Serializer):


    username = serializers.CharField()


    password = serializers.CharField(
        write_only=True
    )



# =====================================================
# PRODUCTEUR
# =====================================================

class ProducteurSerializer(serializers.ModelSerializer):


    username = serializers.CharField(
        source="utilisateur.username",
        read_only=True
    )


    email = serializers.EmailField(
        source="utilisateur.email",
        read_only=True
    )


    class Meta:

        model = Producteur


        fields = (

            "id",

            "utilisateur",

            "username",

            "email",

            "nom_exploitation",

            "description",

            "date_creation",

        )


        read_only_fields = (

            "id",

            "date_creation",

        )



# =====================================================
# CREATION PRODUCTEUR ADMIN
# =====================================================

class ProducteurCreateSerializer(serializers.ModelSerializer):


    utilisateur = serializers.PrimaryKeyRelatedField(
        queryset=Utilisateur.objects.filter(
            role=Role.PRODUCTEUR
        )
    )



    class Meta:

        model = Producteur


        fields = (

            "utilisateur",

            "nom_exploitation",

            "description",

        )



# =====================================================
# NOTIFICATION
# =====================================================

class NotificationSerializer(serializers.ModelSerializer):


    class Meta:

        model = Notification


        fields = (

            "id",

            "titre",

            "message",

            "lu",

            "date",

        )


        read_only_fields = (

            "id",

            "date",

        )



# =====================================================
# JOURNAL ACTIVITE
# =====================================================

class JournalActiviteSerializer(serializers.ModelSerializer):


    utilisateur_username = serializers.CharField(
        source="utilisateur.username",
        read_only=True
    )


    class Meta:

        model = JournalActivite


        fields = (

            "id",

            "utilisateur",

            "utilisateur_username",

            "action",

            "objet",

            "adresse_ip",

            "date",

        )


        read_only_fields = (

            "id",

            "date",

        )



# =====================================================
# PARAMETRES
# =====================================================

class ParametreSerializer(serializers.ModelSerializer):


    class Meta:

        model = Parametre


        fields = (

            "id",

            "commission_plateforme",

            "commission_livreur",

            "devise",

            "maintenance",

        )


        read_only_fields = (

            "id",

        )