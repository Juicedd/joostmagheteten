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


def change_recipe(slug):
    """The admin URL for editing the recept with this slug.

    Reading the row back to build the URL is plumbing, not an assertion --
    the admin numbers its pages by primary key and there is no other way to
    address one.
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
            ADD_RECIPE,
            {
                "title": "Andijviestamppot met oude kaas",
                "slug": "",
                "status": Recipe.Status.DRAFT,
            },
        )

        self.assertEqual(response.status_code, 302)
        page = self.client.get("/recepten/andijviestamppot-met-oude-kaas/")
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Andijviestamppot met oude kaas")

    def test_a_recept_written_in_the_admin_is_not_public_yet(self):
        self.client.post(
            ADD_RECIPE,
            {
                "title": "Andijviestamppot met oude kaas",
                "slug": "",
                "status": Recipe.Status.DRAFT,
            },
        )
        self.client.logout()

        page = self.client.get("/recepten/andijviestamppot-met-oude-kaas/")

        self.assertEqual(page.status_code, 404)

    def test_publishing_a_recept_in_the_admin_makes_it_public(self):
        # Going live is a decision, not a side effect of finishing the text.
        self.client.post(
            ADD_RECIPE,
            {
                "title": "Andijviestamppot met oude kaas",
                "slug": "andijviestamppot-met-oude-kaas",
                "status": Recipe.Status.DRAFT,
            },
        )

        response = self.client.post(
            change_recipe("andijviestamppot-met-oude-kaas"),
            {
                "title": "Andijviestamppot met oude kaas",
                "slug": "andijviestamppot-met-oude-kaas",
                "status": Recipe.Status.PUBLISHED,
            },
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
            {
                "title": "Andijviestamppot",
                "slug": "andijviestamppot",
                "status": Recipe.Status.PUBLISHED,
            },
        )

        self.client.post(
            change_recipe("andijviestamppot"),
            {
                "title": "Andijviestamppot met oude kaas",
                "slug": "andijviestamppot",
                "status": Recipe.Status.PUBLISHED,
            },
        )

        self.client.logout()
        page = self.client.get("/recepten/andijviestamppot/")
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Andijviestamppot met oude kaas")

    def test_the_admin_calls_them_recepten(self):
        response = self.client.get("/admin/")

        self.assertContains(response, "Recepten")
