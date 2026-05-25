#!/usr/bin/env python3
"""
Build site data files from data/rulings/*.json and content/*.md.

Generates:
  - site/_data/rulings.json    — array of all rulings (for homepage + filtering)
  - site/_data/justices.json   — derived array of justice records (panel appearances)
  - site/_data/content.json    — informative content layer (explainers / patterns / essays)
                                  with markdown converted to HTML for rendering
  - site/_data/rulings.csv     — flat CSV export for researchers / spreadsheet users
  - site/feed.xml              — RSS 2.0 feed (one item per ruling, newest first)

Run from repo root after adding or modifying a ruling or a content piece:
    python3 scripts/build.py

Dependencies:
    - markdown (for content/*.md → HTML conversion). Install: pip3 install --user markdown
"""

import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

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
SITE_DIR = REPO_ROOT / "site"
OUT_DIR = SITE_DIR / "_data"

# Public-facing canonical URL (used for RSS GUID + cite formats)
SITE_BASE_URL = "https://eleazarbensimon.github.io/bakshi-and-bitton"

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


def build_csv(out_dir: Path, rulings: list) -> Path:
    """
    Generate a flat CSV export of the documentary core.
    Designed for researchers / journalists who want to load into Excel,
    Google Sheets, R, pandas, etc.
    """
    out = out_dir / "rulings.csv"
    fieldnames = [
        "case_id", "case_id_slug", "case_name_he", "case_name_en",
        "ruling_date", "filing_date",
        "panel_size", "petitioner_type", "petitioner_name_en", "petitioner_name_he",
        "respondent",
        "doctrine_invoked", "outcome",
        "vote_majority", "vote_minority",
        "majority_authors", "minority_authors",
        "official_url",
        "summary_en", "summary_he",
        "compliance_state",
    ]
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        w.writeheader()
        for r in rulings:
            w.writerow({
                "case_id": r.get("case_id", ""),
                "case_id_slug": r.get("case_id_slug", ""),
                "case_name_he": r.get("case_name_he", ""),
                "case_name_en": r.get("case_name_en", ""),
                "ruling_date": r.get("ruling_date", ""),
                "filing_date": r.get("filing_date") or "",
                "panel_size": len(r.get("panel", [])),
                "petitioner_type": r.get("petitioner_type", ""),
                "petitioner_name_en": r.get("petitioner_name_en", ""),
                "petitioner_name_he": r.get("petitioner_name_he", ""),
                "respondent": r.get("respondent", ""),
                "doctrine_invoked": "; ".join(r.get("doctrine_invoked", []) or []),
                "outcome": r.get("outcome", ""),
                "vote_majority": r.get("vote_majority", "") or "",
                "vote_minority": r.get("vote_minority", "") or "",
                "majority_authors": "; ".join(r.get("majority_authors", []) or []),
                "minority_authors": "; ".join(r.get("minority_authors", []) or []),
                "official_url": r.get("official_url", ""),
                "summary_en": r.get("summary_en", "").replace("\n", " "),
                "summary_he": r.get("summary_he", "").replace("\n", " "),
                "compliance_state": r.get("compliance_state") or "",
            })
    return out


def build_rss(site_dir: Path, rulings: list) -> Path:
    """
    Generate RSS 2.0 feed at site/feed.xml.
    One <item> per ruling, sorted newest-first.
    Subscribers get a feed entry for every new documentary-core addition.
    """
    out = site_dir / "feed.xml"

    def rfc822(date_str: str) -> str:
        # ruling_date is YYYY-MM-DD; assume midnight UTC for RSS pubDate
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
        except Exception:
            return ""

    now_rfc822 = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

    items_xml = []
    for r in rulings:
        title_he = r.get("case_name_he", r.get("case_id", "?"))
        case_id = r.get("case_id", "?")
        slug = r.get("case_id_slug", "")
        outcome = r.get("outcome", "")
        summary_he = (r.get("summary_he") or "")[:600]

        link = f"{SITE_BASE_URL}/ruling.html?slug={slug}"

        title_combined = f"{case_id} — {title_he} ({outcome})"
        desc_html = (
            f"<p><strong>תוצאה:</strong> {xml_escape(outcome)}</p>"
            f"<p>{xml_escape(summary_he)}</p>"
            f'<p><a href="{xml_escape(r.get("official_url",""))}">פסק הדין הרשמי</a></p>'
        )

        items_xml.append(
            "    <item>\n"
            f"      <title>{xml_escape(title_combined)}</title>\n"
            f"      <link>{xml_escape(link)}</link>\n"
            f"      <guid isPermaLink=\"true\">{xml_escape(link)}</guid>\n"
            f"      <pubDate>{rfc822(r.get('ruling_date',''))}</pubDate>\n"
            f"      <description><![CDATA[{desc_html}]]></description>\n"
            "    </item>"
        )

    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        '  <channel>\n'
        f'    <title>Bakshi&amp;Bitton · בקשי וביטון</title>\n'
        f'    <link>{SITE_BASE_URL}/</link>\n'
        f'    <atom:link href="{SITE_BASE_URL}/feed.xml" rel="self" type="application/rss+xml"/>\n'
        '    <description>פסיקות בית המשפט העליון בעניין החלטות ממשלה ומינויים — תיעוד מובנה, מקושר למקור הרשמי.</description>\n'
        '    <language>he</language>\n'
        f'    <lastBuildDate>{now_rfc822}</lastBuildDate>\n'
        f'    <pubDate>{now_rfc822}</pubDate>\n'
        + "\n".join(items_xml) + "\n"
        '  </channel>\n'
        '</rss>\n'
    )
    out.write_text(rss, encoding="utf-8")
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

    csv_path = build_csv(OUT_DIR, rulings)
    print(f"✓ wrote {csv_path}")

    rss_path = build_rss(SITE_DIR, rulings)
    print(f"✓ wrote {rss_path} ({len(rulings)} feed items)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
