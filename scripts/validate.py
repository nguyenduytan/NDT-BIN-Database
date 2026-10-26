import csv, json, sqlite3
from pathlib import Path
rows=list(csv.DictReader(open("data/bins.csv",encoding="utf-8")))
assert rows and all(len(r["bin"]) in (6,8) and r["bin"].isdigit() for r in rows)
assert len(rows)==len({r["bin"] for r in rows})
assert json.load(open("data/manifest.json",encoding="utf-8"))["stats"]["rows"]==len(rows)
assert len(list(__import__('pathlib').Path('data/json').glob('*.json'))) >= 50
con=sqlite3.connect("data/bins.sqlite"); assert con.execute("select count(*) from bins").fetchone()[0]==len(rows); con.close()
print(f"validated {len(rows):,} rows")
