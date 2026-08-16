from django.urls import path

from recipes import views

urlpatterns = [
    path("", views.home, name="home"),
    # Dutch, readable and shareable (story 18). The slug converter is
    # ASCII-only, which is the other half of why slugs fold diacritics --
    # see ADR-0006.
    path("recepten/<slug:slug>/", views.recipe_detail, name="recipe-detail"),
]
