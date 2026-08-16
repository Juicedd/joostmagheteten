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
A foodstuff as a thing in the world, independent of any recept — andijvie, goudse kaas, komijnpoeder. An ingrediënt carries its own Dutch-specific knowledge: season, storage, price bracket, flavour profile, what it pairs with. It is named at the level you buy it in a Dutch supermarket — rode paprika rather than paprika; verse peterselie and gedroogde peterselie rather than one peterselie. Where that level is unclear, name it more finely: too specific can be merged later, too broad cannot be split without recovering what nobody wrote down (ADR-0007). Basisingrediënten are the exception — see below.
_Avoid_: product, item (you buy an ingrediënt as a product, but never call it one)

**Ingrediëntregel**:
The use of one ingrediënt inside one recept, together with how much of it and any remark about it — "2 blikken zwarte bonen (van 400gr)". The quantity lives here, never on the ingrediënt.
_Avoid_: ingrediënt (an ingrediëntregel is a *use* of one, not one), regel

**Basisingrediënt**:
An ingrediënt assumed to be in the kitchen already — zout, peper, zonnebloemolie, standard dried spices. Still recorded on the recept in full, but presented apart from the shopping-relevant ingrediënten so a reader knows what they actually need to buy. The supermarket-level naming rule above does not reach a basisingrediënt: it is named as you would say it in a step — zout, not grof zeezout — because that rule exists to make a shopping list honest, and a basisingrediënt is the thing you never shop for. This merges variants of one staple, never two different ones: olijfolie and zonnebloemolie stay apart, as do komijnpoeder and komijnzaad.
_Avoid_: pantry staple, kruiden, staple

**Bron**:
The existing recipe a recept was adapted from, when there is one. Recorded as an act of courtesy and honesty, not obligation.
_Avoid_: origineel, referentie, source

**Portie**:
The yield a recept's quantities are stated for. Every ingrediëntregel is implicitly "per this many porties", which is what makes scaling meaningful.
_Avoid_: persoon, serving

**Fase**:
A named group of consecutive steps within a recept's instructions — mise en place, the cooking itself, assembly. Fases group the steps but do not restart their numbering: a recept has one continuous sequence of steps, divided into fases.
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
A statement about a recept that any competent cook would broadly agree with — seizoen, gerechtstype, moeilijkheidsgraad. Classificaties are published and are the axes a visitor filters on.
_Avoid_: tag, label, categorie

**Oordeel**:
Joost's personal opinion of a recept expressed as a number — voedingsscore, budgetscore, rating. An oordeel is recorded for Joost's own use and is **never published**: it is an opinion dressed as a measurement, and publishing it would make a claim the site can't stand behind.
_Avoid_: score, rating, beoordeling
