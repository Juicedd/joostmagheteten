"""
Django settings for joostmagheteten.

Everything that differs between a laptop and production comes from the
environment -- see .env.example for the complete list. Secrets are never
committed, and there is no second settings module to keep in sync.

The production hardening at the bottom of this file hangs off one environment
variable rather than off DEBUG, because tests run with DEBUG=False too and a
laptop has no TLS to redirect to. `manage.py check --deploy` runs on every
deploy (build.sh) and fails the build if any of it goes missing.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, []),
    DJANGO_SERVED_OVER_HTTPS=(bool, False),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "recipes",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Serves everything in STATIC_ROOT. There is no separate web server in
    # front of Django on Render, so without this the deployed site has no CSS.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "config.wsgi.application"

# Postgres in every environment, including on a laptop (ADR-0005).
DATABASES = {"default": env.db("DATABASE_URL")}

_PASSWORD_VALIDATION = "django.contrib.auth.password_validation"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": f"{_PASSWORD_VALIDATION}.UserAttributeSimilarityValidator"},
    {"NAME": f"{_PASSWORD_VALIDATION}.MinimumLengthValidator"},
    {"NAME": f"{_PASSWORD_VALIDATION}.CommonPasswordValidator"},
    {"NAME": f"{_PASSWORD_VALIDATION}.NumericPasswordValidator"},
]

# ADR-0002: code identifiers are English, everything a visitor reads is Dutch.
LANGUAGE_CODE = "nl"
TIME_ZONE = "Europe/Amsterdam"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # collectstatic writes each file under a name containing a hash of its
    # contents, so a changed file is a changed URL and WhiteNoise can tell
    # browsers to cache it forever. It also writes gzip and brotli copies.
    "staticfiles": {"BACKEND": "config.storage.CollectedStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Production hardening -------------------------------------------------
# True only where something in front of Django terminates TLS -- Render's
# proxy does. False on a laptop and in tests, where there is no HTTPS at all
# and switching this on would redirect every request into nowhere.
if env("DJANGO_SERVED_OVER_HTTPS"):
    # Render forwards the visitor's original scheme here. Without it Django
    # sees plain HTTP behind the proxy, redirects forever, and rejects admin
    # logins because the Origin header says https and the request says http.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    # A year, and a promise: a browser that has seen this header refuses plain
    # HTTP for this hostname until it expires. Render serves HTTPS on both
    # onrender.com and custom domains, so there is nothing to lose by it.
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # Inert on a subdomain of onrender.com -- preloading is something only the
    # owner of a domain can ask for. It is here for the custom domain later,
    # and because `check --deploy` warns without it.
    SECURE_HSTS_PRELOAD = True
    # ADR-0004 means a visitor is never handed a cookie; these two are about
    # the author's session and CSRF cookies in the admin.
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
