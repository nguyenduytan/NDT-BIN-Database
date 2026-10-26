# Schema

| Field | Meaning |
|---|---|
| `bin` | 6 or 8 digit string identifier |
| `bin_length` | 6 or 8 |
| `scheme` | Card network, normalized uppercase |
| `type` | CREDIT, DEBIT, CHARGE or null |
| `level` | Product tier/category when available |
| `issuer` | Issuing institution when available |
| `country`, `country_code`, `country_code3` | Normalized issuer country |
| `prepaid` | true, false or null |
| `source_count` | Number of source families contributing the BIN |
| `conflict_fields` | Fields with contradictory observations |
| `updated_at` | Snapshot date |
