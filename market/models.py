#market/models.py
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from decimal import Decimal
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Panier(models.Model):
    client = models.ForeignKey(
        "accounts.Utilisateur", on_delete=models.CASCADE, related_name="paniers",
        limit_choices_to={"role": "CLIENT"},
    )
    producteur = models.ForeignKey(
        "accounts.Producteur", on_delete=models.CASCADE, related_name="paniers",
        null=True, blank=True,
        help_text="Renseigné automatiquement à l'ajout du premier article.",
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Paniers"
        ordering = ["-date_creation"]
        constraints = [
            models.UniqueConstraint(fields=["client", "producteur"], name="un_panier_actif_par_producteur"),
        ]
        indexes = [models.Index(fields=["client"], name="idx_panier_client")]

    def __str__(self):
        return f"Panier de {self.client} ({self.producteur or 'vide'})"

    def peut_ajouter(self, produit):
        """À vérifier AVANT de créer un PanierArticle (retour d'erreur clair côté API)."""
        return self.producteur_id is None or self.producteur_id == produit.producteur_id


class PanierArticle(models.Model):
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE, related_name="articles")
    produit = models.ForeignKey("catalog.Produit", on_delete=models.CASCADE, related_name="+")
    quantite = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal(0.01))])
    prix = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Prix unitaire au moment de l'ajout (peut différer du prix courant du produit)."
    )

    class Meta:
        verbose_name = "Article du panier"
        verbose_name_plural = "Articles du panier"
        constraints = [
            models.UniqueConstraint(fields=["panier", "produit"], name="un_produit_une_fois_par_panier"),
        ]

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"

    @property
    def sous_total(self):
        return self.quantite * self.prix

    def clean(self):
        if self.panier_id and self.produit_id and not self.panier.peut_ajouter(self.produit):
            raise ValidationError(
                "Ce panier contient déjà des produits d'un autre producteur. "
                "Finalisez cette commande ou videz le panier avant d'en ajouter un nouveau."
            )

    def save(self, *args, **kwargs):
        self.clean()
        creation = self._state.adding
        super().save(*args, **kwargs)
        if creation and self.panier.producteur_id is None:
            self.panier.producteur = self.produit.producteur
            self.panier.save(update_fields=["producteur"])


class StatutCommande(models.TextChoices):
    EN_ATTENTE = "EN_ATTENTE", _("En attente de paiement")
    EN_PREPARATION = "EN_PREPARATION", _("En préparation")
    PRETE = "PRETE", _("Prête pour collecte")
    EN_LIVRAISON = "EN_LIVRAISON", _("En livraison")
    LIVREE = "LIVREE", _("Livrée")
    TERMINEE = "TERMINEE", _("Terminée")
    ANNULEE = "ANNULEE", _("Annulée")


class Commande(models.Model):
    """
    `client` doit avoir role=CLIENT, `livreur` (s'il est renseigné) doit
    avoir role=LIVREUR — imposé via limit_choices_to (UI admin) ET clean()
    (garde-fou réel, y compris hors admin).
    """
    numero = models.CharField(max_length=30, unique=True, editable=False)
    client = models.ForeignKey(
        "accounts.Utilisateur", on_delete=models.PROTECT, related_name="commandes_passees",
        limit_choices_to={"role": "CLIENT"},
    )
    producteur = models.ForeignKey(
        "accounts.Producteur", on_delete=models.PROTECT, related_name="commandes_recues"
    )
    livreur = models.ForeignKey(
        "accounts.Utilisateur", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="commandes_livrees",
        limit_choices_to={"role": "LIVREUR"},
    )
    adresse_livraison = models.TextField()
    montant_total = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, editable=False,
        help_text="Recalculé côté serveur à partir des lignes de commande."
    )
    statut = models.CharField(max_length=20, choices=StatutCommande.choices, default=StatutCommande.EN_ATTENTE)
    date_commande = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ["-date_commande"]
        indexes = [
            models.Index(fields=["client", "-date_commande"], name="idx_commande_client_date"),
            models.Index(fields=["producteur", "statut"], name="idx_commande_producteur_statut"),
            models.Index(fields=["livreur", "statut"], name="idx_commande_livreur_statut"),
        ]

    def __str__(self):
        return f"Commande {self.numero}"

    def clean(self):
        if self.client_id and self.client.role != "CLIENT":
            raise ValidationError({"client": "Le champ client doit référencer un Utilisateur de rôle CLIENT."})
        if self.livreur_id and self.livreur.role != "LIVREUR":
            raise ValidationError({"livreur": "Le livreur assigné doit être de rôle LIVREUR."})

    def save(self, *args, **kwargs):
        self.clean()
        if not self.numero:
            self.numero = f"CMD-{timezone.now():%Y%m%d}-{timezone.now().strftime('%H%M%S%f')[:10]}"
        super().save(*args, **kwargs)

    def recalculer_montant_total(self):
        total = sum((ligne.sous_total for ligne in self.lignes.all()), 0)
        self.montant_total = total
        self.save(update_fields=["montant_total"])
        return total


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name="lignes")
    produit = models.ForeignKey("catalog.Produit", on_delete=models.PROTECT, related_name="lignes_commande")
    quantite = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0.01)])
    prix = models.DecimalField(max_digits=10, decimal_places=2, editable=False, help_text="Prix figé au moment de la commande.")
    sous_total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    class Meta:
        verbose_name = "Ligne de commande"
        verbose_name_plural = "Lignes de commande"

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"

    def save(self, *args, **kwargs):
        self.sous_total = self.quantite * self.prix
        super().save(*args, **kwargs)


