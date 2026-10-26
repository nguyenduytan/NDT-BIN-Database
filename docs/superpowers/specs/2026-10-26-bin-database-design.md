# NDT BIN Database — approved design

Approved in conversation on 2026-10-26. Implement and publish to
nguyenduytan/NDT-BIN-Database without further design approval.

## Scope

Python 3.11+ package, SQLite query engine, CSV/JSON exports, static GitHub Pages
explorer, optional FastAPI server and GitHub Actions refresh. Preserve the original
BinScrapper-main directory; develop this project alongside it. The original informs
the workflow and has a separate legacy CSV import adapter. Its bundled scraped data
is not part of the default public build until redistribution terms are established.

## Data contract

One canonical record per exact BIN. Accept ASCII 6 or 8 digits as strings; reject
short prefixes rather than inventing zero padding. Fields: bin, bin_length, scheme,
type, level, issuer, country, country_code, country_code3, prepaid, source_count,
conflict_fields, updated_at. Unknown values are null. Country names and codes are
normalized together using ISO 3166. Non-ISO territories use explicit exceptions.
Scheme aliases map to stable uppercase values. Type is CREDIT, DEBIT, CHARGE,
PREPAID or null. Prepaid is true/false/null, never guessed false from absence.

Choose one complete normalized row by explicit source priority, completeness and
stable lexical tie-break. Never silently combine issuer/country/type from different
rows. Record conflicts and retain normalized observations in a separate artifact.
Counts describe source datasets, not independent verification or confidence.
Timestamps describe local metadata changes, not verification by a bank. Never
expand 6-digit records into fabricated 8-digit records.

## Pipeline

Download at least two independently maintained licensed public datasets plus a
community fork; record origin lineage so forks are not advertised as independent
corroboration. Validate headers, minimum counts and reject rates. Fail closed if a
required source is unavailable or published record count shrinks unexpectedly.
Build in a staging directory, validate all artifacts, then replace outputs.
Cache downloads locally but do not substitute cached data on failed refreshes.
Sort by BIN and preserve unchanged row timestamps for reproducible outputs.
Publish stats, a machine-readable manifest and SHA-256 hashes.

## Access

CLI and API share parameterized SQLite filters: exact BIN, prefix, country name or
ISO2/ISO3, issuer substring, scheme, type, level substring, BIN length, prepaid,
conflicts; allow combined filters, sorting, bounded pages and totals. Exact lookup
of 8 digits prefers 8-digit data, otherwise reports explicit 6-digit fallback.
Do not accept full PANs. Ship schema and JavaScript integration examples for future
website/extension consumption. No card-generation feature is part of this project.

The static explorer loads a small manifest, selects relevant two-digit prefix
shards and filters in a web worker. Broad filters require all relevant shards, with
progress, bounded concurrency, explicit loading/error/empty states and pagination.
All data is rendered with textContent. URL filters support shareable searches.

## Publication and documentation

Public repo NDT-BIN-Database; code MIT, data CC BY 4.0 with notices outside README.
README in English: centered icon headings and badges, usage, schema, downloads,
stats, dataset-update date and last successful refresh. Do not name data sources
in README. Preserve attribution in THIRD_PARTY_NOTICES.md and provenance manifest.
Actions check daily whether UPDATE_INTERVAL_DAYS (default 7) elapsed. Workflow
dispatch forces refresh. A successful check is distinct from a data change. Pages
deployment follows both initial push and successful scheduled refresh.

## Acceptance

Tests cover invalid input, leading zeros, aliases, missing data, contradictory
observations, exact/fallback lookup, combined filters, export parity, failure
preservation, idempotence and configurable schedule. Run a full real-data refresh,
query the actual database, test browser search and inspect Actions and Pages after
push. Report external authentication blockers honestly if any remain.
