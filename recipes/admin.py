# Django admin is the authoring surface for recepten (spec #1). Registrations
# arrive alongside the models they edit.

from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect

from recipes.models import Ingredient, Recipe, RecipeIngredient, Step


class IngredientAutocomplete(AutocompleteSelect):
    """The ingrediënt dropdown, which survives being handed a name.

    Django's autocomplete widget looks the selected value up in the database
    while re-rendering the form, so a value that is not a key at all -- a
    name, which is the thing this field exists to refuse -- turns a form the
    author could have corrected into a server error. Dropping it here leaves
    the field empty and the form's own message in place.
    """

    def optgroups(self, name, value, attr=None):
        # A key is a number; a name never is.
        keys = [one for one in value if str(one).isdigit()]
        return super().optgroups(name, keys, attr)


class RecipeIngredientInline(admin.TabularInline):
    """The ingrediëntregels, edited inside the recept they belong to.

    Inline rather than a page of its own because an ingrediëntregel has no
    life outside its recept: it is written while the recept is written, and
    read while the recept is read.
    """

    model = RecipeIngredient
    extra = 1
    verbose_name = "ingrediëntregel"
    verbose_name_plural = "ingrediëntregels"
    # A dropdown that searches the ingrediënten there already are, instead of
    # a box the name can be typed into. Typing is how a vault ends up with
    # `Ui` beside `ui`, and the split is only noticed once something -- an
    # ingrediëntpagina, a boodschappenlijst -- tries to gather them again.
    # Django hangs its own "add another" button off this widget, so a genuinely
    # new ingrediënt is still one popup away without leaving the recept.
    autocomplete_fields = ["ingredient"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "ingredient":
            kwargs["widget"] = IngredientAutocomplete(db_field, self.admin_site)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class StepInline(admin.TabularInline):
    """The steps, edited inside the recept they belong to.

    Inline for the same reason the ingrediëntregels are, and stacked in a
    table so the fase of every step is in one column: a fase is a run of
    steps, so what the author needs to see while typing is where the name in
    that column stops repeating.
    """

    model = Step
    extra = 1
    verbose_name = "stap"
    verbose_name_plural = "stappen"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "is_staple")
    list_filter = ("is_staple",)
    # Also what the autocomplete on the recept form searches through.
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("title", "status")
    list_filter = ("status",)
    search_fields = ("title",)
    # In the order a recept is written: what goes in it, and then what to do
    # with it.
    inlines = [RecipeIngredientInline, StepInline]
    # Fills the slug in while the title is typed, so the URL is visible and
    # editable before it is committed to. Django's own script only binds this
    # while the field is empty, so editing the title of a recept that already
    # has a URL leaves that URL alone -- which is the same promise the model
    # makes on save (ADR-0006).
    prepopulated_fields = {"slug": ("title",)}
