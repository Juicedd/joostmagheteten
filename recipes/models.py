"""
The recept and, in later tickets, what hangs off it.

Read CONTEXT.md before adding anything here: per ADR-0002 the identifiers are
English and the interface is Dutch, and the glossary is the only record of
which is which. Ingredient, RecipeIngredient and Step arrive in #5 and #6.
"""

from django.db import models
from django.utils.text import slugify


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


class Recipe(models.Model):
    """A recept: a finished set of instructions a stranger could cook from."""

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

    def save(self, *args, **kwargs):
        # Only when there is nothing there yet. Re-deriving the slug from an
        # edited title would silently change the URL of a recept that has
        # already been shared, and ADR-0006 is about not doing that.
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
