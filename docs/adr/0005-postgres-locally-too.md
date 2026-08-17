# Postgres on a laptop too, not SQLite

Development runs Postgres in a Docker container, the same engine production runs on Render. SQLite is never used, not even for a quick local run or in the test suite.

SQLite is genuinely the easier option: no Docker, no container to start, no port to keep free, just a file. We gave that up on purpose. When the laptop and the server run different databases, the differences do not announce themselves — they surface as a bug that only ever appears in production, on the one day you deploy. Case-sensitivity, transaction behaviour, migration edge cases, `NULL` ordering, date handling and constraint enforcement all differ, and each one costs more to debug remotely than Docker costs to run.

## Consequences

Docker is a genuine prerequisite for working on this project, and `docker compose up -d db` is a real step in setup. That cost is accepted.

The test suite needs a running Postgres, so tests cannot be run on a machine where the container is down. This is the intended trade: tests that exercise the real database are worth more than tests that run anywhere.

Since the classificaties (`Recipe.seasons`, `Recipe.dish_types`) are stored in Postgres array columns, this decision has stopped being merely prudent and become load-bearing: there is no longer a SQLite fallback to retreat to, and reopening this ADR now means reopening how a recept's classificaties are stored.
