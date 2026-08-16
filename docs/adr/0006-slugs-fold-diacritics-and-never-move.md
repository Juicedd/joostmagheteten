# Slugs fold diacritics to ASCII, and never move afterwards

A recept lives at `/recepten/<slug>/`, and the slug is derived from its Dutch title. Two things about that derivation are decided here, because both are cheap now and expensive once links exist in the world.

**Diacritics fold to ASCII.** `crème fraîche` becomes `creme-fraiche` and `geëmulgeerde` becomes `geemulgeerde`, which is what Django's `slugify()` does by default. The alternative, `slugify(allow_unicode=True)`, keeps the letters — and then the URL a visitor copies out of the address bar and pastes into a message is `/recepten/cr%C3%A8me-fra%C3%AEche/`, which is neither readable nor recognisable, and which is the whole point of having a Dutch URL in the first place. Django's `slug` path converter is ASCII-only too, so keeping the letters would mean a custom converter as well.

**A slug is set once and does not follow the title.** It is filled in from the title only while it is empty — on the model when saving, and in the admin form while typing. Rewriting the title of a recept that is already published leaves its URL exactly where it was.

## Consequences

Folding is lossy, so two titles can collide — `Soufflé` and `Souffle` produce the same slug. The slug is unique, so the second one fails to save rather than quietly overwriting anything, and Joost edits the slug or the title on the spot. Silently appending `-2` was rejected: on a site whose URLs are meant to be recognisable, a URL nobody chose is worse than an error message.

Because the slug does not follow the title, a recept whose title is rewritten early keeps a URL that no longer matches it. That is deliberate — the slug is an address, not a summary — and it is why the field stays editable in the admin, so a slug can still be corrected before anyone has the link.

Once a recept is published and shared, changing its slug breaks that link. There is no redirect machinery in v1, so this is a thing not to do rather than a thing that is handled.
