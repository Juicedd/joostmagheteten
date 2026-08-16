"""
Tests for writing a recept in the Django admin.

See CLAUDE.md for how tests are written in this project. This module drives
the authoring surface the way Joost does -- signed in, posting the admin's own
forms -- and then checks the result the way a visitor sees it, over HTTP. The
tickets that add ingrediëntregels and steps extend these same flows with
inline formsets.
"""

from django.test import TestCase

from recipes.models import Ingredient, Recipe, RecipeIngredient, Step, Unit
from recipes.tests.admin_forms import (
    ADD_RECIPE,
    LINES,
    STEPS,
    change_recipe,
    ingredient_line_fields,
    recipe_form,
    step_fields,
)
from recipes.tests.authors import sign_in_as_the_author


class AuthoringTests(TestCase):
    def setUp(self):
        sign_in_as_the_author(self.client)

    def test_the_form_for_a_new_recept_is_in_dutch(self):
        response = self.client.get(ADD_RECIPE)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Titel")
        self.assertContains(response, "Publicatiestatus")

    def test_the_author_can_write_a_recept_in_the_admin(self):
        response = self.client.post(
            ADD_RECIPE, recipe_form("Andijviestamppot met oude kaas")
        )

        self.assertEqual(response.status_code, 302)
        page = self.client.get("/recepten/andijviestamppot-met-oude-kaas/")
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Andijviestamppot met oude kaas")

    def test_a_recept_written_in_the_admin_is_not_public_yet(self):
        self.client.post(ADD_RECIPE, recipe_form("Andijviestamppot met oude kaas"))
        self.client.logout()

        page = self.client.get("/recepten/andijviestamppot-met-oude-kaas/")

        self.assertEqual(page.status_code, 404)

    def test_publishing_a_recept_in_the_admin_makes_it_public(self):
        # Going live is a decision, not a side effect of finishing the text.
        self.client.post(ADD_RECIPE, recipe_form("Andijviestamppot met oude kaas"))

        response = self.client.post(
            change_recipe("andijviestamppot-met-oude-kaas"),
            recipe_form(
                "Andijviestamppot met oude kaas",
                slug="andijviestamppot-met-oude-kaas",
                status=Recipe.Status.PUBLISHED,
            ),
        )

        self.assertEqual(response.status_code, 302)
        self.client.logout()
        page = self.client.get("/recepten/andijviestamppot-met-oude-kaas/")
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Andijviestamppot met oude kaas")

    def test_rewriting_the_title_of_a_published_recept_leaves_its_url_alone(self):
        # Someone has the old link in a message thread. Sharpening the title
        # afterwards must not turn that link into a 404 (ADR-0006).
        self.client.post(
            ADD_RECIPE,
            recipe_form("Andijviestamppot", status=Recipe.Status.PUBLISHED),
        )

        self.client.post(
            change_recipe("andijviestamppot"),
            recipe_form(
                "Andijviestamppot met oude kaas",
                slug="andijviestamppot",
                status=Recipe.Status.PUBLISHED,
            ),
        )

        self.client.logout()
        page = self.client.get("/recepten/andijviestamppot/")
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Andijviestamppot met oude kaas")

    def test_a_second_recept_cannot_take_a_url_that_is_taken(self):
        # Folding diacritics is lossy, so two titles can land on the same
        # URL. The author gets the form back to fix it, rather than a 500 --
        # and the recept that already owns the URL is left alone (ADR-0006).
        self.client.post(ADD_RECIPE, recipe_form("Soufflé van oude Goudse kaas"))

        response = self.client.post(
            ADD_RECIPE, recipe_form("Souffle van oude Goudse kaas")
        )

        self.assertEqual(response.status_code, 200)
        page = self.client.get("/recepten/souffle-van-oude-goudse-kaas/")
        self.assertContains(page, "Soufflé van oude Goudse kaas")


QUESADILLA = "Quesadilla met zoete aardappel"
QUESADILLA_URL = "/recepten/quesadilla-met-zoete-aardappel/"


