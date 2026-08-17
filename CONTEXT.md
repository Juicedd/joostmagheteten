# joostmagheteten.nl

A Dutch-language recipe website. Joost writes and publishes the recipes; everyone else reads and cooks from them.

The domain language is **Dutch**. Terms below are the canonical Dutch words for each concept — use them in the glossary sense even when writing about the project in English, and never silently substitute an English synonym for a term that has been pinned here.

## Language

**Recept**:
A published, cookable set of instructions on the website. A recept is finished — it has been refined to the point where a stranger could cook from it without knowing Joost's kitchen.
_Avoid_: gerecht (that's the dish a recept produces, not the recept itself), notitie, recipe

**Notitie**:
A private note in Joost's Obsidian vault. A notitie is raw material that a recept may later be written from. It is not an early version of a recept and carries no identity relationship to one — there is no sync, and a notitie can change or vanish without the recept caring.
_Avoid_: draft, concept, bron

**Ingrediënt**:
A foodstuff as a thing in the world, independent of any recept — andijvie, goudse kaas, komijnpoeder. An ingrediënt carries its own Dutch-specific knowledge: season, storage, price bracket, flavour profile, what it pairs with. It is named at the level you buy it in a Dutch supermarket — rode paprika rather than paprika; verse peterselie and gedroogde peterselie rather than one peterselie. Where that level is unclear, name it more finely: too specific can be merged later, too broad cannot be split without recovering what nobody wrote down (ADR-0007). Basisingrediënten are the exception — see below. In code: `Ingredient` (ADR-0002).
_Avoid_: product, item (you buy an ingrediënt as a product, but never call it one)

**Ingrediëntregel**:
The use of one ingrediënt inside one recept, together with how much of it and any remark about it — "2 blikken zwarte bonen (van 400gr)". The quantity lives here, never on the ingrediënt, and its eenheid comes from a closed list rather than being typed. In code: `RecipeIngredient`, and `Unit` for the list.
_Avoid_: ingrediënt (an ingrediëntregel is a *use* of one, not one), regel

**Basisingrediënt**:
An ingrediënt assumed to be in the kitchen already — zout, peper, zonnebloemolie, standard dried spices. Still recorded on the recept in full, but presented apart from the shopping-relevant ingrediënten so a reader knows what they actually need to buy. The supermarket-level naming rule above does not reach a basisingrediënt: it is named as you would say it in a step — zout, not grof zeezout — because that rule exists to make a shopping list honest, and a basisingrediënt is the thing you never shop for. This merges variants of one staple, never two different ones: olijfolie and zonnebloemolie stay apart, as do komijnpoeder and komijnzaad. In code: `Ingredient.is_staple` is true — a property of the ingrediënt itself, not of any one use of it.
_Avoid_: pantry staple, kruiden, staple

**Bron**:
The existing recipe a recept was adapted from, when there is one. Recorded as an act of courtesy and honesty, not obligation.
_Avoid_: origineel, referentie, source

**Portie**:
The yield a recept's quantities are stated for. Every ingrediëntregel is implicitly "per this many porties", which is what makes scaling meaningful. In code: `Recipe.servings`.
_Avoid_: persoon, serving

**Totale tijd**:
The bereidingstijd plus the kooktijd, worked out every time it is read and never written down anywhere. A recept that stores all three has one that is wrong the moment a time is edited and the total forgotten. The two halves are whole minutes — a number, so that a recept can be compared, added up and filtered on; turning that into the Dutch a reader wants ("1 uur 30 minuten") is the page's job, not the database's. A total needs both halves: with one of them missing it would repeat the other under a different word, so there is nothing to say. In code: `Recipe.prep_minutes` and `Recipe.cook_minutes` are fields, and `Recipe.total_minutes` is deliberately not.
_Avoid_: bereidingstijd (that is one of the two halves, not the whole), duur

**Kerngegeven**:
One line of the block at the top of a recept that someone deciding whether to cook it reads first — a bereidingstijd, a portie-count, a seizoen. A recept shows only the kerngegevens it has: an empty one is left out rather than printed blank. Like a fase, a kerngegeven exists only where the page is being written: `Recipe.facts` builds the list and `Fact` is its shape. No oordeel is ever a kerngegeven.
_Avoid_: metadata, samenvatting, receptinfo

**Fase**:
A named group of consecutive steps within a recept's instructions — mise en place, the cooking itself, assembly. Fases group the steps but do not restart their numbering: a recept has one continuous sequence of steps, divided into fases. A recept that returns to an earlier fase gets a second stretch under that name rather than having its later steps lifted out of place to join the first. In code: the steps are `Step` rows on the recept, and the name of the fase is `Step.phase`, a label each step carries — grouping is then something the page does with them, and never something the numbering has to know about. The fase itself, name and steps together, exists only where the page is being written: `Recipe.phases` builds it and `Phase` is its shape. What a reader sees numbered is not `Step.position` either; that orders the steps, and the page counts them.
_Avoid_: sectie, deel, stage

**Kookmodus**:
The way a recept is presented to someone actually cooking it, as opposed to someone browsing or deciding. Kookmodus assumes a phone on a counter, at arm's length, with occupied hands — everything it does follows from that.
_Avoid_: kitchen mode, kookweergave

## Publicatie

Every recept is in exactly one of two states, and the boundary between them is the one the site cannot afford to get wrong.

**Concept**:
A recept Joost is still writing. It is in the database, editable and previewable by him, and invisible to everyone else — a visitor asking for one is told it does not exist rather than that they may not see it. Every recept starts as a concept. In code: `Recipe.status` is `draft` (ADR-0002).
_Avoid_: klad, notitie (a notitie is the private note in Obsidian and never becomes a concept — see above), draft in anything a reader sees

**Gepubliceerd**:
The single status that makes a recept public, reached by an explicit act rather than by finishing the text. It is an allowlist of exactly one: anything that is not gepubliceerd is invisible, including any status added later. In code: `Recipe.status` is `published`.
_Avoid_: live, online, af

## Classificatie en oordeel

Two kinds of metadata hang off a recept, and the difference between them decides what the public ever sees.

**Classificatie**:
A statement about a recept that any competent cook would broadly agree with — seizoen, gerechtstype, moeilijkheidsgraad. Classificaties are published and are the axes a visitor filters on. Each axis is a closed vocabulary, for the reason the eenheid is one: nothing filters on a word that was typed two ways. Seizoen and gerechtstype are **sets rather than single values** — a recept is lunch and hoofdgerecht at once, and one that suits the whole year carries all four seizoenen rather than a fifth value meaning "hele jaar door" that every filter would have to know to unpack. The page says "hele jaar door" when it sees all four. In code: `Recipe.difficulty` holds a `Difficulty`; `Recipe.seasons` and `Recipe.dish_types` hold lists of `Season` and `DishType`.
_Avoid_: tag, label, categorie

**Oordeel**:
Joost's personal opinion of a recept expressed as a number from 1 to 5 — voedingsscore, budgetscore, waardering. An oordeel is recorded for Joost's own use and is **never published**: it is an opinion dressed as a measurement, and publishing it would make a claim the site can't stand behind. Nothing in the code stops a template from printing one, so the guarantee is a test that renders the same recept with and without its oordelen and demands the two pages be identical — an absence cannot be checked by reading the template. In code: `Recipe.nutrition_score`, `Recipe.budget_score` and `Recipe.rating`, whose Dutch label is **waardering**.
_Avoid_: score, rating, beoordeling
