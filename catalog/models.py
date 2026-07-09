#catalog/models.py
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Exists, OuterRef
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Categorie(models.Model):
    """Ex: Fruits, Légumes, Céréales, Intrants, Produits transformés."""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ["nom"]
        indexes = [models.Index(fields=["nom"], name="idx_categorie_nom")]

    def __str__(self):
        return self.nom


class Certification(models.Model):

    class Statut(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", _("En attente")
        VALIDEE = "VALIDEE", _("Validée")
        REFUSEE = "REFUSEE", _("Refusée")

    producteur = models.ForeignKey(
        "accounts.Producteur", on_delete=models.CASCADE, related_name="certifications"
    )
    type = models.CharField(max_length=100, help_text="Ex: BIO SPG, CNABio...")
    numero = models.CharField(max_length=100, blank=True)
    document = models.FileField(upload_to="certifications/documents/", blank=True, null=True)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True, help_text="Date d'expiration de la certification.")
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    valide_par = models.ForeignKey(
        "accounts.Utilisateur", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="certifications_validees",
        limit_choices_to={"role": "ADMIN"},
    )
    date_validation = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"
        ordering = ["-date_debut"]
        indexes = [
            models.Index(fields=["producteur", "statut"], name="idx_certif_producteur_statut"),
            models.Index(fields=["statut", "date_fin"], name="idx_certif_statut_date_fin"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(date_fin__isnull=True)
                | models.Q(date_debut__isnull=True)
                | models.Q(date_fin__gte=models.F("date_debut")),
                name="certification_date_fin_apres_date_debut",
            ),
        ]

    def __str__(self):
        return f"{self.producteur.nom_exploitation} - {self.type} ({self.get_statut_display()})"

    def clean(self):
        if self.date_debut and self.date_fin and self.date_fin < self.date_debut:
            raise ValidationError({"date_fin": "La date de fin doit être postérieure à la date de début."})
        if self.statut == self.Statut.VALIDEE and not self.valide_par_id:
            raise ValidationError({"valide_par": "Un administrateur doit être renseigné pour valider."})

    def save(self, *args, **kwargs):
        self.clean()
        if self.statut == self.Statut.VALIDEE and not self.date_validation:
            self.date_validation = timezone.now()
        super().save(*args, **kwargs)

    @property
    def est_active(self):
        return self.statut == self.Statut.VALIDEE and (self.date_fin is None or self.date_fin >= timezone.now().date())


class ProduitQuerySet(models.QuerySet):
    def visibles_publiquement(self):
        certifications_actives = Certification.objects.filter(
            producteur_id=OuterRef("producteur_id"),
            statut=Certification.Statut.VALIDEE,
        ).filter(models.Q(date_fin__isnull=True) | models.Q(date_fin__gte=timezone.now().date()))
        return self.filter(valide=True, disponible=True).filter(Exists(certifications_actives))


class TypeProduit(models.TextChoices):
    FRAIS = "FRAIS", _("Produit frais")
    TRANSFORME = "TRANSFORME", _("Produit transformé")
    INTRANT = "INTRANT", _("Intrant agroécologique")


class Produit(models.Model):
    producteur = models.ForeignKey(
        "accounts.Producteur", on_delete=models.CASCADE, related_name="produits"
    )
    categorie = models.ForeignKey(
        Categorie, on_delete=models.PROTECT, related_name="produits"
    )
    nom = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unite = models.CharField(max_length=20, default="kg", help_text="kg, litre, sac, pièce...")
    stock = models.PositiveIntegerField(default=0)
    type_produit = models.CharField(max_length=20, choices=TypeProduit.choices)
    image = models.ImageField(upload_to="produits/", blank=True, null=True)
    valide = models.BooleanField(
        default=False, help_text="Validation admin requise avant apparition dans le catalogue public."
    )
    valide_par = models.ForeignKey(
        "accounts.Utilisateur", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="produits_valides",
        limit_choices_to={"role": "ADMIN"},
    )
    date_validation = models.DateTimeField(null=True, blank=True)
    disponible = models.BooleanField(default=True, help_text="Bascule rapide indépendante de la validation admin.")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    objects = ProduitQuerySet.as_manager()

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ["-date_creation"]
        indexes = [
            models.Index(fields=["producteur", "valide", "disponible"], name="idx_produit_prod_valide_dispo"),
            models.Index(fields=["categorie"], name="idx_produit_categorie"),
            models.Index(fields=["nom"], name="idx_produit_nom"),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(prix__gte=0), name="produit_prix_positif"),
        ]

    def __str__(self):
        return f"{self.nom} - {self.producteur.nom_exploitation}"

    def save(self, *args, **kwargs):
        if self.valide and not self.date_validation:
            self.date_validation = timezone.now()
        super().save(*args, **kwargs)


class ProduitImage(models.Model):
    """Images additionnelles (galerie) en plus de Produit.image (photo principale)."""
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="produits/galerie/")

    class Meta:
        verbose_name = "Image produit"
        verbose_name_plural = "Images produit"

    def __str__(self):
        return f"Image de {self.produit.nom}"