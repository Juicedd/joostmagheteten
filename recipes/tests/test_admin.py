"""
Tests for access to the Django admin, which is the authoring surface.

See CLAUDE.md for how tests are written in this project. This module carries
the authenticated-client shape that later tickets copy for previewing a concept
recept and for driving the whole authoring flow.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase


class AdminAccessTests(TestCase):
    def test_admin_redirects_anonymous_visitors_to_the_login_page(self):
        response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.headers["Location"])

    def test_admin_renders_for_a_superuser(self):
        superuser = get_user_model().objects.create_superuser(
            username="joost",
            email="joost@example.com",
            password="een-weggooiwachtwoord",
        )
        self.client.force_login(superuser)

        response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 200)
        # LANGUAGE_CODE reaches the admin too. Asserting the lang attribute
        # rather than a translated string on purpose: Django's own Dutch
        # wording can change between releases while the page is still
        # perfectly correct, and a test that breaks then is a bad test.
        self.assertContains(response, 'lang="nl"')
