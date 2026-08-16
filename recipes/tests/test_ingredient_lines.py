"""
Tests for ingrediëntregels as a reader meets them on the recept page.

See CLAUDE.md for how tests are written in this project. Arranging happens
through the ORM -- the same way authors.py creates the account it signs in
with -- and every assertion is made on what the page actually says.
"""

from decimal import Decimal

from django.test import TestCase

from recipes.models import Ingredient, Recipe, RecipeIngredient, Unit


def published_recipe(title):
    return Recipe.objects.create(title=title, status=Recipe.Status.PUBLISHED)


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


def names_in_reading_order(page, *names):
    """The given names, sorted by where they appear on the rendered page."""
    html = page.content.decode()
    return sorted(names, key=html.index)


class IngredientLineRenderingTests(TestCase):
    def test_an_ingredientregel_shows_how_much_of_what_and_the_remark(self):
        # CONTEXT.md's own example of an ingrediëntregel, rendered:
        # "2 blikken zwarte bonen (van 400gr)".
        recipe = published_recipe("Quesadilla met zoete aardappel")
        ingredient_line(
            recipe, "Zwarte bonen", quantity="2", unit=Unit.CAN, note="van 400gr"
        )

        page = self.client.get("/recepten/quesadilla-met-zoete-aardappel/")

        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "2 blikken")
        self.assertContains(page, "Zwarte bonen")
        self.assertContains(page, "van 400gr")

    def test_ingredientregels_are_read_in_the_order_the_author_gave_them(self):
        # A cook reads the list as one thing to shop for and one thing to lay
        # out, so the order is the author's, not alphabetical and not the
        # order the rows happened to be typed in.
        recipe = published_recipe("Quesadilla met zoete aardappel")
        ingredient_line(recipe, "Goudse kaas", position=3)
        ingredient_line(recipe, "Tortilla", position=1)
        ingredient_line(recipe, "Zoete aardappel", position=2)

        page = self.client.get("/recepten/quesadilla-met-zoete-aardappel/")

        self.assertEqual(
            names_in_reading_order(page, "Tortilla", "Zoete aardappel", "Goudse kaas"),
            ["Tortilla", "Zoete aardappel", "Goudse kaas"],
        )

    def test_basisingredienten_stand_apart_from_what_has_to_be_bought(self):
        # Both groups are on the page -- a recept states everything that goes
        # into it -- but a reader can tell at a glance which half is the
        # boodschappenlijst and which half is already in the kitchen.
        recipe = published_recipe("Quesadilla met zoete aardappel")
        ingredient_line(recipe, "Zwarte bonen", quantity="2", unit=Unit.CAN)
        ingredient_line(
            recipe, "Komijnpoeder", quantity="1", unit=Unit.TEASPOON, is_staple=True
        )

        page = self.client.get("/recepten/quesadilla-met-zoete-aardappel/")

        self.assertContains(page, "<h2>Ingrediënten</h2>", html=True)
        self.assertContains(page, "<h2>Basisingrediënten</h2>", html=True)
        self.assertEqual(
            names_in_reading_order(
                page, "Zwarte bonen", "Basisingrediënten", "Komijnpoeder"
            ),
            ["Zwarte bonen", "Basisingrediënten", "Komijnpoeder"],
        )

    def test_half_of_something_is_written_the_way_Dutch_writes_it(self):
        # The quantity is a number so that it can scale with the porties
        # later, which is also why it may be half of one -- and a number is
        # not how a recept reads: 0,5 liter, not 0.50.
        recipe = published_recipe("Andijviestamppot")
        ingredient_line(recipe, "Melk", quantity="0.5", unit=Unit.LITER)

        page = self.client.get("/recepten/andijviestamppot/")

        self.assertContains(page, "0,5 liter")
        self.assertNotContains(page, "0.50")

    def test_an_ingredientregel_without_a_quantity_still_reads_as_a_sentence(self):
        # Peper naar smaak has no number, and the page may not answer that
        # with a stray "None" in front of the name.
        recipe = published_recipe("Andijviestamppot")
        ingredient_line(recipe, "Peper", note="naar smaak", is_staple=True)

        page = self.client.get("/recepten/andijviestamppot/")

        self.assertContains(page, "Peper")
        self.assertContains(page, "naar smaak")
        self.assertNotContains(page, "None")

    def test_one_and_a_half_of_something_stays_singular(self):
        # Dutch pluralises whole things -- 2 blikken -- and stops there:
        # anderhalf blik is still one blik, and part of the next.
        recipe = published_recipe("Andijviestamppot")
        ingredient_line(recipe, "Kokosmelk", quantity="1.5", unit=Unit.CAN)

        page = self.client.get("/recepten/andijviestamppot/")

        self.assertContains(page, "1,5 blik")
        self.assertNotContains(page, "1,5 blikken")

    def test_a_recept_without_basisingredienten_shows_no_empty_group(self):
        recipe = published_recipe("Quesadilla met zoete aardappel")
        ingredient_line(recipe, "Zwarte bonen", quantity="2", unit=Unit.CAN)

        page = self.client.get("/recepten/quesadilla-met-zoete-aardappel/")

        self.assertNotContains(page, "Basisingrediënten")
