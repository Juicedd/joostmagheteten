"""
Static file storage for a project that collects static only when it deploys.

Django's manifest storage assumes `collectstatic` has run: every `{% static %}`
lookup goes through `staticfiles.json` and raises when the file is not in it.
That is exactly right on the deployed site, and wrong on a laptop and in the
test suite, where nothing has been collected and a page rendering at all is the
whole point.
"""

from whitenoise.storage import CompressedManifestStaticFilesStorage


class CollectedStaticFilesStorage(CompressedManifestStaticFilesStorage):
    """Hashed names where static has been collected, plain names where it hasn't."""

    def stored_name(self, name):
        # An empty manifest means static was never collected here, so there is
        # no hashed name to give -- hand back the plain one. A manifest that
        # exists but is missing this file is a broken deploy, and still raises.
        if not self.hashed_files:
            return name
        return super().stored_name(name)