class IngredientLineAuthoringTests(TestCase):
    """Writing ingrediëntregels into a recept, inline on the recept form."""

    def setUp(self):
        sign_in_as_the_author(self.client)
        self.beans = Ingredient.objects.create(name="Zwarte bonen")

    def write_quesadilla_with(self, *lines):
        return self.client.post(
            ADD_RECIPE,
            recipe_form(QUESADILLA, status=Recipe.Status.PUBLISHED, lines=lines),
        )

    def test_the_author_writes_ingredientregels_inside_the_recept(self):
        response = self.write_quesadilla_with(
            ingredient_line_fields(
                self.beans.pk, quantity="2", unit=Unit.CAN, note="van 400gr"
            )
        )

        self.assertEqual(response.status_code, 302)
        self.client.logout()
        page = self.client.get(QUESADILLA_URL)
        self.assertContains(page, "2 blikken")
        self.assertContains(page, "Zwarte bonen")
        self.assertContains(page, "van 400gr")

    def test_the_ingredient_is_picked_from_the_ingredienten_there_already_are(self):
        # A text box here would let a second, near-empty "Ui" be typed next to
        # the real one, splitting everything that hangs off it -- and nobody
        # would notice until the ingrediëntpagina's showed up half empty.
        response = self.client.get(ADD_RECIPE)

        self.assertContains(response, f'<select name="{LINES}-0-ingredient"')

    def test_the_ingredientregels_are_there_when_the_recept_is_opened_again(self):
        self.write_quesadilla_with(
            ingredient_line_fields(
                self.beans.pk, quantity="2", unit=Unit.CAN, note="van 400gr"
            )
        )

        form = self.client.get(change_recipe("quesadilla-met-zoete-aardappel"))

        self.assertEqual(form.status_code, 200)
        self.assertContains(form, "Zwarte bonen")
        self.assertContains(form, "van 400gr")

    def test_a_typed_ingredient_name_is_refused(self):
        response = self.write_quesadilla_with(
            ingredient_line_fields("Zwarte bonen", quantity="2", unit=Unit.CAN)
        )

        # The form comes back instead of redirecting, and nothing was written.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get(QUESADILLA_URL).status_code, 404)

    def test_a_typed_unit_is_refused(self):
        # "blikken" beside "blik", "Stuks" beside "stuks": the vault this site
        # is written from has both, because it let the unit be typed.
        response = self.write_quesadilla_with(
            ingredient_line_fields(self.beans.pk, quantity="2", unit="blikken")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get(QUESADILLA_URL).status_code, 404)

    def test_an_eenheid_without_a_hoeveelheid_is_refused(self):
        # "stuk Goudse kaas" is what this combination renders as, which is
        # not a sentence. The author is asked about it while writing, rather
        # than a reader meeting it on the page.
        response = self.write_quesadilla_with(
            ingredient_line_fields(self.beans.pk, unit=Unit.CAN)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get(QUESADILLA_URL).status_code, 404)

    def test_an_ingredient_that_does_not_exist_yet_can_be_added_from_here(self):
        # Halfway through writing a recept is exactly when you meet an
        # ingrediënt the site has never seen. Leaving the page to add it would
        # mean losing what has been typed so far.
        response = self.client.get(ADD_RECIPE)

        self.assertContains(response, "/admin/recipes/ingredient/add/")

    def test_the_author_takes_an_ingredientregel_back_off_a_recept(self):
        self.write_quesadilla_with(
            ingredient_line_fields(self.beans.pk, quantity="2", unit=Unit.CAN)
        )
        # Arranging: the formset addresses a saved row by its key, so posting
        # the removal needs the key, the same way change_recipe() does.
        written = RecipeIngredient.objects.get()

        self.client.post(
            change_recipe("quesadilla-met-zoete-aardappel"),
            recipe_form(
                QUESADILLA,
                slug="quesadilla-met-zoete-aardappel",
                status=Recipe.Status.PUBLISHED,
                lines=[
                    ingredient_line_fields(
                        self.beans.pk,
                        quantity="2",
                        unit=Unit.CAN,
                        pk=written.pk,
                        delete=True,
                    )
                ],
            ),
        )

        self.client.logout()
        page = self.client.get(QUESADILLA_URL)
        self.assertEqual(page.status_code, 200)
        self.assertNotContains(page, "Zwarte bonen")

    def test_the_author_decides_what_order_the_regels_are_read_in(self):
        # The numbers decide, not the order the rows were filled in, so that
        # an ingrediënt remembered last does not have to be retyped to sit in
        # the middle of the list.
        self.write_quesadilla_with(
            ingredient_line_fields(
                self.beans.pk, quantity="2", unit=Unit.CAN, position=2
            ),
            ingredient_line_fields(
                Ingredient.objects.create(name="Tortilla").pk,
                quantity="12",
                unit=Unit.PIECE,
                position=1,
            ),
        )

        self.client.logout()
        html = self.client.get(QUESADILLA_URL).content.decode()
        self.assertLess(html.index("Tortilla"), html.index("Zwarte bonen"))


