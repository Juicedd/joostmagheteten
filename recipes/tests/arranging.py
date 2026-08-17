"""
The recepten these tests look at, and the one thing they all read back.

Not a test module -- `manage.py test` only collects `test*.py`. Arranging
through the ORM is what CLAUDE.md allows and the assertions never do: a
recept has to exist before there is a page to fetch, the same way
authors.py has to create an account before there is anyone to sign in as.
"""

from decimal import Decimal

from recipes.models import Ingredient, Recipe, RecipeIngredient, Step


def published_recipe(title, **fields):
    """A recept a visitor may read, with whatever else it is given.

    Everything past the title is optional on a Recipe, so it is optional
    here too: a test that is about the seizoen says only that.
    """
    return Recipe.objects.create(title=title, status=Recipe.Status.PUBLISHED, **fields)


def ingredient_line(
    recipe, name, quantity=None, unit="", note="", is_staple=False, position=0
):
    """One ingrediëntregel, creating the ingrediënt it uses if it is new.

    No unit unless one is asked for, because a unit without a quantity is
    the one combination an ingrediëntregel refuses -- "stuk Goudse kaas".
    """
    ingredient, _ = Ingredient.objects.get_or_create(
        name=name, defaults={"is_staple": is_staple}
    )
    return RecipeIngredient.objects.create(
        recipe=recipe,
        ingredient=ingredient,
        quantity=None if quantity is None else Decimal(quantity),
        unit=unit,
        note=note,
        position=position,
    )


def step(recipe, position, text, phase=""):
    return Step.objects.create(recipe=recipe, position=position, text=text, phase=phase)


# The words that would give an oordeel away if one ever reached a template,
# including the ones CONTEXT.md tells us not to use for it: a leak under a
# name the glossary forbids is still a leak. Kept here because both the page
# tests and the authoring tests ask a page for the same absence.
OORDEEL_WORDS = [
    "voedingsscore",
    "budgetscore",
    "waardering",
    "rating",
    "oordeel",
    "beoordeling",
    "score",
]


def in_reading_order(page, *fragments):
    """The given fragments, sorted by where they appear on the rendered page.

    Which is how a page is asked what order it says things in, without
    asking the code that rendered it anything at all.
    """
    html = page.content.decode()
    return sorted(fragments, key=html.index)
