<div align="center">

# 💳 NDT BIN Database

### A normalized, searchable BIN/IIN dataset for developers

[![Quality](https://github.com/nguyenduytan/NDT-BIN-Database/actions/workflows/ci.yml/badge.svg)](https://github.com/nguyenduytan/NDT-BIN-Database/actions/workflows/ci.yml)
[![Refresh](https://github.com/nguyenduytan/NDT-BIN-Database/actions/workflows/refresh.yml/badge.svg)](https://github.com/nguyenduytan/NDT-BIN-Database/actions/workflows/refresh.yml)
[![License](https://img.shields.io/badge/code-MIT-22c55e.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776ab.svg)](https://www.python.org/)

**Lookup-ready metadata for BIN tools, websites, browser extensions and test environments.**

</div>

## 📊 Current stats

<div align="center">

| Records | Countries | Issuers | Schemes | Last update |
|:---:|:---:|:---:|:---:|:---:|
| 458,075 | 225 | 18,505 | 75 | 2026-10-26 |

</div>

## ✨ Features

- Stable 6 and 8 digit BIN/IIN strings with leading zeroes preserved.
- Normalized scheme, card type, level, issuer and ISO country metadata.
- Deterministic conflict handling with `source_count` and `conflict_fields`.
- CSV, JSON and SQLite downloads.
- CLI and FastAPI lookup with combined filters, pagination and safe sorting.
- Automated weekly refresh with quality gates and reproducible manifests.

## 📦 Downloads

- [`data/bins.csv`](data/bins.csv) — universal tabular import.
- [`data/json/`](data/json/) — application and extension integration, split into valid prefix shards.
- [`data/bins.sqlite`](data/bins.sqlite) — fast offline lookup.
- [`data/manifest.json`](data/manifest.json) — schema, stats, hashes and refresh metadata.

## 🚀 Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e ".[api,dev]"
ndt-bin --bin 004078 --scheme VISA --json
uvicorn ndt_bin.api:app --reload
```

API example:

```text
GET /api/v1/bins?country=US&scheme=VISA&type=DEBIT&page=1&page_size=25
```

## 🧭 Data contract

`bin` is always a string. Accepted values contain exactly 6 or 8 ASCII digits.
Unknown metadata is `null`. `scheme` is the card network; `type` is the product
type (`CREDIT`, `DEBIT`, `CHARGE` or `null`). `prepaid` is tri-state and is never
inferred as false just because a dataset omits it. A six digit record is never
expanded into a fabricated eight digit range.

This is metadata for development and lookup. It does not validate a payment card,
prove that an account exists, or authorize a transaction. Never store or submit a
full payment card number to this project.

## 🔁 Refresh

The scheduled workflow runs weekly and can also be started manually from the
Actions tab. It downloads into a staging directory, validates every input, and
publishes a new snapshot only after all artifacts pass validation. See
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for redistribution notices.

## 📄 License

Code is available under the MIT License. Dataset notices and attribution are kept
in the repository notice files and generated provenance manifest.

<div align="center">

Made with care by **NDT** · [nguyenduytan](https://github.com/nguyenduytan)

</div>
