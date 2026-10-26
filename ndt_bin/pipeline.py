from __future__ import annotations
import csv, hashlib, io, json, sqlite3, urllib.request, shutil
from pathlib import Path
from .model import normalize, merge

SOURCES = [
    {"id":"primary", "priority":10, "url":"https://raw.githubusercontent.com/venelinkochev/bin-list-data/master/bin-list-data.csv", "format":"comma"},
    {"id":"secondary", "priority":20, "url":"https://raw.githubusercontent.com/iannuttall/binlist-data/master/binlist-data.csv", "format":"comma"},
    {"id":"community", "priority":30, "url":"https://raw.githubusercontent.com/marlonlp/binlist-data/master/binlist-data.csv", "format":"semicolon"},
]
FIELDS = ["bin","bin_length","scheme","type","level","issuer","country","country_code","country_code3","prepaid","source_count","conflict_fields","updated_at"]

def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent":"NDT-BIN-Database/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8-sig")

def read_rows(text: str, delimiter: str = ",") -> list[dict]:
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    if not reader.fieldnames or not any(str(x).lower() in {"bin", "bin_number"} for x in reader.fieldnames):
        raise ValueError("missing BIN column")
    return list(reader)

def build(out_dir: str | Path, date: str, urls: list[dict] | None = None, previous: list[dict] | None = None) -> dict:
    out = Path(out_dir)
    stage = out / ".staging"
    stage.mkdir(parents=True, exist_ok=True)
    observations, manifests = [], []
    for source in urls or SOURCES:
        raw = fetch(source["url"])
        rows = read_rows(raw, ";" if source.get("format") == "semicolon" else ",")
        normalized, rejected = [], 0
        for row in rows:
            try:
                normalized.append(normalize(row))
            except ValueError:
                rejected += 1
        if len(normalized) < 1000 or rejected > max(100, len(rows) // 10):
            raise ValueError(f"source quality gate failed: {source['id']}")
        observations.extend((source["id"], source["priority"], row) for row in normalized)
        manifests.append({"id":source["id"], "url":source["url"], "rows":len(rows), "accepted":len(normalized), "rejected":rejected, "sha256":hashlib.sha256(raw.encode()).hexdigest()})
    old = {row["bin"]: row for row in (previous or [])}
    rows = sorted(merge(observations, old, date), key=lambda row: row["bin"])
    data_stage = stage / "data"
    data_stage.mkdir(exist_ok=True)
    with (data_stage / "bins.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: "|".join(row[key]) if key == "conflict_fields" else row.get(key) for key in FIELDS})
    json_dir = data_stage / "json"
    json_dir.mkdir()
    shards = {}
    for row in rows:
        shards.setdefault(row["bin"][:2], []).append(row)
    for prefix, shard_rows in shards.items():
        (json_dir / f"{prefix}.json").write_text(json.dumps(shard_rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    conn = sqlite3.connect(data_stage / "bins.sqlite")
    conn.execute("CREATE TABLE bins (" + ", ".join(f"{field} TEXT" for field in FIELDS) + ")")
    conn.execute("CREATE INDEX idx_bins_bin ON bins(bin)")
    conn.execute("CREATE INDEX idx_bins_country ON bins(country_code)")
    conn.execute("CREATE INDEX idx_bins_scheme ON bins(scheme)")
    values = [tuple("|".join(row[key]) if key == "conflict_fields" else "true" if row[key] is True else "false" if row[key] is False else row.get(key) for key in FIELDS) for row in rows]
    conn.executemany("INSERT INTO bins VALUES (" + ",".join("?" for _ in FIELDS) + ")", values)
    conn.commit(); conn.close()
    stats = {"rows":len(rows), "countries":len({r["country_code"] for r in rows if r["country_code"]}), "issuers":len({r["issuer"] for r in rows if r["issuer"]}), "schemes":len({r["scheme"] for r in rows if r["scheme"]}), "updated_at":date}
    (data_stage / "manifest.json").write_text(json.dumps({"schema_version":"1.0", "generated_at":date, "stats":stats, "sources":manifests}, ensure_ascii=False, indent=2), encoding="utf-8")
    target = out / "data"
    target.mkdir(exist_ok=True)
    for path in data_stage.iterdir():
        path.replace(target / path.name)
    shutil.rmtree(stage, ignore_errors=True)
    return stats
