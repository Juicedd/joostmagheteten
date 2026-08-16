"""
The recept and what hangs off it.

Read CONTEXT.md before adding anything here: per ADR-0002 the identifiers are
English and the interface is Dutch, and the glossary is the only record of
which is which -- Ingredient is an ingrediënt, RecipeIngredient is an
ingrediëntregel, `Step.phase` is a fase, and `is_staple` is what makes an
ingrediënt a basisingrediënt.
"""

from collections import namedtuple
from functools import cached_property
from itertools import groupby
from operator import attrgetter

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import Truncator, slugify


class PermanentSlug(models.Model):
    """A slug derived from a name once, and never moved again (ADR-0006).

    The models carry their own slug field, because the Dutch help text says
    which field it is made from; what they share is the promise that it stops
    following that field the moment it has a value.
    """

    slug_source_field = "name"

    class Meta:
        abstract = True

    def clean(self):
        # Before uniqueness is validated rather than after, so that two
        # names folding onto one slug is a Dutch error on the form the
        # author is looking at, and not an IntegrityError from save().
        super().clean()
        self.derive_slug()

    def save(self, *args, **kwargs):
        # Again, because writes that do not come from a form -- the tests,
        # an importer later -- never go through clean().
        self.derive_slug()
        super().save(*args, **kwargs)

    def derive_slug(self):
        """Fill the slug in, but only while there is none.

        Re-deriving it from an edited name would silently change the URL of
        a page that has already been shared, and ADR-0006 is about not
        doing that.
        """
        if not self.slug:
            self.slug = slugify(getattr(self, self.slug_source_field))


class RecipeQuerySet(models.QuerySet):
    def published(self):
        """The recepten a visitor may read.

        An allowlist, and it stays one: exactly one status is public and
        everything else -- including any status added later -- is invisible
        until someone decides otherwise here. The denylist version of this
        publishes the draft whose new status nobody remembered to exclude,
        and once that is indexed it cannot be taken back.
        """
        return self.filter(status=Recipe.Status.PUBLISHED)

    def visible_to(self, user):
        """The recepten `user` may read.

        Joost reads his own concepten back before publishing them; everyone
        else, signed in or not, sees exactly what has been published. Every
        public view goes through here, so the rule lives in one place.
        """
        if user.is_staff:
            return self
        return self.published()


class Recipe(PermanentSlug):
    """A recept: a finished set of instructions a stranger could cook from."""

    slug_source_field = "title"

    class Status(models.TextChoices):
        DRAFT = "draft", "Concept"
        PUBLISHED = "published", "Gepubliceerd"

    title = models.CharField("titel", max_length=200)
    slug = models.SlugField(
        "URL-naam",
        max_length=200,
        unique=True,
        blank=True,
        help_text=(
            "Wordt automatisch van de titel gemaakt. Verandert daarna niet "
            "meer mee met de titel, zodat gedeelde links blijven werken."
        ),
    )
    status = models.CharField(
        "publicatiestatus",
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        help_text="Alleen een gepubliceerd recept is zichtbaar voor bezoekers.",
    )

    objects = RecipeQuerySet.as_manager()

    class Meta:
        verbose_name = "recept"
        verbose_name_plural = "recepten"

    def __str__(self):
        return self.title

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED

    # Cached because the page asks each of these twice -- once to decide
    # whether the group is there at all, once to print it -- and a fresh
    # queryset each time would go back to the database for the same rows.
    @cached_property
    def shopping_lines(self):
        """The ingrediëntregels a reader actually has to buy."""
        return self.ingredient_lines.filter(ingredient__is_staple=False).select_related(
            "ingredient"
        )

    @cached_property
    def staple_lines(self):
        """The ingrediëntregels for basisingrediënten.

        Kept on the recept in full -- a recept states everything that goes
        into it -- but shown apart, so that what a reader has to shop for is
        not padded out with the zout they already own.
        """
        return self.ingredient_lines.filter(ingredient__is_staple=True).select_related(
            "ingredient"
        )

    @cached_property
    def phases(self):
        """The steps as the page prints them: each fase and what falls under it.

        Grouped on runs of the same fase rather than gathered per name,
        because a fase is a stretch of the sequence: a recept that returns to
        the hob after assembling something returns to a second stretch, and
        the steps in between may not be lifted out of their place to join it.

        A recept with no fases at all comes back as a single unnamed stretch,
        which the page prints as one plain list.
        """
        return [
            Phase(name, list(steps))
            for name, steps in groupby(self.numbered_steps, key=attrgetter("phase"))
        ]

    @cached_property
    def numbered_steps(self):
        """Every step of the recept, told where it falls in the whole.

        Counted here, over the recept, and never inside a fase, because that
        is the difference between "stap 8" meaning one thing and meaning
        three. Counted rather than read off `position`, so that a number the
        author skipped or typed twice while reordering cannot reach a reader
        as a list that runs 1, 2, 4.
        """
        steps = list(self.steps.all())
        for number, step in enumerate(steps, start=1):
            step.number = number
        return steps