class ModePaiement(models.TextChoices):
    MOBILE_MONEY = "MOBILE_MONEY", _("Mobile Money (Orange/Moov)")
    WAVE = "WAVE", _("Wave")
    CARTE = "CARTE", _("Carte prépayée")


class StatutPaiement(models.TextChoices):
    EN_ATTENTE = "EN_ATTENTE", _("En attente")
    PAYE = "PAYE", _("Payé")
    ECHEC = "ECHEC", _("Échec")


class Paiement(models.Model):
    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name="paiement")
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    moyen = models.CharField(max_length=20, choices=ModePaiement.choices)
    reference = models.CharField(max_length=100, blank=True)
    statut = models.CharField(max_length=20, choices=StatutPaiement.choices, default=StatutPaiement.EN_ATTENTE)
    date_paiement = models.DateTimeField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        indexes = [models.Index(fields=["statut"], name="idx_paiement_statut")]

    def __str__(self):
        return f"Paiement {self.commande.numero} - {self.get_statut_display()}"

    def marquer_paye(self, reference=""):
        self.statut = StatutPaiement.PAYE
        self.date_paiement = timezone.now()
        if reference:
            self.reference = reference
        self.save()


class StatutVersement(models.TextChoices):
    EN_ATTENTE = "EN_ATTENTE", _("En attente")
    VERSE = "VERSE", _("Versé")


class Versement(models.Model):
    producteur = models.ForeignKey(
        "accounts.Producteur", on_delete=models.PROTECT, related_name="versements"
    )
    commande = models.OneToOneField(Commande, on_delete=models.PROTECT, related_name="versement")
    montant = models.DecimalField(max_digits=12, decimal_places=2, help_text="Montant brut de la commande.")
    commission_plateforme = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    montant_net = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    statut = models.CharField(max_length=20, choices=StatutVersement.choices, default=StatutVersement.EN_ATTENTE)
    date = models.DateTimeField(auto_now_add=True)
    date_versement = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Versement producteur"
        verbose_name_plural = "Versements producteurs"
        ordering = ["-date"]
        indexes = [models.Index(fields=["producteur", "statut"], name="idx_versement_prod_statut")]

    def __str__(self):
        return f"Versement {self.commande.numero} → {self.producteur}"

    def save(self, *args, **kwargs):
        self.montant_net = self.montant - self.commission_plateforme
        super().save(*args, **kwargs)

    def marquer_verse(self):
        self.statut = StatutVersement.VERSE
        self.date_versement = timezone.now()
        self.save()