class StepAuthoringTests(TestCase):
    """Writing the steps of a recept, inline on the recept form."""

    def setUp(self):
        sign_in_as_the_author(self.client)

    def write_quesadilla_with(self, *steps):
        return self.client.post(
            ADD_RECIPE,
            recipe_form(QUESADILLA, status=Recipe.Status.PUBLISHED, steps=steps),
        )

    def test_the_recept_form_offers_a_stap_to_write(self):
        # The steps are written where the recept is written, in the author's
        # own language (ADR-0002), and not on a page of their own.
        response = self.client.get(ADD_RECIPE)

        self.assertContains(response, "Stappen")
        self.assertContains(response, f'name="{STEPS}-0-text"')

    def test_the_author_writes_the_steps_inside_the_recept(self):
        response = self.write_quesadilla_with(
            step_fields("Snijd de zoete aardappel in blokjes.", position=1),
            step_fields("Verhit een pan.", position=2),
        )

        self.assertEqual(response.status_code, 302)
        self.client.logout()
        page = self.client.get(QUESADILLA_URL)
        self.assertContains(page, "Snijd de zoete aardappel in blokjes.")
        self.assertContains(page, "Verhit een pan.")

    def test_the_author_says_which_fase_a_step_belongs_to(self):
        self.write_quesadilla_with(
            step_fields(
                "Snijd de zoete aardappel in blokjes.",
                position=1,
                phase="Mise en place",
            ),
            step_fields("Verhit een pan.", position=2, phase="Bakken"),
        )

        self.client.logout()
        page = self.client.get(QUESADILLA_URL)
        self.assertContains(page, "<h3>Mise en place</h3>", html=True)
        self.assertContains(page, "<h3>Bakken</h3>", html=True)

    def test_the_steps_are_there_when_the_recept_is_opened_again(self):
        self.write_quesadilla_with(
            step_fields("Verhit een pan.", position=1, phase="Bakken")
        )

        form = self.client.get(change_recipe("quesadilla-met-zoete-aardappel"))

        self.assertEqual(form.status_code, 200)
        self.assertContains(form, "Verhit een pan.")
        self.assertContains(form, "Bakken")

    def test_the_author_decides_what_order_the_steps_are_read_in(self):
        # A step remembered afterwards is given its number and drops into
        # place, rather than having to be retyped in the middle of the list.
        self.write_quesadilla_with(
            step_fields("Verhit een pan.", position=2),
            step_fields("Snijd de zoete aardappel in blokjes.", position=1),
        )

        self.client.logout()
        html = self.client.get(QUESADILLA_URL).content.decode()
        self.assertLess(html.index("Snijd de zoete"), html.index("Verhit een pan"))

    def test_a_step_that_moves_to_another_number_is_renumbered_on_the_page(self):
        # The page counts the steps itself, so reordering two of them leaves
        # a reader with 1, 2 and never with 2, 2.
        self.write_quesadilla_with(
            step_fields("Verhit een pan.", position=1),
            step_fields("Snijd de zoete aardappel in blokjes.", position=2),
        )
        written = {step.text: step.pk for step in Step.objects.all()}

        self.client.post(
            change_recipe("quesadilla-met-zoete-aardappel"),
            recipe_form(
                QUESADILLA,
                slug="quesadilla-met-zoete-aardappel",
                status=Recipe.Status.PUBLISHED,
                steps=[
                    step_fields(
                        "Verhit een pan.",
                        position=2,
                        pk=written["Verhit een pan."],
                    ),
                    step_fields(
                        "Snijd de zoete aardappel in blokjes.",
                        position=1,
                        pk=written["Snijd de zoete aardappel in blokjes."],
                    ),
                ],
            ),
        )

        self.client.logout()
        page = self.client.get(QUESADILLA_URL)
        self.assertContains(
            page,
            '<li id="stap-1" value="1">Snijd de zoete aardappel in blokjes.</li>',
            html=True,
        )
        self.assertContains(
            page, '<li id="stap-2" value="2">Verhit een pan.</li>', html=True
        )

    def test_the_author_takes_a_step_back_off_a_recept(self):
        self.write_quesadilla_with(step_fields("Verhit een pan.", position=1))
        # Arranging: the formset addresses a saved row by its key, the same
        # way the ingrediëntregel tests above do.
        written = Step.objects.get()

        self.client.post(
            change_recipe("quesadilla-met-zoete-aardappel"),
            recipe_form(
                QUESADILLA,
                slug="quesadilla-met-zoete-aardappel",
                status=Recipe.Status.PUBLISHED,
                steps=[
                    step_fields(
                        "Verhit een pan.", position=1, pk=written.pk, delete=True
                    )
                ],
            ),
        )

        self.client.logout()
        page = self.client.get(QUESADILLA_URL)
        self.assertEqual(page.status_code, 200)
        self.assertNotContains(page, "Verhit een pan.")


class IngredientAuthoringTests(TestCase):
    """Writing the ingrediënten themselves, which ingrediëntregels point at."""

    def setUp(self):
        sign_in_as_the_author(self.client)

    def offered_for(self, term):
        """The ingrediënten the dropdown on a recept offers for a search.

        The same request the browser makes while the author types into that
        dropdown, which is where the damage of a split ingrediënt would show
        up: two rows offered where there is one foodstuff.
        """
        answer = self.client.get(
            "/admin/autocomplete/",
            {
                "term": term,
                "app_label": "recipes",
                "model_name": "recipeingredient",
                "field_name": "ingredient",
            },
        )
        return [found["text"] for found in answer.json()["results"]]

    def test_the_dropdown_finds_the_ingredienten_there_already_are(self):
        Ingredient.objects.create(name="Zwarte bonen")
        Ingredient.objects.create(name="Witte bonen")

        self.assertEqual(self.offered_for("Zwarte"), ["Zwarte bonen"])

    def test_an_ingredient_name_cannot_be_used_twice(self):
        # One row per foodstuff is the whole point: a second "Zwarte bonen"
        # would split every ingrediëntregel, ingrediëntpagina and
        # boodschappenlijst that ever gathers them, unnoticed.
        Ingredient.objects.create(name="Zwarte bonen")

        response = self.client.post(
            "/admin/recipes/ingredient/add/",
            {"name": "Zwarte bonen", "slug": "", "is_staple": False},
        )

        # The form comes back rather than redirecting, and the dropdown still
        # offers the one ingrediënt it offered before.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.offered_for("bonen"), ["Zwarte bonen"])

    def test_the_form_says_how_specific_a_name_has_to_be(self):
        # ADR-0007 is a decision about the data, and the moment it is applied
        # is the moment a name is typed -- so it is on the form, not only in
        # a document nobody has open while writing a recept.
        response = self.client.get("/admin/recipes/ingredient/add/")

        self.assertContains(response, "Rode paprika")
