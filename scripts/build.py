#!/usr/bin/env python3
"""
Build site data files from data/rulings/*.json and content/*.md.

Generates:
  - site/_data/rulings.json    — array of all rulings (for homepage + filtering)
  - site/_data/justices.json   — derived array of justice records (panel appearances)
  - site/_data/content.json    — informative content layer (explainers / patterns / essays)
                                  with markdown converted to HTML for rendering

Run from repo root after adding or modifying a ruling or a content piece:
    python3 scripts/build.py

Dependencies:
    - markdown (for content/*.md → HTML conversion). Install: pip3 install --user markdown
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    import markdown as md
except ImportError:
    print("ERROR: python 'markdown' package not installed.", file=sys.stderr)
    print("Install with: pip3 install --user markdown", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
RULINGS_DIR = REPO_ROOT / "data" / "rulings"
JUSTICES_DIR = REPO_ROOT / "data" / "justices"
CONTENT_DIR = REPO_ROOT / "content"
OUT_DIR = REPO_ROOT / "site" / "_data"

# Categories shown in the Reading section, in display order.
CONTENT_CATEGORIES = ["essays", "explainers", "patterns"]


# ─── Helpers ─────────────────────────────────────────────────────────────

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """
    Parse YAML-ish frontmatter from a markdown file.

    Handles only the subset used in this project (single-line key: value pairs,
    optional surrounding quotes). Returns (meta_dict, remaining_body).
    """
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    fm_text, body = m.group(1), m.group(2)
    meta: dict[str, str] = {}
    for line in fm_text.split("\n"):
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        val = val.strip()
        if (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        ):
            val = val[1:-1]
        meta[key.strip()] = val
    return meta, body


def markdown_to_html(body: str) -> str:
    """Convert markdown to HTML with extensions appropriate for our content."""
    return md.markdown(
        body,
        extensions=[
            "tables",          # the pattern document uses tables
            "fenced_code",     # for any ``` blocks
            "attr_list",       # so we can target classes if needed later
            "sane_lists",      # better list handling
            "smarty",          # smart quotes / dashes
        ],
        output_format="html5",
    )


def relativize_internal_links(html: str) -> str:
    """
    Rewrite internal repo paths into site URLs where reasonable.

    The content files use relative paths like ../../data/rulings/X.json (which
    don't make sense on a public website). For now we strip these to plain
    anchor text and keep external https:// links as-is.
    """
    # Convert <a href="../../data/rulings/foo.json">text</a> -> <strong>text</strong>
    html = re.sub(
        r'<a href="\.\./\.\./data/rulings/[^"]+"[^>]*>(.*?)</a>',
        r"<strong>\1</strong>",
        html,
    )
    html = re.sub(
        r'<a href="(?:\.\./)*data/[^"]+"[^>]*>(.*?)</a>',
        r"<strong>\1</strong>",
        html,
    )

    # Cross-content references: ../patterns/foo.md or ../explainers/foo.md
    # Rewrite to in-site links: content.html?slug=foo
    def cross_content(m):
        path = m.group(1)
        anchor = m.group(2)
        slug_match = re.search(r"/([^/]+)\.md$", path)
        if not slug_match:
            return f"<strong>{anchor}</strong>"
        slug = slug_match.group(1)
        return f'<a href="content.html?slug={slug}">{anchor}</a>'

    html = re.sub(
        r'<a href="(\.\.[^"]*\.md)"[^>]*>(.*?)</a>',
        cross_content,
        html,
    )
    return html


# ─── Build stages ────────────────────────────────────────────────────────

def build_rulings(out_dir: Path) -> list:
    rulings = []
    for f in sorted(RULINGS_DIR.glob("*.json")):
        rulings.append(json.loads(f.read_text(encoding="utf-8")))
    rulings.sort(key=lambda r: r.get("ruling_date", ""), reverse=True)
    (out_dir / "rulings.json").write_text(
        json.dumps(rulings, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return rulings


def build_justices(out_dir: Path, rulings: list) -> list:
    justices: dict[str, dict] = {}
    counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {"panel_count": 0, "majority_authored": 0, "minority_authored": 0}
    )

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
    (out_dir / "justices.json").write_text(
        json.dumps(justices_list, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return justices_list


def build_content(out_dir: Path) -> dict:
    """
    Build the informative content layer: convert each content/*/foo.md to HTML
    and emit content.json with metadata + body_html per piece.
    """
    out = {cat: [] for cat in CONTENT_CATEGORIES}
    if not CONTENT_DIR.exists():
        print("  (no content/ directory found; skipping content build)")
        (out_dir / "content.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return out

    for category in CONTENT_CATEGORIES:
        cat_dir = CONTENT_DIR / category
        if not cat_dir.exists():
            continue
        for f in sorted(cat_dir.glob("*.md")):
            text = f.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(text)
            html = markdown_to_html(body)
            html = relativize_internal_links(html)
            out[category].append({
                "slug": f.stem,
                "category": category,
                "title": meta.get("title", f.stem),
                "contributor": meta.get("contributor", ""),
                "date": meta.get("date", ""),
                "summary": meta.get("summary", ""),
                "body_html": html,
            })

    (out_dir / "content.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return out


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rulings = build_rulings(OUT_DIR)
    print(f"✓ wrote {OUT_DIR/'rulings.json'} ({len(rulings)} rulings)")

    justices_list = build_justices(OUT_DIR, rulings)
    print(f"✓ wrote {OUT_DIR/'justices.json'} ({len(justices_list)} justices)")

    content_out = build_content(OUT_DIR)
    total_pieces = sum(len(v) for v in content_out.values())
    by_cat = ", ".join(f"{len(v)} {k}" for k, v in content_out.items())
    print(f"✓ wrote {OUT_DIR/'content.json'} ({total_pieces} pieces — {by_cat})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
