"""
ferme_ecole/urls.py

Routes principales API :
- Authentification
- Accounts
- Catalogue
- Marché
- Communauté
"""


from django.contrib import admin

from django.urls import (
    path,
    include,
)


from django.conf import settings

from django.conf.urls.static import static


from rest_framework.routers import DefaultRouter



# =====================================================
# ACCOUNTS
# =====================================================

from accounts.views import (
    UtilisateurViewSet,
    ProducteurViewSet,
    NotificationViewSet,
    JournalActiviteViewSet,
    ParametreViewSet,

    RegisterView,
    LoginView,
    ProfileView,
)



# =====================================================
# CATALOG
# =====================================================

from catalog.views import (
    CategorieViewSet,
    ProduitViewSet,
    CertificationViewSet,
    ProduitImageViewSet,
)



# =====================================================
# MARKET
# =====================================================

from market.views import (
    PanierViewSet,
    PanierArticleViewSet,
    CommandeViewSet,
    PaiementViewSet,
    VersementViewSet,
    LivraisonViewSet,
    CommissionViewSet,
    SocieteLivraisonViewSet,
)



# =====================================================
# COMMUNITY
# =====================================================

from community.views import (
    AvisViewSet,
    SujetForumViewSet,
    ReponseForumViewSet,
    FormationViewSet,
    SuiviFormationViewSet,
)



# =====================================================
# ROUTER
# =====================================================

router = DefaultRouter()



# =====================================================
# ACCOUNTS
# =====================================================

router.register(
    r"utilisateurs",
    UtilisateurViewSet,
    basename="utilisateurs"
)

router.register(
    r"producteurs",
    ProducteurViewSet,
    basename="producteurs"
)

router.register(
    r"notifications",
    NotificationViewSet,
    basename="notifications"
)

router.register(
    r"journal-activites",
    JournalActiviteViewSet,
    basename="journal-activites"
)

router.register(
    r"parametres",
    ParametreViewSet,
    basename="parametres"
)



# =====================================================
# CATALOG
# =====================================================

router.register(
    r"categories",
    CategorieViewSet,
    basename="categories"
)

router.register(
    r"produits",
    ProduitViewSet,
    basename="produits"
)

router.register(
    r"certifications",
    CertificationViewSet,
    basename="certifications"
)

router.register(
    r"produit-images",
    ProduitImageViewSet,
    basename="produit-images"
)



# =====================================================
# MARKET
# =====================================================

router.register(
    r"paniers",
    PanierViewSet,
    basename="paniers"
)

router.register(
    r"panier-articles",
    PanierArticleViewSet,
    basename="panier-articles"
)

router.register(
    r"commandes",
    CommandeViewSet,
    basename="commandes"
)

router.register(
    r"paiements",
    PaiementViewSet,
    basename="paiements"
)

router.register(
    r"versements",
    VersementViewSet,
    basename="versements"
)

router.register(
    r"livraisons",
    LivraisonViewSet,
    basename="livraisons"
)

router.register(
    r"commissions",
    CommissionViewSet,
    basename="commissions"
)

router.register(
    r"societes-livraison",
    SocieteLivraisonViewSet,
    basename="societes-livraison"
)



# =====================================================
# COMMUNITY
# =====================================================

router.register(
    r"avis",
    AvisViewSet,
    basename="avis"
)

router.register(
    r"sujets-forum",
    SujetForumViewSet,
    basename="sujets-forum"
)

router.register(
    r"reponses-forum",
    ReponseForumViewSet,
    basename="reponses-forum"
)

router.register(
    r"formations",
    FormationViewSet,
    basename="formations"
)

router.register(
    r"suivis-formations",
    SuiviFormationViewSet,
    basename="suivis-formations"
)



# =====================================================
# URLPATTERNS
# =====================================================

urlpatterns = [

    # Administration Django
    path(
        "admin/",
        admin.site.urls
    ),


    # -------------------------
    # Authentification
    # -------------------------

    path(
        "api/auth/register/",
        RegisterView.as_view(),
        name="register"
    ),

    path(
        "api/auth/login/",
        LoginView.as_view(),
        name="login"
    ),

    path(
        "api/auth/me/",
        ProfileView.as_view(),
        name="profile"
    ),


    # -------------------------
    # API REST
    # -------------------------

    path(
        "api/",
        include(router.urls)
    ),

]



# =====================================================
# MEDIA / STATIC
# =====================================================

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )


    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )