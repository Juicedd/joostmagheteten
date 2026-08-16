from django.shortcuts import get_object_or_404, render

from recipes.models import Recipe


def home(request):
    return render(request, "recipes/home.html")


def recipe_detail(request, slug):
    recipe = get_object_or_404(Recipe.objects.visible_to(request.user), slug=slug)
    return render(request, "recipes/recipe_detail.html", {"recipe": recipe})
