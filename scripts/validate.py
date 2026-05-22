#!/usr/bin/env python3
"""
Validate all ruling JSON files against schemas/ruling.schema.json.

Run from repo root:
    python3 scripts/validate.py

CI-friendly: exits 0 on success, 1 if any errors.
No external dependencies — uses only the standard library.
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "ruling.schema.json"
RULINGS_DIR = REPO_ROOT / "data" / "rulings"


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_ruling(ruling: dict, schema: dict) -> list[str]:
    errors: list[str] = []
    required = schema["required"]
    props = schema["properties"]

    # Required fields
    for f in required:
        if f not in ruling:
            errors.append(f"missing required field: {f}")

    # Filename-slug match
    slug_pattern = re.compile(r"^[a-z0-9-]+$")
    if "case_id_slug" in ruling and not slug_pattern.match(ruling["case_id_slug"]):
        errors.append(f"case_id_slug invalid: {ruling['case_id_slug']!r}")

    # Enum checks
    def check_enum(value, key):
        if value is None:
            return
        allowed = props[key].get("enum")
        if allowed and value not in allowed:
            errors.append(f"{key}={value!r} not in {allowed}")

    check_enum(ruling.get("petitioner_type"), "petitioner_type")
    check_enum(ruling.get("respondent"), "respondent")
    check_enum(ruling.get("outcome"), "outcome")
    check_enum(ruling.get("compliance_state"), "compliance_state")

    # Doctrines array
    allowed_doctrines = props["doctrine_invoked"]["items"]["enum"]
    for d in ruling.get("doctrine_invoked", []):
        if d not in allowed_doctrines:
            errors.append(f"doctrine invalid: {d!r}")

    # Panel structure
    panel = ruling.get("panel", [])
    if not isinstance(panel, list) or not panel:
        errors.append("panel must be a non-empty array")
    else:
        for i, justice in enumerate(panel):
            if not all(k in justice for k in ("name_he", "name_en")):
                errors.append(f"panel[{i}] missing name_he or name_en")
            if "slug" in justice and not slug_pattern.match(justice["slug"]):
                errors.append(f"panel[{i}].slug invalid: {justice['slug']!r}")

    # Vote consistency (if both provided)
    vm = ruling.get("vote_majority")
    vn = ruling.get("vote_minority")
    if vm is not None and vn is not None:
        total = vm + vn
        if total != len(panel):
            errors.append(f"vote_majority + vote_minority = {total} ≠ panel size {len(panel)}")

    # Author slugs must reference panel slugs
    panel_slugs = {j.get("slug") for j in panel if j.get("slug")}
    for slug in ruling.get("majority_authors", []):
        if slug not in panel_slugs:
            errors.append(f"majority_authors references unknown slug: {slug!r}")
    for slug in ruling.get("minority_authors", []):
        if slug not in panel_slugs:
            errors.append(f"minority_authors references unknown slug: {slug!r}")

    # Summary length
    for fld in ("summary_he", "summary_en"):
        v = ruling.get(fld, "")
        if v and (len(v) < 20 or len(v) > 600):
            errors.append(f"{fld} length {len(v)} outside 20..600")

    return errors


def main() -> int:
    if not SCHEMA_PATH.exists():
        print(f"ERROR: schema not found at {SCHEMA_PATH}")
        return 2
    if not RULINGS_DIR.exists():
        print(f"ERROR: rulings directory not found at {RULINGS_DIR}")
        return 2

    schema = load_schema()
    files = sorted(RULINGS_DIR.glob("*.json"))
    if not files:
        print("WARNING: no ruling files found")
        return 0

    total_errors = 0
    for f in files:
        try:
            ruling = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"✗ {f.name}: invalid JSON — {e}")
            total_errors += 1
            continue

        # Filename-slug consistency
        expected_slug = f.stem
        if ruling.get("case_id_slug") != expected_slug:
            print(f"✗ {f.name}: case_id_slug ({ruling.get('case_id_slug')!r}) != filename ({expected_slug!r})")
            total_errors += 1

        errors = validate_ruling(ruling, schema)
        if errors:
            print(f"✗ {f.name}")
            for e in errors:
                print(f"    - {e}")
            total_errors += len(errors)
        else:
            print(
                f"✓ {f.name}: "
                f"{ruling.get('ruling_date','?')} | "
                f"{ruling.get('outcome','?')} {ruling.get('vote_majority','?')}-{ruling.get('vote_minority','?')} | "
                f"panel {len(ruling.get('panel',[]))}"
            )

    print(f"\n{len(files)} ruling(s) checked, {total_errors} error(s)")
    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
