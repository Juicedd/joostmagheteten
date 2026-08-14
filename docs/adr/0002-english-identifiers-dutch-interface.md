# English identifiers in code, Dutch in the interface

This is a Dutch site with a Dutch domain language, and `CONTEXT.md` pins the canonical terms in Dutch — so the ubiquitous-language argument for Dutch model and field names is real, and we rejected it anyway. Code identifiers are English (`Recipe.source`, `RecipeIngredient.quantity`); everything a visitor reads is Dutch; the glossary stays Dutch and acts as the bridge between the two.

Two reasons decided it. `ë` is legal in Python identifiers but leaks badly into form field names, query parameters, JSON keys, and anything that normalises Unicode — and `ingrediënt` is unavoidable in Dutch. And the codebase is bilingual regardless the moment you write `Recept.objects.filter()`, so "all Dutch" was never actually on the table; the choice was between bilingual-with-a-clean-rule and bilingual-by-accident.

## Consequences

`CONTEXT.md` is load-bearing rather than decorative: it is the only place recording that `source` means **bron** and `RecipeIngredient` means **ingrediëntregel**. Anyone — human or agent — writing code here reads it first, or the two vocabularies drift apart.

UI strings are Dutch from the first commit. Retrofitting a language layer after writing English templates is the kind of tedious that never gets done.
