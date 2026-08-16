"""
Tests for writing a recept in the Django admin.

See CLAUDE.md for how tests are written in this project. This module drives
the authoring surface the way Joost does -- signed in, posting the admin's own
forms -- and then checks the result the way a visitor sees it, over HTTP. The
tickets that add ingrediëntregels and steps extend these same flows with
inline formsets.
"""

from django.test import TestCase

from recipes.models import Recipe
from recipes.tests.authors import sign_in_as_the_author

ADD_RECIPE = "/admin/recipes/recipe/add/"


def recipe_form(title, slug="", status=Recipe.Status.DRAFT):
    """The fields the admin's recept form posts.

    An empty slug is what the browser sends when the author has not touched
    the field and the prepopulate script has not run -- which is the case
    worth covering, because it is the one where the server has to fill it in.
    """
    return {"title": title, "slug": slug, "status": status}


def change_recipe(slug):
    """The admin URL for editing the recept with this slug.

    Arranging, not asserting: the admin addresses its pages by primary key,
    so reaching one needs the key, the same way these tests need a user row
    to sign in with.
    """
    return f"/admin/recipes/recipe/{Recipe.objects.get(slug=slug).pk}/change/"


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
