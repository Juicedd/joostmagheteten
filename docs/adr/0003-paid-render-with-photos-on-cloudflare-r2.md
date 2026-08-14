# Paid Render for the app, Cloudflare R2 for the photos

The site runs on a **paid** Render Starter service with a paid Postgres, and recipe photos live in **Cloudflare R2** rather than on Render at all.

Render's free tier is unusable here for one specific reason: free services spin down after 15 minutes idle and cold-start in 30–60 seconds. The core use case is someone opening a recept at a hob with a pan already hot, and a minute of white screen is the single failure this site cannot have. Free Postgres also carries an expiry, which is wrong for content meant to last. Roughly $13/month, accepted deliberately.

Photos are on a second vendor because every Render option is worse. Without a disk, uploads are lost on the next deploy — a new instance has a fresh filesystem. With a disk, they survive, but a disk costs $0.25/GB/month, **removes zero-downtime deploys** (the old instance must stop before the new one starts, to avoid two versions writing to one disk), and permanently pins the service to a single instance. R2 is free to 10 GB with no egress charges, which at roughly 50 hero photos means free indefinitely.

## Consequences

Two vendors instead of one, and an S3-compatible storage backend (`django-storages`) configured against R2 from the first deploy rather than retrofitted. Being on Cloudflare already is also what makes Cloudflare Web Analytics the natural choice in ADR-0004.

Photo upload is never "just save the file" — there is no local filesystem to fall back on, including in development, unless a separate local storage backend is configured.
