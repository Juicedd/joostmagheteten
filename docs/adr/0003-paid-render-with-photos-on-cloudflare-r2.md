# Paid Render for the app, Cloudflare R2 for the photos

The site runs on a **paid** Render Starter service with a paid Postgres, and recipe photos live in **Cloudflare R2** rather than on Render at all.

Render's free tier is unusable here for one specific reason: free services spin down after 15 minutes idle and cold-start in 30–60 seconds. The core use case is someone opening a recept at a hob with a pan already hot, and a minute of white screen is the single failure this site cannot have. Free Postgres also carries an expiry, which is wrong for content meant to last. Roughly $13/month, accepted deliberately.

Photos are on a second vendor because every Render option is worse. Without a disk, uploads are lost on the next deploy — a new instance has a fresh filesystem. With a disk, they survive, but a disk costs $0.25/GB/month, **removes zero-downtime deploys** (the old instance must stop before the new one starts, to avoid two versions writing to one disk), and permanently pins the service to a single instance. R2 is free to 10 GB with no egress charges, which at roughly 50 hero photos means free indefinitely.

## When the paid plans start

The build phase runs on the free tier, and that is not a departure from the decision above — the reasoning above is entirely about *visitors*, and during the build there are none. Both free and paid Render services get an `onrender.com` subdomain, and custom domains are free on either plan, so the plan is what costs money and the address never was. The deploy pipeline is therefore proven for nothing in #3, and the two paid plans start at different moments:

- **Postgres** upgrades in #7, before the deployed database holds a recept that is not still upstream in Obsidian. A free Postgres expires 30 days after creation, with a 14-day grace period, after which Render deletes it and its data — and per ADR-0001 the Django database is canonical. Until then the deployed database must stay reproducible from migrations, which #3 verifies rather than assumes.
- **The Starter instance** upgrades in #12, at launch. The cold start is what a visitor at a hob would feel; while there are no visitors, a minute of white screen costs nothing.

## Consequences

Two vendors instead of one, and an S3-compatible storage backend (`django-storages`) configured against R2 from the first deploy rather than retrofitted. Being on Cloudflare already is also what makes Cloudflare Web Analytics the natural choice in ADR-0004.

Photo upload is never "just save the file" — there is no local filesystem to fall back on, including in development, unless a separate local storage backend is configured.
