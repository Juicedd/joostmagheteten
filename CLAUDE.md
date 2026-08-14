# joostmagheteten

## Agent skills

### Issue tracker

Issues live as GitHub issues, driven through the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical triage roles, using the default label strings (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — one `CONTEXT.md` and one `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Testing

This project has **one test seam: the HTTP boundary**, driven through Django's test client. This section is the single source of truth for that rule — `README.md` and the test modules point here rather than restating it.

- Assert only on what a visitor or an author observes through HTTP: status codes, rendered content, redirects, and **what is present and what is absent**.
- Never assert that a particular method was called, never inspect ORM internals, never mock.
- A test that breaks when the code behind a view is refactored, while the page still renders correctly, is a bad test.

`recipes/tests/` is the prior art every ticket copies. Two shapes carry most of the weight and are demonstrated there:

- **An authenticated client** (`force_login`) — for anything staff-only, including previewing a concept recept and the whole authoring flow.
- **Negative assertions** (`assertNotContains`, absence checks) — for anything that must never reach a visitor: oordelen, concept recepten, an absent bron.

Run the suite with `uv run python manage.py test`.
