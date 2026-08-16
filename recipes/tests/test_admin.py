"""
Tests for access to the Django admin, which is the authoring surface.

See CLAUDE.md for how tests are written in this project. This module carries
the authenticated-client shape that later tickets copy for previewing a concept
recept and for driving the whole authoring flow.
"""

from django.test import TestCase

from recipes.tests.authors import sign_in_as_the_author


class AdminAccessTests(TestCase):
    def test_admin_redirects_anonymous_visitors_to_the_login_page(self):
        response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.headers["Location"])

    def test_admin_renders_for_a_superuser(self):
        sign_in_as_the_author(self.client)

        response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 200)
        # LANGUAGE_CODE reaches the admin too. Asserting the lang attribute
        # rather than a translated string on purpose: Django's own Dutch
        # wording can change between releases while the page is still
        # perfectly correct, and a test that breaks then is a bad test.
        self.assertContains(response, 'lang="nl"')

    def test_the_admin_calls_them_recepten(self):
        # Our own word rather than one of Django's translations, so this is
        # safe to assert on: per ADR-0002 the interface Joost reads is Dutch,
        # and the admin is the interface he spends the most time in.
        sign_in_as_the_author(self.client)

        response = self.client.get("/admin/")

        self.assertContains(response, "Recepten")
