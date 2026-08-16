"""
Signing a test client in as Joost.

Not a test module -- `manage.py test` only collects `test*.py`. Two functions
rather than one because the difference between them is load-bearing: the
preview keys on `is_staff`, while writing a recept in the admin needs the
account Joost actually signs in with, which is the superuser that
`ensure_superuser` creates on every deploy.
"""

from django.contrib.auth import get_user_model


def sign_in_as_staff(client):
    """Staff, with no permissions at all -- the flag the preview keys on."""
    user = get_user_model().objects.create_user(
        username="joost",
        password="een-weggooiwachtwoord",
        is_staff=True,
    )
    client.force_login(user)
    return user


def sign_in_as_the_author(client):
    """The account Joost writes recepten with."""
    user = get_user_model().objects.create_superuser(
        username="joost",
        email="joost@example.com",
        password="een-weggooiwachtwoord",
    )
    client.force_login(user)
    return user
