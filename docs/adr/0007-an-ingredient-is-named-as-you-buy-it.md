# An ingrediënt is named at the level you buy it, and finer when in doubt

Nothing so far says how specific one ingrediënt is. The vault's first recept calls for `Paprika` with the remark *"Rood en Groen beste combi"*, and `Zwarte Bonen` measured in blikken. Both readings are defensible: one ingrediënt named `Paprika`, or two named `Rode paprika` and `Groene paprika`. `CONTEXT.md` did not settle it either — its own examples pull both ways, since *goudse kaas* is a variety and *andijvie* is a whole foodstuff.

The question has to be answered before ingrediëntregels are built, because that is the ticket that starts creating ingrediënten, and twenty recepten of regels later the answer is fixed by the data.

**An ingrediënt is named at the level you buy it in a Dutch supermarket.** Rode paprika, goudse kaas, zwarte bonen, andijvie. The rule cuts on form as well as on variety: verse peterselie and gedroogde peterselie are two ingrediënten, not one.

**Where that level is unclear, name it more finely.** Supermarkets do not agree with each other and their assortments change, so this rule identifies no exact set and is not meant to — it is meant to fail in the recoverable direction. Merging two ingrediënten later is repointing the regels that reference them, and nothing is lost that was not already in the name. Splitting one later means revisiting every regel to recover a distinction that was never recorded anywhere, which is not a migration but an act of memory.

**Basisingrediënten are exempt**, and are named as you would say them in a step: `Zout`, not `Grof zeezout`. The reason to name finely is so that a shopping list is honest, and a basisingrediënt is defined as the thing excluded from that list. The exemption merges variants of a single staple and nothing else — olijfolie and zonnebloemolie remain separate ingrediënten, as do komijnpoeder and komijnzaad, because those are different foodstuffs rather than one foodstuff sold in variants.

## Considered options

**Name coarsely — one `Paprika`, one `Peterselie` — and put the distinction in the regel's note.** Rejected on two counts. The stronger one is that the database is expected to be read by an agent later: a `Paprika` row whose colour lives in Dutch free text is opaque to anything that did not write it, while `Rode paprika` describes itself. The second is `is_staple`, which sits on the ingrediënt and not on the regel: gedroogde peterselie is a basisingrediënt and verse peterselie is shopping, so a single `Peterselie` is guaranteed to be wrong for one of them.

**Move `is_staple` down to the ingrediëntregel** so that a coarse ingrediënt can be a staple in one recept and not in another. Rejected: it reverses a decision the spec made deliberately, and it solves only the peterselie symptom while leaving the colour of the paprika just as unrecoverable.

**Name one supermarket as the reference** and resolve ambiguity by looking at its assortment. Rejected: it binds the domain model to one retailer's shelves, which change without telling us, and it answers a question about our own vocabulary by consulting somebody else's.

**Give ingrediënten a parent concept**, so that verse and gedroogde peterselie could split while sharing one ingrediëntpagina. Rejected as premature: not one ingrediëntpagina has been written yet, and this invents a hierarchy to solve a problem nobody has met.

## Consequences

There will be more ingrediënten than a coarser rule would produce, and some of them will look pedantically similar. That is the intended cost.

An ingrediëntpagina — deferred to v2, and the feature that will make the site distinctive — inherits this granularity. The page for verse peterselie is about verse peterselie, and there is no page about peterselie in general. If that turns out to be the wrong shape once real pages exist, merging is the cheap direction, which is the direction this decision leaves open.

Ingrediënt slugs follow the names, and ADR-0006 says a slug does not move once set. Renaming an ingrediënt after its page is public therefore costs a broken link, which is a further reason to be specific from the first row rather than to sharpen names later.

The rule is a default with a defined fall-direction, not a specification. Joost overrides it where the supermarket is genuinely ambiguous; the fall-direction says which way to override.
