from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Utilisateur


class UtilisateurCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = Utilisateur
        fields = (
            "username",
            "nom",
            "prenom",
            "email",
            "telephone",
            "role",
            "type_client",
            "autre_precision",
        )


class UtilisateurChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = Utilisateur
        fields = "__all__"