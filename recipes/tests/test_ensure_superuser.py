"""
Tests for the author account that the deploy creates.

See CLAUDE.md for how tests are written in this project. The command is run
here the way the deploy runs it -- credentials in the environment -- and every
assertion is about what an author observes at the login page, never about what
is in the users table.

Why the deploy creates the account at all is in the command's own docstring.
"""

import os
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

USERNAME = "joost"
EMAIL = "joost@example.com"
PASSWORD = "een-weggooiwachtwoord"


class EnsureSuperuserTests(TestCase):
    def deploy(self, password=PASSWORD):
        """Run the command the way build.sh does, on this environment."""
        credentials = {
            "DJANGO_SUPERUSER_USERNAME": USERNAME,
            "DJANGO_SUPERUSER_EMAIL": EMAIL,
            "DJANGO_SUPERUSER_PASSWORD": password,
        }
        for name, value in credentials.items():
            os.environ[name] = value
            self.addCleanup(os.environ.pop, name, None)

        # Its report goes to the deploy log, which is not what these tests are
        # about, so it goes nowhere here.
        call_command("ensure_superuser", stdout=StringIO())

    def log_in(self, password):
        return self.client.post(
            "/admin/login/",
            {"username": USERNAME, "password": password, "next": "/admin/"},
        )

    def test_the_author_can_log_in_to_the_admin_after_a_deploy(self):
        self.deploy()

        self.assertRedirects(self.log_in(PASSWORD), "/admin/")
        # A staff account that is not a superuser reaches the admin index too,
        # but with nothing on it. The link to the user list is only there for
        # an account that can administer everything.
        self.assertContains(self.client.get("/admin/"), "/admin/auth/user/")

    def test_a_password_the_author_changed_survives_the_next_deploy(self):
        self.deploy()
        self.log_in(PASSWORD)
        new_password = "een-ander-weggooiwachtwoord"
        self.client.post(
            "/admin/password_change/",
            {
                "old_password": PASSWORD,
                "new_password1": new_password,
                "new_password2": new_password,
            },
        )
        self.client.logout()

        # The deploy environment still carries the password the account was
        # created with. Redeploying must not hand it back.
        self.deploy()

        self.assertRedirects(self.log_in(new_password), "/admin/")