class SocieteLivraison(models.Model):
    nom = models.CharField(max_length=150)
    responsable = models.CharField(max_length=150, blank=True)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    adresse = models.TextField(blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Société de livraison"
        verbose_name_plural = "Sociétés de livraison"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class StatutLivraison(models.TextChoices):
    EN_ATTENTE = "EN_ATTENTE", _("En attente d'un livreur (pool)")
    EN_COURS = "EN_COURS", _("En cours")
    LIVREE = "LIVREE", _("Livrée (déclarée par le livreur)")
    CONFIRMEE = "CONFIRMEE", _("Confirmée reçue")


class Livraison(models.Model):
    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name="livraison")
    livreur = models.ForeignKey(
        "accounts.Utilisateur", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="livraisons", limit_choices_to={"role": "LIVREUR"},
    )
    societe = models.ForeignKey(
        SocieteLivraison, on_delete=models.SET_NULL, null=True, blank=True, related_name="livraisons"
    )
    statut = models.CharField(max_length=20, choices=StatutLivraison.choices, default=StatutLivraison.EN_ATTENTE)
    date_prise = models.DateTimeField(null=True, blank=True)
    date_livraison = models.DateTimeField(null=True, blank=True)
    confirmee_par = models.ForeignKey(
        "accounts.Utilisateur", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="livraisons_confirmees",
        help_text="Le client lui-même, ou l'admin si le client ne répond pas.",
    )
    date_confirmation = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Livraison"
        verbose_name_plural = "Livraisons"
        indexes = [
            models.Index(fields=["statut"], name="idx_livraison_statut"),
            models.Index(fields=["livreur", "statut"], name="idx_livraison_livreur_statut"),
        ]

    def __str__(self):
        return f"Livraison {self.commande.numero}"

    def clean(self):
        if self.livreur_id and self.livreur.role != "LIVREUR":
            raise ValidationError({"livreur": "Le livreur assigné doit être de rôle LIVREUR."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def prendre_en_charge(self, livreur):
        if self.livreur_id is not None:
            raise ValidationError("Cette livraison a déjà été prise en charge par un autre livreur.")
        self.livreur = livreur
        self.statut = StatutLivraison.EN_COURS
        self.date_prise = timezone.now()
        self.save()
        Commission.objects.get_or_create(livraison=self, livreur=livreur)

    def relacher(self):
        if self.statut in (StatutLivraison.LIVREE, StatutLivraison.CONFIRMEE):
            raise ValidationError("Impossible de relâcher une livraison déjà livrée ou confirmée.")
        Commission.objects.filter(livraison=self).delete()
        self.livreur = None
        self.statut = StatutLivraison.EN_ATTENTE
        self.date_prise = None
        self.save()

    def marquer_livree(self):
        if not self.livreur_id:
            raise ValidationError("Aucun livreur n'a pris en charge cette livraison.")
        self.statut = StatutLivraison.LIVREE
        self.date_livraison = timezone.now()
        self.save()

    def confirmer_reception(self, utilisateur):
        if self.statut != StatutLivraison.LIVREE:
            raise ValidationError("La livraison doit d'abord être déclarée livrée par le livreur.")
        self.statut = StatutLivraison.CONFIRMEE
        self.confirmee_par = utilisateur
        self.date_confirmation = timezone.now()
        self.save()
        commission = getattr(self, "commission", None)
        if commission:
            commission.valider()


class StatutCommission(models.TextChoices):
    EN_ATTENTE = "EN_ATTENTE", _("En attente")
    VALIDEE = "VALIDEE", _("Validée")
    PAYEE = "PAYEE", _("Payée")


class Commission(models.Model):
    """
    Commission du livreur pour une Livraison. Créée dès la prise en
    charge (statut EN_ATTENTE), passe à VALIDEE quand la réception est
    confirmée (voir Livraison.confirmer_reception), et à PAYEE lorsque
    l'admin déclenche effectivement le versement au livreur.
    """
    livraison = models.OneToOneField(Livraison, on_delete=models.CASCADE, related_name="commission")
    livreur = models.ForeignKey(
        "accounts.Utilisateur", on_delete=models.CASCADE, related_name="commissions",
        limit_choices_to={"role": "LIVREUR"},
    )
    montant = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    statut = models.CharField(max_length=20, choices=StatutCommission.choices, default=StatutCommission.EN_ATTENTE)

    class Meta:
        verbose_name = "Commission livreur"
        verbose_name_plural = "Commissions livreurs"
        indexes = [models.Index(fields=["livreur", "statut"], name="idx_commission_livreur_statut")]

    def __str__(self):
        return f"Commission {self.montant} - {self.livreur} ({self.get_statut_display()})"

    def save(self, *args, **kwargs):
        if not self.montant:
            from accounts.models import Parametre

            parametre = Parametre.charger()

            montant_commande = self.livraison.commande.montant_total

            self.montant = (
                                   montant_commande * parametre.commission_livreur
                           ) / 100

        super().save(*args, **kwargs)
    def valider(self):
        if self.statut == StatutCommission.EN_ATTENTE:
            self.statut = StatutCommission.VALIDEE
            self.save()

    def marquer_payee(self):
        if self.statut != StatutCommission.VALIDEE:
            raise ValidationError("Seule une commission validée peut être marquée payée.")
        self.statut = StatutCommission.PAYEE
        self.save()