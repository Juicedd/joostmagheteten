# The Django database is canonical; Obsidian is an upstream notebook

All content originates as notes in Joost's Obsidian vault, which already holds structured YAML frontmatter — so generating a static site directly from the vault looks like the obvious architecture, and it is the wrong one here. A recept only becomes a recept by being refined *on the website*: pantry ingredients filled in, quantities made honest, prose written for a stranger rather than for Joost. Making the vault canonical would push all of that editing back into Obsidian and delete the authoring surface the project exists to have.

We therefore keep a Django application with a database as the single source of truth for published recepten. A notitie in the vault is private raw material with no sync, no import contract, and no identity link to any recept.

## Considered Options

**Static site generated from the vault** (Hugo/Astro/11ty, or a Django `build` command). Rejected: it makes the vault canonical, which forces refinement to happen in Obsidian and turns the website into a read-only projection. It also cannot host the editing and scaling features that are the point.

**Sync between vault and site.** Rejected without much agonising: two writable stores for the same content is a conflict-resolution problem nobody asked for, and the vault genuinely is a scratchpad — most notities will never become recepten.

## Consequences

The website needs its own publication state, because refinement now happens on the site and half-finished recepten must not be publicly visible. Obsidian's own `status: to-develop` tag is vault-side only and carries no meaning here.

Getting a notitie into the site is a manual act by design. Any import tooling is a convenience that pre-fills a form — it must never establish an ongoing relationship between a notitie and a recept.
