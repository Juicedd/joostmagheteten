"""
Posting the admin's recept form the way a browser does.

Not a test module -- `manage.py test` only collects `test*.py`. It lives here
because the recept form stopped being three fields the moment ingrediëntregels
were edited inside it: an inline formset only accepts a post that carries its
management fields, and every test that writes a recept now needs them.
"""

from recipes.models import Recipe

ADD_RECIPE = "/admin/recipes/recipe/add/"

# The inline formset names its fields after the accessor on Recipe, which is
# `ingredient_lines`.
LINES = "ingredient_lines"


def recipe_form(title, slug="", status=Recipe.Status.DRAFT, lines=()):
    """The fields the admin's recept form posts.

    An empty slug is what the browser sends when the author has not touched
    the field and the prepopulate script has not run -- which is the case
    worth covering, because it is the one where the server has to fill it in.
    """
    saved = [line for line in lines if line.get("id")]
    form = {
        "title": title,
        "slug": slug,
        "status": status,
        f"{LINES}-TOTAL_FORMS": len(lines),
        f"{LINES}-INITIAL_FORMS": len(saved),
        f"{LINES}-MIN_NUM_FORMS": 0,
        f"{LINES}-MAX_NUM_FORMS": 1000,
    }
    for index, line in enumerate(lines):
        for field, value in line.items():
            form[f"{LINES}-{index}-{field}"] = value
    return form


def ingredient_line_fields(
    ingredient, quantity="", unit="", note="", position=0, id="", delete=False
):
    """One row of the ingrediëntregel formset.

    `ingredient` is whatever the browser would send for that field, which is
    the key of an existing ingrediënt -- passing a name instead is exactly
    the mistake the form has to refuse.
    """
    fields = {
        "ingredient": ingredient,
        "quantity": quantity,
        "unit": unit,
        "note": note,
        "position": position,
        "id": id,
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
