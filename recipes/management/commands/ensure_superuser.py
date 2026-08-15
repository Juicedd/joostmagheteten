"""
Create the author's account if the database has none yet.

Every deploy runs this (build.sh). Django ships `createsuperuser --noinput`,
which reads the same environment variables but fails when the account already
exists -- which would be every deploy after the first.

The account cannot be created by hand instead: Render's free instances have no
shell and no one-off jobs. README.md ("Deploy") has the rest of why.

This command lives in the recipes app only because a management command has to
live in an installed app, and that is the only one.
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create the author's superuser account unless it already exists."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")

        if not (username and email and password):
            # Loudly, rather than skipping: a deploy that quietly leaves the
            # site with no author account is the failure this command exists
            # to prevent.
            raise CommandError(
                "DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL and "
                "DJANGO_SUPERUSER_PASSWORD all have to be set, or the author "
                "has no account to log in with."
            )

        if get_user_model().objects.filter(username=username).exists():
            self.stdout.write(f"Superuser {username} already exists.")
            return

        get_user_model().objects.create_superuser(
            username=username, email=email, password=password
        )
        self.stdout.write(self.style.SUCCESS(f"Created superuser {username}."))
