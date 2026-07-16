"""
Django settings for ferme_ecole project.
"""

from pathlib import Path
from datetime import timedelta


# =====================================================
# BASE
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = (
    "django-insecure-$02bz^(3hdxf0kv0%#v2f2v)"
    "1jta1h!-yzdb=zb3qb2u^wo2&-"
)


DEBUG = True


ALLOWED_HOSTS = ["*"]



# =====================================================
# APPLICATIONS
# =====================================================

INSTALLED_APPS = [

    # Grappelli Admin
    "grappelli",


    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",


    # API
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",


    # CORS
    "corsheaders",


    # Projet
    "accounts",
    "catalog",
    "market",
    "community",
]



# =====================================================
# MIDDLEWARE
# =====================================================

MIDDLEWARE = [

    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.security.SecurityMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]



# =====================================================
# URL / APPLICATION
# =====================================================

ROOT_URLCONF = "ferme_ecole.urls"


WSGI_APPLICATION = "ferme_ecole.wsgi.application"



# =====================================================
# TEMPLATES
# =====================================================

TEMPLATES = [

    {
        "BACKEND":
            "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates"
        ],

        "APP_DIRS": True,

        "OPTIONS": {

            "context_processors": [

                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]



# =====================================================
# BASE DE DONNEES
# =====================================================

DATABASES = {

    "default": {

        "ENGINE":
            "django.db.backends.postgresql",

        "NAME":
            "agro_db",

        "USER":
            "postgres",

        "PASSWORD":
            "data2025",

        "HOST":
            "localhost",

        "PORT":
            "5432",
    }
}



# =====================================================
# MODELE UTILISATEUR PERSONNALISE
# =====================================================

AUTH_USER_MODEL = "accounts.Utilisateur"



# =====================================================
# VALIDATION MOT DE PASSE
# =====================================================

AUTH_PASSWORD_VALIDATORS = [

    {
        "NAME":
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },

    {
        "NAME":
            "django.contrib.auth.password_validation.MinimumLengthValidator",
    },

    {
        "NAME":
            "django.contrib.auth.password_validation.CommonPasswordValidator",
    },

    {
        "NAME":
            "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]



# =====================================================
# INTERNATIONALISATION
# =====================================================

LANGUAGE_CODE = "fr-fr"


TIME_ZONE = "Africa/Ouagadougou"


USE_I18N = True


USE_TZ = True



# =====================================================
# STATIC / MEDIA
# =====================================================

STATIC_URL = "/static/"


STATIC_ROOT = BASE_DIR / "staticfiles"


STATICFILES_DIRS = [

    BASE_DIR / "static"
]


MEDIA_URL = "/media/"


MEDIA_ROOT = BASE_DIR / "media"



DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)



# =====================================================
# GRAPPELLI ADMIN
# =====================================================

GRAPPELLI_ADMIN_TITLE = (
    "FERME-ÉCOLE Administration"
)


GRAPPELLI_INDEX_DASHBOARD = (
    "grappelli.dashboard.dashboards.DefaultIndexDashboard"
)


GRAPPELLI_AUTOCOMPLETE_SEARCH = True



# =====================================================
# CORS
# =====================================================

CORS_ALLOW_ALL_ORIGINS = True



# =====================================================
# REST FRAMEWORK
# =====================================================

REST_FRAMEWORK = {

    "DEFAULT_AUTHENTICATION_CLASSES": (

        "rest_framework_simplejwt.authentication.JWTAuthentication",

    ),


    "DEFAULT_PERMISSION_CLASSES": (

        "rest_framework.permissions.IsAuthenticated",

    ),
}



# =====================================================
# JWT
# =====================================================

SIMPLE_JWT = {

    "ACCESS_TOKEN_LIFETIME":
        timedelta(minutes=60),


    "REFRESH_TOKEN_LIFETIME":
        timedelta(days=7),


    "ROTATE_REFRESH_TOKENS":
        True,


    "BLACKLIST_AFTER_ROTATION":
        True,


    "AUTH_HEADER_TYPES":
        (
            "Bearer",
        ),
}