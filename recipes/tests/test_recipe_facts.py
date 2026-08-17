"""
Tests for what a recept tells someone deciding whether to cook it -- the
tijden, the porties and the classificaties -- and for the oordelen, which it
tells nobody.

See CLAUDE.md for how tests are written in this project. The oordeel tests at
the bottom are the reason this module exists: they assert an absence, and an
absence is the one thing that cannot be checked by reading the template.
"""

from django.test import TestCase

from recipes.models import Difficulty, DishType, Recipe, Season, Unit
from recipes.tests.arranging import ingredient_line, published_recipe, step
from recipes.tests.authors import sign_in_with_only_the_staff_flag

ANDIJVIE = "Andijviestamppot"
ANDIJVIE_URL = "/recepten/andijviestamppot/"


class RecipeTimeTests(TestCase):
    def test_a_recept_says_how_long_it_takes(self):
        published_recipe(ANDIJVIE, prep_minutes=20, cook_minutes=30)

        page = self.client.get(ANDIJVIE_URL)

        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Bereidingstijd")
        self.assertContains(page, "20 minuten")
        self.assertContains(page, "Kooktijd")
        self.assertContains(page, "30 minuten")

    def test_the_total_is_the_two_of_them_added_up(self):
        published_recipe(ANDIJVIE, prep_minutes=20, cook_minutes=30)

        page = self.client.get(ANDIJVIE_URL)

        self.assertContains(page, "Totale tijd")
        self.assertContains(page, "50 minuten")

    def test_the_times_are_written_the_way_they_are_said(self):
        # Stored as a number so it can be compared and added up, and read as
        # words, because "90 minuten" is a sum a reader has to do himself
        # while working out whether there is time tonight.
        said = [
            (1, "1 minuut"),
            (45, "45 minuten"),
            (60, "1 uur"),
            (90, "1 uur 30 minuten"),
            (120, "2 uur"),
        ]

        for minutes, expected in said:
            with self.subTest(minutes=minutes):
                published_recipe(f"Stoofpot van {minutes}", cook_minutes=minutes)

                page = self.client.get(f"/recepten/stoofpot-van-{minutes}/")

                self.assertContains(page, expected)

    def test_a_recept_with_only_one_of_the_two_does_not_repeat_it_as_a_total(self):
        # A total is prep plus cook. With one of the two missing there is
        # nothing to add up, and the same number twice under two different
        # words reads as a contradiction rather than as a sum.
        published_recipe(ANDIJVIE, prep_minutes=20)

        page = self.client.get(ANDIJVIE_URL)

        self.assertContains(page, "20 minuten")
        self.assertNotContains(page, "Totale tijd")

    def test_a_recept_without_times_says_nothing_about_time(self):
        published_recipe(ANDIJVIE)

        page = self.client.get(ANDIJVIE_URL)

        self.assertEqual(page.status_code, 200)
        self.assertNotContains(page, "Bereidingstijd")
        self.assertNotContains(page, "Kooktijd")
        self.assertNotContains(page, "Totale tijd")


class RecipeServingsTests(TestCase):
    def test_a_recept_says_how_many_it_feeds(self):
        published_recipe(ANDIJVIE, servings=4)

        page = self.client.get(ANDIJVIE_URL)

        self.assertContains(page, "Porties")
        self.assertContains(page, "4 porties")

    def test_a_recept_for_one_is_not_written_as_porties(self):
        published_recipe(ANDIJVIE, servings=1)

        page = self.client.get(ANDIJVIE_URL)

        self.assertContains(page, "1 portie")
        self.assertNotContains(page, "1 porties")

    def test_a_recept_without_porties_says_nothing_about_them(self):
        published_recipe(ANDIJVIE)

        page = self.client.get(ANDIJVIE_URL)

        self.assertNotContains(page, "Porties")
        self.assertNotContains(page, "porties")


