# No ads, no cookies, and therefore no consent banner

The site carries no advertising and sets no tracking cookies. Analytics is Cloudflare Web Analytics, which is cookieless and collects no personal data, so under AVG/GDPR no consent banner is required — and the site does not have one.

This is recorded because it is an explicit *no* that someone will eventually try to reverse, and because the three parts are load-bearing together. Adding an ad network, or swapping in Google Analytics, does not merely add a feature: it makes a consent banner legally necessary, and a Dutch-language site serving Dutch users has no wriggle room there.

The product reason matters more than the legal one. This site exists as an alternative to recipe sites where the recipe is buried under two thousand words of preamble — and that preamble exists *because of ad revenue*. Monetising would make the site into the thing it was built to replace. The arithmetic also doesn't work: food content earns roughly €5–15 per thousand pageviews, so covering $13/month hosting needs sustained traffic a new site with fifty recipes will not have.

## Consequences

Any future proposal to add advertising, embedded third-party widgets, or cookie-based analytics reopens this ADR first. The consent banner is not an implementation detail to be added later — its absence is a property of the design.
