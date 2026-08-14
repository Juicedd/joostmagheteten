"""
Tests for the home page.

See CLAUDE.md for how tests are written in this project -- one seam, the HTTP
boundary, and nothing asserted that a visitor could not observe.
"""

from django.test import TestCase


class HomePageTests(TestCase):
    def test_home_page_renders_in_dutch(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "joostmagheteten")
        self.assertContains(response, "Recepten om uit te koken")

    def test_home_page_declares_dutch_as_its_language(self):
        # Screen readers and search engines both read this attribute, so it is
        # behaviour rather than decoration.
        response = self.client.get("/")

        self.assertContains(response, 'lang="nl"')

    def test_home_page_sets_no_cookies(self):
        # ADR-0004: the site sets no cookies, which is what lets it have no
        # consent banner. This is the negative-assertion shape later tickets
        # copy for the cases that actually matter -- oordelen never reaching a
        # visitor, a concept recept never being readable.
        response = self.client.get("/")

        self.assertEqual(dict(response.cookies), {})
