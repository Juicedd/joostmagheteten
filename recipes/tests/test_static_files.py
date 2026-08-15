"""
Tests that the site serves the static files it asks for.

See CLAUDE.md for how tests are written in this project. These tests run with
DEBUG=False, which is what the deploy runs with -- so the path they exercise is
the deployed one: collectstatic writes the files, the template asks for a
hashed name, and WhiteNoise hands that file back over HTTP. `runserver` serves
static files a different way entirely, and is not what breaks in production.
"""

import re
import tempfile

from django.core.management import call_command
from django.test import TestCase

# The first static asset any page asks for -- the admin login page is used
# because it is the one page with static files that exists before any recept
# does.
STATIC_URL_IN_HTML = re.compile(rb'href="(/static/[^"]+\.css)"')


class StaticFileTests(TestCase):
    def setUp(self):
        static_root = self.enterContext(tempfile.TemporaryDirectory())
        self.enterContext(self.settings(STATIC_ROOT=static_root))
        call_command("collectstatic", "--no-input", verbosity=0)

    def fetch_stylesheet_of(self, path):
        page = self.client.get(path)
        match = STATIC_URL_IN_HTML.search(page.content)
        self.assertIsNotNone(match, f"{path} asks for no stylesheet at all")

        response = self.client.get(match.group(1).decode())
        # The file stays open until the response is closed, and Windows will
        # not delete the temporary STATIC_ROOT out from under an open handle.
        self.addCleanup(response.close)
        return response

    def test_a_stylesheet_the_page_asks_for_is_actually_served(self):
        response = self.fetch_stylesheet_of("/admin/login/")

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(b"".join(response.streaming_content), b"")

    def test_a_collected_asset_may_be_cached_forever(self):
        # Only safe because the collected name contains a hash of the content:
        # a changed file is a changed URL. Asserting the header rather than the
        # hash because the header is what a browser acts on.
        response = self.fetch_stylesheet_of("/admin/login/")

        self.assertIn("immutable", response.headers["Cache-Control"])
