"""
Tests for the steps of a recept, grouped into fases, as a reader meets them.

See CLAUDE.md for how tests are written in this project. Arranging happens
through the ORM, the same way test_ingredient_lines.py does it, and every
assertion is made on what the page actually says.
"""

from django.test import TestCase

from recipes.models import Recipe, Step


def published_recipe(title):
    return Recipe.objects.create(title=title, status=Recipe.Status.PUBLISHED)


def step(recipe, position, text, phase=""):
    return Step.objects.create(recipe=recipe, position=position, text=text, phase=phase)


def texts_in_reading_order(page, *texts):
    """The given fragments, sorted by where they appear on the rendered page."""
    html = page.content.decode()
    return sorted(texts, key=html.index)


class StepRenderingTests(TestCase):
    def test_a_recept_says_what_to_do(self):
        recipe = published_recipe("Andijviestamppot")
        step(recipe, 1, "Kook de aardappels in twintig minuten gaar.")

        page = self.client.get("/recepten/andijviestamppot/")

        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Kook de aardappels in twintig minuten gaar.")

    def test_a_step_stands_under_the_fase_it_belongs_to(self):
        # Mise en place is what you do before the pan is hot, and a reader has
        # to be able to see where that stops.
        recipe = published_recipe("Quesadilla met zoete aardappel")
        step(recipe, 1, "Snijd de zoete aardappel in blokjes.", phase="Mise en place")
        step(recipe, 2, "Verhit een pan.", phase="Bakken")

        page = self.client.get("/recepten/quesadilla-met-zoete-aardappel/")

        self.assertContains(page, "<h3>Mise en place</h3>", html=True)
        self.assertContains(page, "<h3>Bakken</h3>", html=True)
        self.assertEqual(
            texts_in_reading_order(page, "Mise en place", "Snijd", "Bakken", "Verhit"),
            ["Mise en place", "Snijd", "Bakken", "Verhit"],
        )

    def test_the_numbering_carries_on_over_a_fase(self):
        # The worked example from the vault: seven steps under two fases, and
        # then a third fase that goes on at 8. A fase groups the steps, it
        # does not start counting them again (CONTEXT.md, "Fase").
        recipe = published_recipe("Quesadilla met zoete aardappel")
        for position in range(1, 6):
            step(recipe, position, f"Snijden {position}", phase="Mise en place")
        for position in range(6, 8):
            step(recipe, position, f"Bakken {position}", phase="Stappen")
        step(recipe, 8, "Verhit de pan zonder olie.", phase="Bouwen")

        page = self.client.get("/recepten/quesadilla-met-zoete-aardappel/")

        self.assertContains(
            page,
            '<li id="stap-8" value="8">Verhit de pan zonder olie.</li>',
            html=True,
        )
        self.assertNotContains(
            page,
            '<li id="stap-1" value="1">Verhit de pan zonder olie.</li>',
            html=True,
        )

    def test_the_steps_are_read_in_the_order_the_author_gave_them(self):
        # A recept is cooked from top to bottom, so the order is the author's
        # and never the order the rows happened to be typed in.
        recipe = published_recipe("Andijviestamppot")
        step(recipe, 3, "Stamp de andijvie erdoor.")
        step(recipe, 1, "Kook de aardappels gaar.")
        step(recipe, 2, "Giet de aardappels af.")

        page = self.client.get("/recepten/andijviestamppot/")

        self.assertEqual(
            texts_in_reading_order(page, "Stamp", "Kook", "Giet"),
            ["Kook", "Giet", "Stamp"],
        )

    def test_a_recept_without_fases_is_simply_a_list_of_steps(self):
        # Not every recept is worth dividing up, and one that is not may not
        # be given an empty heading to make up for it.
        recipe = published_recipe("Andijviestamppot")
        step(recipe, 1, "Kook de aardappels gaar.")
        step(recipe, 2, "Stamp de andijvie erdoor.")

        page = self.client.get("/recepten/andijviestamppot/")

        self.assertContains(page, "Kook de aardappels gaar.")
        self.assertContains(page, "Stamp de andijvie erdoor.")
        self.assertNotContains(page, "<h3>")

    def test_a_fase_the_recept_comes_back_to_is_a_second_fase(self):
        # A fase is a stretch of the sequence, not a name to gather steps
        # under: the pan is used, left, and used again, and step 3 may not be
        # lifted out of its place to sit beside steps 1 and 2.
        recipe = published_recipe("Quesadilla met zoete aardappel")
        step(recipe, 1, "Bak de vulling.", phase="Bakken")
        step(recipe, 2, "Vouw de tortilla dicht.", phase="Bouwen")
        step(recipe, 3, "Bak de quesadilla goudbruin.", phase="Bakken")

        page = self.client.get("/recepten/quesadilla-met-zoete-aardappel/")

        self.assertEqual(
            texts_in_reading_order(page, "Vouw de tortilla", "Bak de quesadilla"),
            ["Vouw de tortilla", "Bak de quesadilla"],
        )
        self.assertContains(page, "<h3>Bakken</h3>", count=2, html=True)

    def test_every_step_can_be_pointed_at_on_its_own(self):
        # Kookmodus (#10) strikes one single step through, and a reader who
        # is told "vanaf stap 3" has somewhere to jump to.
        recipe = published_recipe("Andijviestamppot")
        step(recipe, 1, "Kook de aardappels gaar.")
        step(recipe, 2, "Snijd de andijvie.", phase="Mise en place")

        page = self.client.get("/recepten/andijviestamppot/")

        self.assertContains(page, 'id="stap-1"')
        self.assertContains(page, 'id="stap-2"')

    def test_a_recept_without_steps_shows_no_empty_instructies(self):
        published_recipe("Andijviestamppot")

        page = self.client.get("/recepten/andijviestamppot/")

        self.assertEqual(page.status_code, 200)
        self.assertNotContains(page, "Instructies")
