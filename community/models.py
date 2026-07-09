"""
community/models.py

Avis sur les produits, forum ouvert à tous les utilisateurs actifs,
et espace de formation destiné aux producteurs.
"""
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Avis(models.Model):
    """Un client ne peut laisser qu'un seul avis par produit (contrainte unique)."""
    produit = models.ForeignKey("catalog.Produit", on_delete=models.CASCADE, related_name="avis")
    client = models.ForeignKey(
        "accounts.Utilisateur", on_delete=models.CASCADE, related_name="avis",
        limit_choices_to={"role": "CLIENT"},
    )
    note = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    commentaire = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(fields=["produit", "client"], name="un_avis_par_client_et_produit"),
        ]
        indexes = [models.Index(fields=["produit", "-date"], name="idx_avis_produit_date")]

    def __str__(self):
        return f"{self.note}/5 - {self.produit.nom} par {self.client}"

    def clean(self):
        if self.client_id and self.client.role != "CLIENT":
            raise ValidationError({"client": "Seul un compte CLIENT peut laisser un avis."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class SujetForum(models.Model):
    """Ouvert à tous les utilisateurs actifs, quel que soit leur rôle."""
    auteur = models.ForeignKey("accounts.Utilisateur", on_delete=models.CASCADE, related_name="sujets_forum")
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    epingle = models.BooleanField(default=False, help_text="Mis en avant par l'administrateur.")
    ferme = models.BooleanField(default=False, help_text="Fermé aux nouvelles réponses par l'administrateur.")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sujet du forum"
        verbose_name_plural = "Sujets du forum"
        ordering = ["-epingle", "-date"]
        indexes = [models.Index(fields=["-epingle", "-date"], name="idx_sujet_epingle_date")]

    def __str__(self):
        return self.titre


class ReponseForum(models.Model):
    sujet = models.ForeignKey(SujetForum, on_delete=models.CASCADE, related_name="reponses")
    auteur = models.ForeignKey("accounts.Utilisateur", on_delete=models.CASCADE, related_name="reponses_forum")
    contenu = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Réponse du forum"
        verbose_name_plural = "Réponses du forum"
        ordering = ["date"]
        indexes = [models.Index(fields=["sujet", "date"], name="idx_reponse_sujet_date")]

    def __str__(self):
        return f"Réponse de {self.auteur} sur {self.sujet.titre}"

    def clean(self):
        if self.sujet_id and self.sujet.ferme:
            raise ValidationError("Ce sujet est fermé : impossible d'y répondre.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Formation(models.Model):
    """Publiée exclusivement par l'Administrateur."""
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    document = models.FileField(upload_to="formations/documents/", blank=True, null=True)
    video = models.URLField(blank=True, help_text="Lien externe (YouTube, etc.) si applicable.")
    publie_par = models.ForeignKey(
        "accounts.Utilisateur", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="formations_publiees",
        limit_choices_to={"role": "ADMIN"},
    )
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Formation"
        verbose_name_plural = "Formations"
        ordering = ["-date"]

    def __str__(self):
        return self.titre


class SuiviFormation(models.Model):
    """Suivi de la progression d'un producteur sur une formation (statistiques de consultation admin)."""
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name="suivis")
    producteur = models.ForeignKey(
        "accounts.Producteur", on_delete=models.CASCADE, related_name="suivis_formation"
    )
    progression = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Pourcentage de progression (0-100)."
    )
    terminee = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Suivi de formation"
        verbose_name_plural = "Suivis de formation"
        constraints = [
            models.UniqueConstraint(fields=["formation", "producteur"], name="un_suivi_par_producteur_et_formation"),
        ]
        indexes = [models.Index(fields=["producteur", "terminee"], name="idx_suivi_producteur_termine")]

    def __str__(self):
        return f"{self.producteur} - {self.formation.titre} ({self.progression}%)"

    def save(self, *args, **kwargs):
        if self.progression >= 100:
            self.terminee = True
        super().save(*args, **kwargs)