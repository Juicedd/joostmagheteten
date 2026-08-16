# joostmagheteten

A Dutch-language recipe website. Joost writes the recepten; everyone else reads
and cooks from them.

Read [`CONTEXT.md`](CONTEXT.md) before writing any code. Per
[ADR-0002](docs/adr/0002-english-identifiers-dutch-interface.md) the code is in
English and the interface is in Dutch, and `CONTEXT.md` is the only record of
which English identifier means which Dutch domain term.

## Requirements

- [uv](https://docs.astral.sh/uv/) — dependency and environment management
- Docker — runs Postgres locally

## Setup

```bash
uv sync                          # create .venv and install dependencies
docker compose up -d db          # start Postgres
cp .env.example .env             # then fill in DJANGO_SECRET_KEY
uv run python manage.py migrate
uv run python manage.py createsuperuser
```

Generate a secret key with:

```bash
uv run python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

## Running

```bash
uv run python manage.py runserver
```

The site is at `http://127.0.0.1:8000/` and the authoring interface at
`http://127.0.0.1:8000/admin/`.

## Tests

```bash
uv run python manage.py test
```

This project has **one test seam: the HTTP boundary**, driven through Django's
test client. The rules for writing tests here live in
[`CLAUDE.md`](CLAUDE.md#testing) — that is the single source of truth, so it is
not restated in this file. `recipes/tests/` is the prior art to copy.

## Linting and formatting

```bash
uv run ruff check .          # report problems
uv run ruff check --fix .    # fix what can be fixed automatically
uv run ruff format .         # format
```

Line length is **88**, not the pycodestyle default of 79 — configured in
[`pyproject.toml`](pyproject.toml). If your editor is showing E501 warnings at
79 characters, point it at the project config.

## Configuration

Every environment variable the project reads is documented in
[`.env.example`](.env.example). There is one settings module rather than a
per-environment split, and no secret is ever committed. The one credential you
will find in the repo is the throwaway Postgres password in
[`docker-compose.yml`](docker-compose.yml), which only ever guards a local
container.

Production hardening — the HTTPS redirect, HSTS, secure cookies — hangs off
`DJANGO_SERVED_OVER_HTTPS`, which only the deploy sets. It is keyed off that
rather than off `DEBUG` because tests run with `DEBUG=False` too, and a laptop
has no HTTPS to redirect to.

Postgres runs locally as well as in production, deliberately — see
[ADR-0005](docs/adr/0005-postgres-locally-too.md).

## Deploy

The site runs on [Render](https://render.com), described by
[`render.yaml`](render.yaml) rather than by clicking around a dashboard.
**Pushing to `main` deploys**; there is no second step.

Every deploy runs [`build.sh`](build.sh), which stops at the first failure —
and a failed deploy leaves the previous version serving:

1. `uv sync --no-dev --locked` — the lockfile has to match `pyproject.toml`
2. `manage.py check --deploy` — fails the build on *any* warning, so the
   production settings cannot quietly regress
3. `collectstatic`, `migrate`, `ensure_superuser`

### Creating it the first time

In Render: **New → Blueprint**, point it at this repository, and fill in the
four values it asks for. They live in Render and are never committed:

| Variable | Value |
| --- | --- |
| `DJANGO_SECRET_KEY` | a fresh key from the generator command above |
| `DJANGO_SUPERUSER_USERNAME` | the name to log in to `/admin/` with |
| `DJANGO_SUPERUSER_EMAIL` | an address you can read |
| `DJANGO_SUPERUSER_PASSWORD` | a real password — changing it in the admin later is safe, deploys leave an existing account alone |

### While this is on the free plan

A free Render Postgres **expires 30 days after it is created**, with a 14-day
grace period, after which Render deletes it and everything in it. Per
[ADR-0001](docs/adr/0001-django-database-is-canonical-obsidian-is-upstream.md)
the Django database is canonical and a notitie in Obsidian is not a copy of a
recept — so until the paid Postgres arrives (#7), **nothing may live in the
deployed database that a push to `main` cannot put back**.

Which makes rebuilding it a routine rather than a disaster:

1. **Delete the database** in the Render dashboard. It has to go first — a
   workspace may only have one free Postgres at a time.
2. **Push a commit that changes `render.yaml`.** Any change will do.

Step 2 is not the same event as a normal deploy, and the difference is the one
worth knowing. A push deploys the *code* of a service that already exists. Only
a push that touches `render.yaml` makes Render **sync the Blueprint**, which is
what reconciles the resources — and a database that is in `render.yaml` but not
in the dashboard gets recreated by that sync. Push code alone after deleting
the database and the deploy will simply fail at `migrate`, against a
`DATABASE_URL` still pointing at a database that no longer exists.

(The **Manual Sync** button in the dashboard does the same job, but it only
appears once **Auto Sync** is set to **No** on the Blueprint's settings page.)

The sync recreates the database, rewrites `DATABASE_URL`, and redeploys. Watch
that build apply the migrations and print `Created superuser`, then log in. That
is also exactly what recovering from the 30-day expiry looks like, and it is
worth doing once on purpose.

The free web service sleeps after 15 minutes idle and takes about a minute to
wake — which is why it stays free only until there are visitors to feel it
([ADR-0003](docs/adr/0003-paid-render-with-photos-on-cloudflare-r2.md)).

## Architecture decisions

- [ADR-0001](docs/adr/0001-django-database-is-canonical-obsidian-is-upstream.md) — the Django database is canonical; Obsidian is an upstream notebook
- [ADR-0002](docs/adr/0002-english-identifiers-dutch-interface.md) — English identifiers, Dutch interface
- [ADR-0003](docs/adr/0003-paid-render-with-photos-on-cloudflare-r2.md) — paid Render, photos on Cloudflare R2
- [ADR-0004](docs/adr/0004-no-ads-no-cookies-no-consent-banner.md) — no ads, no cookies, no consent banner
- [ADR-0005](docs/adr/0005-postgres-locally-too.md) — Postgres on a laptop too, not SQLite
- [ADR-0006](docs/adr/0006-slugs-fold-diacritics-and-never-move.md) — slugs fold diacritics to ASCII, and never move afterwards
