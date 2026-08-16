"""
Tests for the public recept page.

See CLAUDE.md for how tests are written in this project -- one seam, the HTTP
boundary, and nothing asserted that a visitor could not observe. URLs are
written out in full here rather than reversed or read off the model, so that a
test disagrees with the code when the URL changes instead of moving with it.
"""

from django.test import TestCase

from recipes.models import Recipe
from recipes.tests.authors import sign_in_with_only_the_staff_flag


class RecipePageTests(TestCase):
    def test_a_published_recept_renders_at_its_own_dutch_url(self):
        Recipe.objects.create(
            title="Andijviestamppot met oude kaas",
            status=Recipe.Status.PUBLISHED,
        )

        response = self.client.get("/recepten/andijviestamppot-met-oude-kaas/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Andijviestamppot met oude kaas")

    def test_a_recept_is_a_concept_until_it_is_published(self):
        # No status given. The default has to be the invisible one: the
        # failure mode of the other default is a half-written recept going
        # public, which is not something you can take back once it is
        # indexed.
        Recipe.objects.create(title="Quesadilla met zoete aardappel")

        response = self.client.get("/recepten/quesadilla-met-zoete-aardappel/")

        self.assertEqual(response.status_code, 404)

    def test_a_concept_recept_is_not_found_by_a_visitor(self):
        # 404 and not 403 on purpose: a 403 tells the visitor there is
        # something there, which is exactly what a concept must not do.
        Recipe.objects.create(
            title="Quesadilla met zoete aardappel",
            status=Recipe.Status.DRAFT,
        )

        response = self.client.get("/recepten/quesadilla-met-zoete-aardappel/")

        self.assertEqual(response.status_code, 404)
        self.assertNotContains(
            response, "Quesadilla met zoete aardappel", status_code=404
        )

    def test_the_page_a_visitor_gets_instead_is_in_dutch(self):
        # This 404 is the most-seen visitor-facing response the recept page
        # has, and Django's built-in one is in English no matter what
        # LANGUAGE_CODE says.
        Recipe.objects.create(
            title="Quesadilla met zoete aardappel",
            status=Recipe.Status.DRAFT,
        )

        response = self.client.get("/recepten/quesadilla-met-zoete-aardappel/")

        self.assertContains(response, "Deze pagina bestaat niet", status_code=404)
        self.assertContains(response, 'lang="nl"', status_code=404)

    def test_a_concept_recept_renders_for_the_signed_in_author(self):
        # Writing a recept over several evenings means reading it back the
        # way a visitor eventually will, before it is public.
        Recipe.objects.create(
            title="Quesadilla met zoete aardappel",
            status=Recipe.Status.DRAFT,
        )
        sign_in_with_only_the_staff_flag(self.client)

        response = self.client.get("/recepten/quesadilla-met-zoete-aardappel/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Quesadilla met zoete aardappel")

    def test_a_previewed_concept_says_that_it_is_one(self):
        # Otherwise a preview is indistinguishable from the live page, and
        # "is this already public?" becomes a question you answer by signing
        # out.
        Recipe.objects.create(
            title="Quesadilla met zoete aardappel",
            status=Recipe.Status.DRAFT,
        )
        sign_in_with_only_the_staff_flag(self.client)

        response = self.client.get("/recepten/quesadilla-met-zoete-aardappel/")

        self.assertContains(response, "Concept")

    def test_a_published_recept_is_never_marked_as_a_concept(self):
        # Signed in as the one person who sees both kinds: the marker has to
        # follow the recept's status and not who is looking at it.
        Recipe.objects.create(
            title="Andijviestamppot met oude kaas",
            status=Recipe.Status.PUBLISHED,
        )
        sign_in_with_only_the_staff_flag(self.client)

        response = self.client.get("/recepten/andijviestamppot-met-oude-kaas/")

        self.assertNotContains(response, "Concept")


class RecipeUrlTests(TestCase):
    """The URL a recept gets, which is a promise once it has been shared."""

    def test_dutch_titles_with_diacritics_get_a_readable_ascii_url(self):
        # ADR-0006: e-with-diaeresis folds to e rather than being
        # percent-encoded into something nobody can read in a message.
        titles_and_urls = [
            (
                "Andijviestamppot met crème fraîche",
                "/recepten/andijviestamppot-met-creme-fraiche/",
            ),
            (
                "Vinaigrette met geëmulgeerde mosterd",
                "/recepten/vinaigrette-met-geemulgeerde-mosterd/",
            ),
            (
                "Soufflé van oude Goudse kaas",
                "/recepten/souffle-van-oude-goudse-kaas/",
            ),
        ]

        for title, url in titles_and_urls:
            with self.subTest(title=title):
                Recipe.objects.create(title=title, status=Recipe.Status.PUBLISHED)

                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, title)
