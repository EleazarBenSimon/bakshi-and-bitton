#!/usr/bin/env python3
"""
Build site data files from data/rulings/*.json.

Generates:
  - site/_data/rulings.json    — array of all rulings (for homepage + filtering)
  - site/_data/justices.json   — derived array of justice records (panel appearances)

Run from repo root after adding or modifying a ruling:
    python3 scripts/build.py

CI-friendly: stdlib only, exits 0 on success.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RULINGS_DIR = REPO_ROOT / "data" / "rulings"
JUSTICES_DIR = REPO_ROOT / "data" / "justices"
OUT_DIR = REPO_ROOT / "site" / "_data"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rulings = []
    for f in sorted(RULINGS_DIR.glob("*.json")):
        rulings.append(json.loads(f.read_text(encoding="utf-8")))

    rulings.sort(key=lambda r: r.get("ruling_date", ""), reverse=True)

    (OUT_DIR / "rulings.json").write_text(
        json.dumps(rulings, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    justices: dict[str, dict] = {}
    counts: dict[str, dict[str, int]] = defaultdict(lambda: {
        "panel_count": 0,
        "majority_authored": 0,
        "minority_authored": 0,
    })

    for ruling in rulings:
        rid = ruling["case_id_slug"]
        rdate = ruling.get("ruling_date")
        for j in ruling.get("panel", []):
            slug = j.get("slug")
            if not slug:
                continue
            if slug not in justices:
                justices[slug] = {
                    "slug": slug,
                    "name_he": j.get("name_he"),
                    "name_en": j.get("name_en"),
                    "appearances": [],
                }
            counts[slug]["panel_count"] += 1
            justices[slug]["appearances"].append({
                "case_id_slug": rid,
                "case_id": ruling.get("case_id"),
                "ruling_date": rdate,
                "role": j.get("role"),
                "outcome": ruling.get("outcome"),
                "authored_majority": slug in ruling.get("majority_authors", []),
                "authored_minority": slug in ruling.get("minority_authors", []),
            })
            if slug in ruling.get("majority_authors", []):
                counts[slug]["majority_authored"] += 1
            if slug in ruling.get("minority_authors", []):
                counts[slug]["minority_authored"] += 1

    justices_list = []
    for slug, j in sorted(justices.items()):
        j["panel_count"] = counts[slug]["panel_count"]
        j["majority_authored"] = counts[slug]["majority_authored"]
        j["minority_authored"] = counts[slug]["minority_authored"]
        j["appearances"].sort(key=lambda a: a.get("ruling_date", ""), reverse=True)
        justices_list.append(j)

    justices_list.sort(key=lambda x: x["panel_count"], reverse=True)

    (OUT_DIR / "justices.json").write_text(
        json.dumps(justices_list, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"✓ wrote {OUT_DIR/'rulings.json'} ({len(rulings)} rulings)")
    print(f"✓ wrote {OUT_DIR/'justices.json'} ({len(justices_list)} justices)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
