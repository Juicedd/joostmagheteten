"""
Posting the admin's recept form the way a browser does.

Not a test module -- `manage.py test` only collects `test*.py`. It lives here
because the recept form stopped being three fields the moment ingrediëntregels
and stappen were edited inside it: an inline formset only accepts a post that
carries its management fields, and every test that writes a recept now needs
them for both.
"""

from recipes.models import Recipe

ADD_RECIPE = "/admin/recipes/recipe/add/"

# Each inline formset names its fields after the accessor on Recipe.
LINES = "ingredient_lines"
STEPS = "steps"


def recipe_form(title, slug="", status=Recipe.Status.DRAFT, lines=(), steps=()):
    """The fields the admin's recept form posts.

    An empty slug is what the browser sends when the author has not touched
    the field and the prepopulate script has not run -- which is the case
    worth covering, because it is the one where the server has to fill it in.
    """
    return {
        "title": title,
        "slug": slug,
        "status": status,
        **formset_fields(LINES, lines),
        **formset_fields(STEPS, steps),
    }


def formset_fields(prefix, rows):
    """One inline formset's rows, and the management fields that carry them.

    A formset posted without these is not incomplete but unreadable: Django
    refuses the whole form rather than the one inline, so an empty inline
    still sends them.
    """
    saved = [row for row in rows if row.get("id")]
    fields = {
        f"{prefix}-TOTAL_FORMS": len(rows),
        f"{prefix}-INITIAL_FORMS": len(saved),
        f"{prefix}-MIN_NUM_FORMS": 0,
        f"{prefix}-MAX_NUM_FORMS": 1000,
    }
    for index, row in enumerate(rows):
        for field, value in row.items():
            fields[f"{prefix}-{index}-{field}"] = value
    return fields


def ingredient_line_fields(
    ingredient, quantity="", unit="", note="", position=0, pk="", delete=False
):
    """One row of the ingrediëntregel formset.

    `ingredient` is whatever the browser would send for that field, which is
    the key of an existing ingrediënt -- passing a name instead is exactly
    the mistake the form has to refuse. `pk` is empty for a row being added
    and the row's own key for one already saved, which is how the formset
    tells the two apart.
    """
    fields = {
        "ingredient": ingredient,
        "quantity": quantity,
        "unit": unit,
        "note": note,
        "position": position,
        "id": pk,
    }
    if delete:
        fields["DELETE"] = "on"
    return fields


def step_fields(text, position=0, phase="", pk="", delete=False):
    """One row of the stap formset, with `pk` working as it does above."""
    fields = {
        "text": text,
        "position": position,
        "phase": phase,
        "id": pk,
    }
    if delete:
        fields["DELETE"] = "on"
    return fields


def change_recipe(slug):
    """The admin URL for editing the recept with this slug.

    Arranging, not asserting: the admin addresses its pages by primary key,
    so reaching one needs the key, the same way these tests need a user row
    to sign in with.
    """
    return f"/admin/recipes/recipe/{Recipe.objects.get(slug=slug).pk}/change/"
