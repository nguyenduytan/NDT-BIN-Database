# NDT BIN Database Implementation Plan

> Execute inline using superpowers:executing-plans. User approved implementation and push.

**Goal:** Publish a normalized, searchable, automatically refreshed BIN dataset.

**Architecture:** Source adapters feed deterministic whole-record normalization and
selection. A validated snapshot serves SQLite/CLI/API and static browser shards.

**Tech stack:** Python 3.11+, pycountry, SQLite, FastAPI, vanilla JavaScript, Actions.

**Spec:** ../specs/2026-10-26-bin-database-design.md

## Global constraints

- Preserve BinScrapper-main; create sibling NDT-BIN-Database.
- ASCII 6/8-digit string identifiers, null unknowns, no synthetic BIN expansion.
- No data-source names in README; attribution in notices and manifest.
- Never publish partial/empty datasets on network or validation failure.

## Tasks

- [ ] 1. Normalization and deterministic merge: tests/test_model.py and
  ndt_bin/model.py. Test leading zeros, invalid lengths, ISO aliases, unknowns,
  stable conflict selection and true/unknown prepaid. Run pytest before and after.
- [ ] 2. Sources and build: ndt_bin/sources.py, pipeline.py, export.py and
  tests/test_pipeline.py. Download CSV with header validation, source families,
  row-count gates; export sorted CSV/JSON/SQLite/shards/provenance; preserve old
  output on failure and timestamps on no-op rebuild.
- [ ] 3. Queries and CLI/API: ndt_bin/query.py, cli.py, api.py and tests/test_query.py.
  Verify combined filters, literal wildcard handling, page boundaries, safe sort,
  exact BIN lookup and explicitly marked 8-to-6 fallback.
- [ ] 4. Static explorer: web/index.html, style.css, app.js, worker.js and search.mjs.
  Test filter logic with node --test; verify rendered search, pagination, reset,
  downloads, loading and errors in a browser.
- [ ] 5. Release automation and docs: workflows ci.yml, refresh.yml, pages.yml;
  docs/schema.md, docs/integration.md, README.md, notices and licenses. Verify
  daily due checks and force refresh. Generate real-data stats in README.
- [ ] 6. Full build and publication: run pytest and node --test, rebuild twice,
  validate artifacts, commit, create public repo, push, configure Pages, inspect
  Actions outcomes and test public URLs. Report final counts and any blockers.