class Ingredient(PermanentSlug):
    """An ingrediënt: a foodstuff as a thing in the world.

    One row per foodstuff, shared by every recept that uses it, which is why
    the name is unique and why nothing about a single use -- how much, cut
    how -- may live here.
    """

    name = models.CharField(
        "naam",
        max_length=100,
        unique=True,
        help_text=(
            "Zoals je het in de supermarkt koopt: 'Rode paprika', niet "
            "'Paprika'; 'Verse peterselie' en 'Gedroogde peterselie' apart. "
            "Twijfel je, kies dan het fijnere niveau (ADR-0007). Een "
            "basisingrediënt heet zoals je het in een stap zegt: 'Zout'."
        ),
    )
    slug = models.SlugField(
        "URL-naam",
        max_length=100,
        unique=True,
        blank=True,
        help_text=(
            "Wordt automatisch van de naam gemaakt. Verandert daarna niet "
            "meer mee met de naam, zodat gedeelde links blijven werken."
        ),
    )
    is_staple = models.BooleanField(
        "basisingrediënt",
        default=False,
        help_text=(
            "Staat al in de keuken -- zout, peper, zonnebloemolie, gedroogde "
            "kruiden. Wordt op het recept apart van de boodschappen getoond."
        ),
    )

    class Meta:
        verbose_name = "ingrediënt"
        verbose_name_plural = "ingrediënten"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Unit(models.TextChoices):
    """The units an ingrediëntregel may be measured in.

    A closed list, and that is the point: the vault this site is written
    from already holds `stuks` beside `Stuks` and `blik` beside `blikken`,
    because it let the unit be typed. It is also what makes scaling a recept
    to another portie-count possible later -- nothing can scale a unit it
    cannot recognise.

    English stored values and Dutch labels, the same way Recipe.Status is
    `draft` and reads "Concept" (ADR-0002).
    """

    GRAM = "gram", "gram"
    KILOGRAM = "kilogram", "kilogram"
    MILLILITER = "milliliter", "milliliter"
    LITER = "liter", "liter"
    TABLESPOON = "tablespoon", "eetlepel"
    TEASPOON = "teaspoon", "theelepel"
    PINCH = "pinch", "snufje"
    PIECE = "piece", "stuk"
    CLOVE = "clove", "teen"
    CAN = "can", "blik"
    JAR = "jar", "pot"
    PACK = "pack", "pak"
    BUNCH = "bunch", "bos"


# Only the units that are countable things; a Dutch recept says "600 gram"
# and "2 liter", but "2 blikken" and "4 tenen". Keyed by stored value rather
# than by member, because what comes back out of the database is a string.
PLURAL_UNITS = {
    Unit.TABLESPOON.value: "eetlepels",
    Unit.TEASPOON.value: "theelepels",
    Unit.PINCH.value: "snufjes",
    Unit.PIECE.value: "stuks",
    Unit.CLOVE.value: "tenen",
    Unit.CAN.value: "blikken",
    Unit.JAR.value: "potten",
    Unit.PACK.value: "pakken",
    Unit.BUNCH.value: "bossen",
}


