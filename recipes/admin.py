# Django admin is the authoring surface for recepten (spec #1). Registrations
# arrive alongside the models they edit.

from django.contrib import admin

from recipes.models import Recipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("title", "status")
    list_filter = ("status",)
    search_fields = ("title",)
    # Fills the slug in while the title is typed, so the URL is visible and
    # editable before it is committed to. Django's own script only binds this
    # while the field is empty, so editing the title of a recept that already
    # has a URL leaves that URL alone -- which is the same promise the model
    # makes on save (ADR-0006).
    prepopulated_fields = {"slug": ("title",)}
