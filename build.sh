#!/usr/bin/env bash
# Render runs this for every deploy -- see render.yaml.
#
# Everything the deployed environment needs in order to exist happens here, and
# none of it may need a human: this script is the only thing standing between
# an empty database and a working site. README.md ("Deploy") says why that
# matters while the database is free.
#
# A failing step fails the deploy, which leaves the previous version live.
set -o errexit

# --locked refuses to deploy a lockfile that does not match pyproject.toml.
uv sync --no-dev --locked

# Before anything touches the database: DEBUG, ALLOWED_HOSTS, HTTPS, cookies.
uv run --no-dev python manage.py check --deploy --fail-level WARNING

uv run --no-dev python manage.py collectstatic --no-input
uv run --no-dev python manage.py migrate
uv run --no-dev python manage.py ensure_superuser
