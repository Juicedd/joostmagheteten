from django.apps import AppConfig


class RecipesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recipes"
    # The heading this app gets in the admin, which Joost reads (ADR-0002).
    verbose_name = "Recepten"