class RecipeIngredient(models.Model):
    """An ingrediëntregel: the use of one ingrediënt inside one recept.

    Everything about that use lives here and not on the ingrediënt -- how
    much, in what unit, and the remark that makes it cookable ("van 400gr",
    "geraspt"). The same ingrediënt may appear twice in one recept, because
    a recept may well use olijfolie in two different places.
    """

    recipe = models.ForeignKey(
        Recipe,
        verbose_name="recept",
        on_delete=models.CASCADE,
        related_name="ingredient_lines",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name="ingrediënt",
        # An ingrediënt that recepten point at is not deletable by accident:
        # removing it takes the ingrediëntregels of every recept with it.
        on_delete=models.PROTECT,
        related_name="lines",
    )
    quantity = models.DecimalField(
        "hoeveelheid",
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            "Een getal, zodat het later mee kan schalen met de porties. "
            "Leeg laten mag: 'peper' met de opmerking 'naar smaak'."
        ),
    )
    unit = models.CharField(
        "eenheid",
        max_length=20,
        choices=Unit.choices,
        blank=True,
        help_text="Leeg laten als de hoeveelheid al genoeg zegt: '2 uien'.",
    )
    note = models.CharField(
        "opmerking",
        max_length=200,
        blank=True,
        help_text="Wat er nog bij hoort: 'van 400gr', 'geraspt', 'fijngesneden'.",
    )
    position = models.PositiveSmallIntegerField(
        "volgorde",
        default=0,
        help_text="Lage nummers staan bovenaan op het recept.",
    )

    class Meta:
        verbose_name = "ingrediëntregel"
        verbose_name_plural = "ingrediëntregels"
        # The author's order, and then the order they were written in, so
        # that two ingrediëntregels sharing a number never swap places
        # between two loads of the same page.
        ordering = ["position", "pk"]
        constraints = [
            # The same rule as clean() below, kept where a write that never
            # saw a form -- the importer ADR-0001 leaves room for -- still
            # runs into it.
            models.CheckConstraint(
                condition=models.Q(unit="") | models.Q(quantity__isnull=False),
                name="een_eenheid_heeft_een_hoeveelheid",
            )
        ]

    def __str__(self):
        return f"{self.amount} {self.ingredient}".strip()

    def clean(self):
        """An eenheid says nothing on its own.

        "stuk Goudse kaas" is not a sentence, and it is the sentence a unit
        with no quantity produces. Refused here rather than papered over
        while rendering, so that the recept is asked about it once, while it
        is being written.
        """
        super().clean()
        if self.unit and self.quantity is None:
            raise ValidationError(
                {
                    "unit": (
                        "Een eenheid zonder hoeveelheid zegt niets. Vul een "
                        "hoeveelheid in, of laat de eenheid leeg en zet het "
                        "in de opmerking ('naar smaak')."
                    )
                }
            )

    @property
    def amount(self):
        """What stands in front of the name: "2 blikken", "600 gram", "".

        Empty is a real answer -- zout naar smaak has no quantity -- and the
        page has to read properly without it.
        """
        return " ".join(part for part in (self.quantity_label, self.unit_label) if part)

    @property
    def quantity_label(self):
        """The quantity as Dutch writes it: 2, not 2.00; 0,5, not 0.5."""
        if self.quantity is None:
            return ""
        quantity = self.quantity.normalize()
        if quantity == quantity.to_integral_value():
            # normalize() turns 200 into 2E+2, which is true and unreadable.
            quantity = quantity.quantize(1)
        return f"{quantity}".replace(".", ",")

    @property
    def unit_label(self):
        """The unit, pluralised only where Dutch pluralises it.

        Dutch counts whole things in the plural -- 2 blikken, 4 tenen -- and
        leaves everything else singular: 1 blik, and 1,5 blik as well.
        """
        if not self.unit:
            return ""
        if self.counts_whole_things():
            return PLURAL_UNITS.get(self.unit, self.get_unit_display())
        return self.get_unit_display()

    def counts_whole_things(self):
        """More than one of something, and not a fraction of the next one."""
        if self.quantity is None or self.quantity <= 1:
            return False
        return self.quantity == self.quantity.to_integral_value()


# One fase and the run of steps standing under it, which is the shape the
# page loops over. `name` is empty for the steps the author gave no fase.
Phase = namedtuple("Phase", "name steps")


class Step(models.Model):
    """One instruction in a recept, standing under a fase.

    A recept has one sequence of steps from beginning to end. The fase is a
    label carried by the step rather than a group the step belongs to,
    because that is what keeps the numbering out of the grouping's hands: a
    fase names a stretch of the sequence, it does not start a new one
    (CONTEXT.md, "Fase").
    """

    recipe = models.ForeignKey(
        Recipe,
        verbose_name="recept",
        on_delete=models.CASCADE,
        related_name="steps",
    )
    position = models.PositiveSmallIntegerField(
        "volgorde",
        default=0,
        help_text=(
            "Bepaalt de volgorde, niet het nummer: lage nummers staan "
            "bovenaan, en de pagina telt de stappen zelf -- doorlopend over "
            "de fases heen. Gaten en dubbele nummers ziet een lezer dus niet."
        ),
    )
    phase = models.CharField(
        "fase",
        max_length=100,
        blank=True,
        help_text=(
            "De kop waar deze stap onder hoort: 'Mise en place', 'Bouwen'. "
            "Stappen die op elkaar volgen en dezelfde fase hebben, komen "
            "onder één kop te staan. Leeg laten mag."
        ),
    )
    text = models.TextField(
        "stap",
        help_text="Eén handeling, geschreven voor iemand die jouw keuken niet kent.",
    )

    # Where this step falls in its recept, which is not a field: it is a fact
    # about the whole sequence, and only Recipe.numbered_steps can count it.
    # A step that never went through there has no number to print, which is
    # why the page reaches the steps through Recipe.phases and not otherwise.
    number = None

    class Meta:
        verbose_name = "stap"
        verbose_name_plural = "stappen"
        # The author's order, and then the order they were written in, so that
        # two steps sharing a number never swap places between two loads of
        # the same page -- the same tie-break the ingrediëntregels use.
        ordering = ["position", "pk"]

    def __str__(self):
        # A step is a sentence, and the admin shows this in places built for a
        # label: the object history, a delete confirmation.
        return Truncator(self.text).chars(70)
