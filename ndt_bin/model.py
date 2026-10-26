from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

import pycountry

SCHEMES = {"VISA": "VISA", "MASTER CARD": "MASTERCARD", "MASTERCARD": "MASTERCARD", "MC": "MASTERCARD", "AMERICAN EXPRESS": "AMEX", "AMEX": "AMEX", "CHINA UNION PAY": "UNIONPAY", "UNIONPAY": "UNIONPAY", "DISCOVER": "DISCOVER", "JCB": "JCB", "MAESTRO": "MAESTRO", "DINERS CLUB INTERNATIONAL": "DINERS CLUB"}
TYPES = {"CREDIT": "CREDIT", "DEBIT": "DEBIT", "CHARGE CARD": "CHARGE", "CHARGE": "CHARGE", "PREPAID": "DEBIT"}
NA = {"", "-", "N/A", "NA", "UNKNOWN", "NULL", "NONE"}

def _text(value: Any) -> str | None:
    if value is None: return None
    s = re.sub(r"\s+", " ", str(value).strip()).upper()
    return None if s in NA else s

def _country(value: Any, code: Any) -> tuple[str | None, str | None, str | None]:
    raw, raw_code = _text(value), _text(code)
    if raw_code == "UK": raw_code = "GB"
    obj = None
    if raw_code:
        obj = pycountry.countries.get(alpha_2=raw_code) or pycountry.countries.get(alpha_3=raw_code)
        if obj and raw:
            named = pycountry.countries.get(name=raw)
            if named and named.alpha_2 != obj.alpha_2:
                raise ValueError("country code and country name disagree")
    if not obj and raw:
        obj = pycountry.countries.get(name=raw)
        if not obj:
            try: obj = pycountry.countries.search_fuzzy(raw)[0]
            except LookupError: obj = None
    if obj and raw_code and obj.alpha_2 != raw_code:
        raise ValueError("country code and country name disagree")
    if not obj: return raw, raw_code, None
    return obj.name, obj.alpha_2, obj.alpha_3

def normalize(raw: dict[str, Any]) -> dict[str, Any]:
    value = raw.get("bin", raw.get("BIN", raw.get("bin_number")))
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{6}|[0-9]{8}", value):
        raise ValueError("bin must be an ASCII 6 or 8 digit string")
    scheme = _text(raw.get("scheme", raw.get("brand", raw.get("Brand"))))
    scheme = SCHEMES.get(scheme, scheme)
    card_type = _text(raw.get("type", raw.get("Type", raw.get("card_type"))))
    card_type = TYPES.get(card_type)
    level = _text(raw.get("level", raw.get("category", raw.get("Category"))))
    issuer = _text(raw.get("issuer", raw.get("bank", raw.get("Issuer"))))
    country, code2, code3 = _country(raw.get("country", raw.get("CountryName")), raw.get("country_code", raw.get("isoCode2", raw.get("alpha_2"))))
    prepaid_value = raw.get("prepaid")
    prepaid = None if prepaid_value is None else bool(prepaid_value) if isinstance(prepaid_value, bool) else (_text(prepaid_value) in {"TRUE", "YES", "1"})
    if prepaid is None and level and "PREPAID" in level: prepaid = True
    return {"bin": value, "bin_length": len(value), "scheme": scheme, "type": card_type,
            "level": level, "issuer": issuer, "country": country, "country_code": code2,
            "country_code3": code3, "prepaid": prepaid}

def merge(observations: list[tuple[str, int, dict[str, Any]]], previous: dict[str, dict[str, Any]], date: str) -> list[dict[str, Any]]:
    groups: dict[str, list[tuple[str, int, dict[str, Any]]]] = {}
    for source, priority, row in observations: groups.setdefault(row["bin"], []).append((source, priority, row))
    output = []
    for bin_value in sorted(groups):
        group = groups[bin_value]
        chosen = sorted(group, key=lambda x: (x[1], -sum(v is not None for v in x[2].values()), x[0]))[0][2]
        conflicts = []
        for field in ("scheme", "type", "level", "issuer", "country", "country_code", "country_code3", "prepaid"):
            values = {item[2].get(field) for item in group if item[2].get(field) is not None}
            if len(values) > 1: conflicts.append(field)
        row = deepcopy(chosen)
        old = previous.get(bin_value)
        row.update(source_count=len({x[0] for x in group}), conflict_fields=conflicts)
        row["updated_at"] = old.get("updated_at", date) if old and row == {k: old.get(k) for k in row} else date
        if old and all(row.get(k) == old.get(k) for k in row if k not in {"updated_at", "source_count", "conflict_fields"}):
            row["updated_at"] = old.get("updated_at", date)
        output.append(row)
    return output
