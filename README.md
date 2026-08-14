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

## Configuration

Every environment variable the project reads is documented in
[`.env.example`](.env.example). There is one settings module rather than a
per-environment split, and no secret is ever committed. The one credential you
will find in the repo is the throwaway Postgres password in
[`docker-compose.yml`](docker-compose.yml), which only ever guards a local
container.

Production hardening is not in `config/settings.py` yet — it lands with the
deploy in ticket #3. Until then the settings module is only safe to run locally.

Postgres runs locally as well as in production, deliberately. SQLite on a laptop
and Postgres in production is the difference that hides bugs until deploy day.

## Architecture decisions

- [ADR-0001](docs/adr/0001-django-database-is-canonical-obsidian-is-upstream.md) — the Django database is canonical; Obsidian is an upstream notebook
- [ADR-0002](docs/adr/0002-english-identifiers-dutch-interface.md) — English identifiers, Dutch interface
- [ADR-0003](docs/adr/0003-paid-render-with-photos-on-cloudflare-r2.md) — paid Render, photos on Cloudflare R2
- [ADR-0004](docs/adr/0004-no-ads-no-cookies-no-consent-banner.md) — no ads, no cookies, no consent banner