class ClassificatieTests(TestCase):
    """The statements about a recept that are published (CONTEXT.md)."""

    def test_a_recept_says_how_hard_it_is(self):
        published_recipe(ANDIJVIE, difficulty=Difficulty.EASY)

        page = self.client.get(ANDIJVIE_URL)

        self.assertContains(page, "Moeilijkheidsgraad")
        self.assertContains(page, "makkelijk")

    def test_a_recept_says_which_seizoenen_it_suits(self):
        published_recipe(ANDIJVIE, seasons=[Season.AUTUMN, Season.WINTER])

        page = self.client.get(ANDIJVIE_URL)

        self.assertContains(page, "Seizoen")
        self.assertContains(page, "herfst, winter")

    def test_the_seizoenen_are_read_in_the_order_the_year_runs(self):
        # Ticked in whatever order they occurred to the author, and read in
        # the order they occur, so that two recepten never disagree about
        # what a year looks like.
        published_recipe(ANDIJVIE, seasons=[Season.WINTER, Season.SPRING])

        page = self.client.get(ANDIJVIE_URL)

        self.assertContains(page, "lente, winter")

    def test_a_recept_for_the_whole_year_says_so_in_one_breath(self):
        # All four is not a list of four seizoenen; it is the statement that
        # the seizoen does not matter, and that is one thing to say.
        published_recipe(
            ANDIJVIE,
            seasons=[Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER],
        )

        page = self.client.get(ANDIJVIE_URL)

        self.assertContains(page, "hele jaar door")
        self.assertNotContains(page, "lente, zomer")

    def test_a_recept_can_be_more_than_one_gerechtstype(self):
        # The worked example the spec is written from is lunch and
        # hoofdgerecht both, which is why this is a list and not a choice.
        published_recipe(ANDIJVIE, dish_types=[DishType.MAIN, DishType.LUNCH])

        page = self.client.get(ANDIJVIE_URL)

        self.assertContains(page, "Gerechtstype")
        self.assertContains(page, "lunch, hoofdgerecht")

    def test_a_recept_without_classificaties_shows_no_empty_row(self):
        published_recipe(ANDIJVIE)

        page = self.client.get(ANDIJVIE_URL)

        self.assertEqual(page.status_code, 200)
        self.assertNotContains(page, "Moeilijkheidsgraad")
        self.assertNotContains(page, "Seizoen")
        self.assertNotContains(page, "Gerechtstype")


# The words that would give an oordeel away if one ever reached a template,
# including the ones CONTEXT.md tells us not to use for it: a leak is just as
# bad under a name the glossary forbids.
OORDEEL_WORDS = [
    "voedingsscore",
    "budgetscore",
    "rating",
    "oordeel",
    "beoordeling",
    "score",
]


class OordeelTests(TestCase):
    """Joost's own numbers, which no visitor is ever shown (CONTEXT.md).

    An oordeel is an opinion dressed as a measurement. Publishing one would
    make a claim the site cannot stand behind, so these are the tests that
    have to keep working when everything else about the page changes.
    """

    def test_no_oordeel_reaches_a_reader(self):
        # Deliberately bare: with no times, porties or steps on it, the only
        # digits a recept page could carry are the ones in its head -- the 1
        # of initial-scale and the 8 of utf-8 -- so oordelen of 3, 4 and 5
        # can be looked for as digits and not merely as words.
        published_recipe(ANDIJVIE, nutrition_score=3, budget_score=4, rating=5)

        page = self.client.get(ANDIJVIE_URL)

        self.assertEqual(page.status_code, 200)
        self.assertNotContains(page, "3")
        self.assertNotContains(page, "4")
        self.assertNotContains(page, "5")

    def test_no_oordeel_is_named_on_a_finished_recept(self):
        # The whole page this time, with everything a recept can carry on it,
        # because a heading with nothing after it is a leak too.
        recipe = published_recipe(
            ANDIJVIE,
            prep_minutes=20,
            cook_minutes=30,
            servings=4,
            difficulty=Difficulty.EASY,
            seasons=[Season.WINTER],
            dish_types=[DishType.MAIN],
            nutrition_score=3,
            budget_score=4,
            rating=5,
        )
        ingredient_line(recipe, "Andijvie", quantity="500", unit=Unit.GRAM)
        step(recipe, 1, "Kook de aardappels gaar.", phase="Mise en place")

        page = self.client.get(ANDIJVIE_URL)

        self.assertEqual(page.status_code, 200)
        for word in OORDEEL_WORDS:
            with self.subTest(word=word):
                self.assertNotContains(page, word)
                self.assertNotContains(page, word.capitalize())

    def test_the_author_previewing_a_concept_is_shown_no_oordeel_either(self):
        # The preview is the page a visitor gets, so an oordeel that only
        # showed up here would be one that is a single publish away from
        # being public -- and nobody would be looking at that page again.
        Recipe.objects.create(
            title=ANDIJVIE,
            status=Recipe.Status.DRAFT,
            nutrition_score=3,
            budget_score=4,
            rating=5,
        )
        sign_in_with_only_the_staff_flag(self.client)

        page = self.client.get(ANDIJVIE_URL)

        self.assertEqual(page.status_code, 200)
        self.assertNotContains(page, "3")
        self.assertNotContains(page, "4")
        self.assertNotContains(page, "5")
