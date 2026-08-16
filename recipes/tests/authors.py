"""
Signing a test client in as Joost.

Not a test module -- `manage.py test` only collects `test*.py`. Two functions
rather than one because the difference between them is load-bearing, and they
sign in as two different accounts so that a test may use both.
"""

from django.contrib.auth import get_user_model


def sign_in_with_only_the_staff_flag(client):
    """Staff, and nothing else: no permissions, not a superuser.

    `is_staff` is the flag the concept preview keys on. Signing in as the
    superuser instead would pass whether the rule read `is_staff` or
    `is_superuser`, and so could not tell the two apart.
    """
    user = get_user_model().objects.create_user(
        username="joost-zonder-rechten",
        password="een-weggooiwachtwoord",
        is_staff=True,
    )
    client.force_login(user)
    return user


def sign_in_as_the_author(client):
    """The account Joost writes recepten with.

    A superuser, because that is what `ensure_superuser` creates on every
    deploy and what the admin's add and change forms need.
    """
    user = get_user_model().objects.create_superuser(
        username="joost",
        email="joost@example.com",
        password="een-weggooiwachtwoord",
    )
    client.force_login(user)
    return user
