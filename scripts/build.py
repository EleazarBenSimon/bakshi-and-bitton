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
import html
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
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
# Extra content categories that are built (HTML, static pages, findable by
# content.html) but do NOT appear in the Reading list — they have their own
# top-level nav entry instead. "structure" = the Power-Structure long-form.
EXTRA_CONTENT_CATEGORIES = ["structure"]


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

# Illustrated comics keyed to the ruling they retell. Surfaced as a prominent
# link on that ruling's page (and vice-versa).
COMICS = {
    "5658-23": {
        "url": "comic-5658-23.html",
        "title_he": "מי נתן להם את הסמכות הזו? — סיפור מצויר",
        "title_en": "Who gave them this authority? — illustrated story",
    },
}


def _reverse_content_index() -> dict:
    """Scan content/*/*.md for links to data/rulings/<slug>.json and return
    {ruling_slug: [{slug,title_he,title_en,category}]} so each ruling can link
    back to the essays/explainers/patterns that discuss it."""
    index: dict[str, list] = defaultdict(list)
    if not CONTENT_DIR.exists():
        return index
    link_re = re.compile(r"data/rulings/([a-z0-9-]+)\.json")
    for category in CONTENT_CATEGORIES:
        cat_dir = CONTENT_DIR / category
        if not cat_dir.exists():
            continue
        for f in sorted(cat_dir.glob("*.md")):
            if f.stem.endswith(".he") or f.stem.endswith(".en"):
                continue
            text = f.read_text(encoding="utf-8")
            meta, _ = parse_frontmatter(text)
            title = meta.get("title", f.stem)
            piece = {
                "slug": f.stem, "category": category,
                "title_he": meta.get("title_he", title),
                "title_en": meta.get("title_en", title),
            }
            for slug in {m.group(1) for m in link_re.finditer(text)}:
                if all(p["slug"] != piece["slug"] for p in index[slug]):
                    index[slug].append(piece)
    return index


def build_rulings(out_dir: Path) -> list:
    rulings = []
    for f in sorted(RULINGS_DIR.glob("*.json")):
        rulings.append(json.loads(f.read_text(encoding="utf-8")))
    rulings.sort(key=lambda r: r.get("ruling_date", ""), reverse=True)
    # Enrich with cross-links (comic + related reading) for the site layer.
    rev = _reverse_content_index()
    for r in rulings:
        slug = r.get("case_id_slug")
        if slug in COMICS:
            r["comic"] = COMICS[slug]
        if rev.get(slug):
            r["related_content"] = rev[slug]
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
            # Placeholder seats for rulings whose full panel composition was not
            # verified. They are kept on the ruling's own panel (for honest
            # panel-size reporting) but must NOT aggregate into the justices
            # index — "unverified-3" is a different unknown person in each case.
            if slug.startswith("unverified"):
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
    all_categories = CONTENT_CATEGORIES + EXTRA_CONTENT_CATEGORIES
    out = {cat: [] for cat in all_categories}
    if not CONTENT_DIR.exists():
        print("  (no content/ directory found; skipping content build)")
        (out_dir / "content.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return out

    def _strip_dup_h1(body_text: str, *titles: str) -> str:
        """Strip the leading `# Title` line if it duplicates any of the
        candidate titles (canonical / he / en). Keeps the body uncluttered."""
        lines = body_text.lstrip().splitlines()
        if lines and lines[0].startswith("# "):
            first_h1 = lines[0][2:].strip()
            if any(first_h1 == (tt or "").strip() for tt in titles):
                return "\n".join(lines[1:]).lstrip()
        return body_text

    def _words_of(b: str) -> int:
        """Word count proxy from raw markdown — strip links/images."""
        stripped = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", b)
        stripped = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", stripped)
        stripped = re.sub(r"[`*_#>~|\-]+", " ", stripped)
        return len([w for w in stripped.split() if w and not w.startswith("http")])

    for category in all_categories:
        cat_dir = CONTENT_DIR / category
        if not cat_dir.exists():
            continue
        for f in sorted(cat_dir.glob("*.md")):
            # Skip language-overlay files; they're loaded by name from
            # their canonical sibling (foo.he.md, foo.en.md). Path.stem
            # of "foo.he.md" is "foo.he" — so endswith catches them.
            if f.stem.endswith(".he") or f.stem.endswith(".en"):
                continue
            text = f.read_text(encoding="utf-8")
            meta, canonical_body = parse_frontmatter(text)

            # Per-language body overlays: when `slug.he.md` or `slug.en.md`
            # exists alongside the canonical `slug.md`, its body replaces
            # the canonical body for that language only. Frontmatter on
            # the overlay file is ignored — all metadata lives on the
            # canonical. Falls back to the canonical body if no overlay.
            def _load_overlay(suffix: str) -> str:
                overlay = cat_dir / f"{f.stem}.{suffix}.md"
                if overlay.exists():
                    _m, overlay_body = parse_frontmatter(overlay.read_text(encoding="utf-8"))
                    return overlay_body
                return canonical_body

            body_he_raw = _load_overlay("he")
            body_en_raw = _load_overlay("en")

            title_meta = meta.get("title", "").strip()
            title_he   = meta.get("title_he", title_meta).strip()
            title_en   = meta.get("title_en", title_meta).strip()

            body_he_raw = _strip_dup_h1(body_he_raw, title_meta, title_he, title_en)
            body_en_raw = _strip_dup_h1(body_en_raw, title_meta, title_he, title_en)

            html_he = relativize_internal_links(markdown_to_html(body_he_raw))
            html_en = relativize_internal_links(markdown_to_html(body_en_raw))

            words_he = _words_of(body_he_raw)
            words_en = _words_of(body_en_raw)
            mins_he  = max(1, round(words_he / 200))
            mins_en  = max(1, round(words_en / 200))

            primary_title   = meta.get("title", f.stem)
            primary_summary = meta.get("summary", "")
            # Legacy fields (body_html, word_count, reading_minutes) keep
            # the English/canonical values for back-compat with any
            # older consumers; bilingual readers use the *_he / *_en pair.
            out[category].append({
                "slug": f.stem,
                "category": category,
                "title": primary_title,
                "title_he": meta.get("title_he", primary_title),
                "title_en": meta.get("title_en", primary_title),
                "contributor": meta.get("contributor", ""),
                "date": meta.get("date", ""),
                "summary": primary_summary,
                "summary_he": meta.get("summary_he", primary_summary),
                "summary_en": meta.get("summary_en", primary_summary),
                "word_count": words_en,
                "reading_minutes": mins_en,
                "word_count_he": words_he,
                "word_count_en": words_en,
                "reading_minutes_he": mins_he,
                "reading_minutes_en": mins_en,
                "body_html": html_en,
                "body_html_he": html_he,
                "body_html_en": html_en,
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
        outcome_he = OUTCOME_LABELS_HE.get(outcome, outcome.replace("_", " "))
        summary_he = (r.get("summary_he") or "")[:600]

        # Canonical link is the prerendered static ruling page (real per-ruling
        # OG/meta + crawlable). The old ?slug= form pointed at a param the SPA
        # never read, so every feed link 404'd in practice.
        link = f"{SITE_BASE_URL}/ruling-{slug}.html"

        title_combined = f"{case_id} — {title_he} ({outcome_he})"
        desc_html = (
            f"<p><strong>תוצאה:</strong> {xml_escape(outcome_he)}</p>"
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


# ─── Controlled-vocabulary labels ────────────────────────────────────────
# Human-readable Hebrew/English labels for the enum fields that were
# previously shown to users as raw code strings (struck_down, ultra_vires…).
# These maps are the single source of truth: build.py uses them for the
# prerendered static pages, and they are emitted to _data/labels.json so the
# SPA (app.js) renders the same labels at runtime.

OUTCOME_LABELS_HE = {
    "struck_down": "בוטל",
    "partially_struck": "בוטל חלקית",
    "mandatory_order": "צו עשה",
    "warning_of_voidness": "התראת בטלות",
    "remanded": "הוחזר לדיון",
    "dismissed": "נדחה",
    "declarative": "הצהרתי",
}
OUTCOME_LABELS_EN = {
    "struck_down": "Struck down",
    "partially_struck": "Partially struck",
    "mandatory_order": "Mandatory order",
    "warning_of_voidness": "Warning of voidness",
    "remanded": "Remanded",
    "dismissed": "Dismissed",
    "declarative": "Declarative",
}
DOCTRINE_LABELS_HE = {
    "reasonableness": "עילת הסבירות",
    "proportionality": "מידתיות",
    "ultra_vires": "חריגה מסמכות",
    "separation_of_powers": "הפרדת רשויות",
    "judicial_independence": "עצמאות שיפוטית",
    "procedural_review": "ביקורת הליכית",
    "conflict_of_interest": "ניגוד עניינים",
    "constitutional_supremacy": "עליונות חוקתית",
    "constituent_authority_limits": "גבולות הסמכות המכוננת",
    "abuse_of_constituent_power": "שימוש לרעה בסמכות מכוננת",
    "basic_law_judiciary": "חוק-יסוד: השפיטה",
    "basic_law_government": "חוק-יסוד: הממשלה",
    "basic_law_human_dignity_and_liberty": "חוק-יסוד: כבוד האדם וחירותו",
}
DOCTRINE_LABELS_EN = {
    "reasonableness": "Reasonableness",
    "proportionality": "Proportionality",
    "ultra_vires": "Ultra vires",
    "separation_of_powers": "Separation of powers",
    "judicial_independence": "Judicial independence",
    "procedural_review": "Procedural review",
    "conflict_of_interest": "Conflict of interest",
    "constitutional_supremacy": "Constitutional supremacy",
    "constituent_authority_limits": "Constituent-authority limits",
    "abuse_of_constituent_power": "Abuse of constituent power",
    "basic_law_judiciary": "Basic Law: The Judiciary",
    "basic_law_government": "Basic Law: The Government",
    "basic_law_human_dignity_and_liberty": "Basic Law: Human Dignity and Liberty",
}
PETITIONER_TYPE_HE = {
    "NGO": "ארגון חברה אזרחית",
    "individual": "יחיד/ה",
    "political": "גורם פוליטי",
    "local_authority": "רשות מקומית",
    "corporation": "תאגיד",
    "party": "סיעה",
}
COMPLIANCE_HE = {
    "complied": "קוים",
    "defied": "לא קוים",
    "partial": "קוים חלקית",
    "pending": "תלוי ועומד",
    "moot": "התייתר",
}
RESPONDENT_HE = {
    "Knesset": "הכנסת",
    "Government": "הממשלה",
    "Cabinet": "הממשלה",
    "Minister": "שר/ה",
    "Prime Minister": "ראש הממשלה",
    "Statute": "חקיקה",
    "Local-Authority": "רשות מקומית",
    "Senior-Appointments-Committee": "הוועדה לבדיקת מינויים בכירים",
}


def build_labels(out_dir: Path) -> None:
    """Emit _data/labels.json so app.js can render the same human labels."""
    labels = {
        "outcome": {"he": OUTCOME_LABELS_HE, "en": OUTCOME_LABELS_EN},
        "doctrine": {"he": DOCTRINE_LABELS_HE, "en": DOCTRINE_LABELS_EN},
        "petitioner_type": {"he": PETITIONER_TYPE_HE},
        "compliance_state": {"he": COMPLIANCE_HE},
        "respondent": {"he": RESPONDENT_HE},
    }
    (out_dir / "labels.json").write_text(
        json.dumps(labels, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ─── Prerendered static pages (SEO / social previews / no-JS) ─────────────
# The site is a client-rendered SPA: search crawlers and social-card scrapers
# that don't execute JS see an empty shell. These generators emit one static,
# fully-baked HTML page per ruling and per content piece — real <head> meta +
# Open Graph + JSON-LD + crawlable Hebrew body — so a shared link renders a
# rich card and the content is indexable. The interactive SPA stays the
# default for navigation; these are canonical landing pages.

OG_IMAGE = f"{SITE_BASE_URL}/assets/og-default.png"


def _esc(s) -> str:
    return html.escape(str(s if s is not None else ""), quote=True)


def _page_head(title_he: str, description: str, canonical_path: str,
               og_type: str = "website", jsonld: dict | None = None,
               og_image: str = OG_IMAGE) -> str:
    """Full <head> with localized title, description, OG, Twitter, canonical,
    favicon, and optional JSON-LD."""
    canonical = f"{SITE_BASE_URL}/{canonical_path}"
    desc = " ".join((description or "").split())[:300]
    parts = [
        '<!DOCTYPE html>',
        '<html lang="he" dir="rtl">',
        '<head>',
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f'<title>{_esc(title_he)} · בקשי וביטון</title>',
        f'<meta name="description" content="{_esc(desc)}">',
        f'<link rel="canonical" href="{_esc(canonical)}">',
        '<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">',
        '<link rel="stylesheet" href="assets/style.css">',
        '<link rel="alternate" type="application/rss+xml" title="Bakshi&Bitton — new rulings" href="feed.xml">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:site_name" content="Bakshi&Bitton · בקשי וביטון">',
        f'<meta property="og:title" content="{_esc(title_he)}">',
        f'<meta property="og:description" content="{_esc(desc)}">',
        f'<meta property="og:url" content="{_esc(canonical)}">',
        f'<meta property="og:image" content="{_esc(og_image)}">',
        '<meta property="og:locale" content="he_IL">',
        '<meta property="og:locale:alternate" content="en_US">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{_esc(title_he)}">',
        f'<meta name="twitter:description" content="{_esc(desc)}">',
        f'<meta name="twitter:image" content="{_esc(og_image)}">',
    ]
    if jsonld:
        parts.append(
            '<script type="application/ld+json">'
            + json.dumps(jsonld, ensure_ascii=False) + '</script>'
        )
    parts.append('</head>')
    return "\n".join(parts)


def _static_header(active: str) -> str:
    """Static Hebrew header matching app.js renderHeader markup. The EN toggle
    routes to the interactive SPA (which holds the bilingual rendering)."""
    def nav(href, label, key):
        style = ' style="font-weight:600;color:var(--accent)"' if key == active else ''
        return f'<a href="{href}"{style}>{label}</a>'
    return (
        '<header><div class="header-inner">'
        '<div><a class="logo" href="index.html">בקשי וביטון'
        '<span class="logo-sub">פסיקות בית המשפט העליון בעניין החלטות ממשלה ומינויים</span>'
        '</a></div>'
        '<nav>'
        + nav("index.html", "פסיקות", "rulings")
        + nav("reading.html", "קריאה", "reading")
        + nav("justices.html", "שופטים", "justices")
        + nav("content.html?slug=power-structure", "מבנה הכוח", "structure")
        + nav("cite.html", "ציטוט והפצה", "cite")
        + nav("about.html", "אודות", "about")
        + '</nav>'
        '<button class="lang-toggle" onclick="localStorage.setItem(\'bakshi-and-bitton-lang\',\'en\');'
        'location.href=this.dataset.spa">EN</button>'
        '</div></header>'
    )


_STATIC_FOOTER = (
    '<footer>Bakshi&Bitton · '
    '<a href="https://github.com/EleazarBenSimon/bakshi-and-bitton">github.com/EleazarBenSimon/bakshi-and-bitton</a>'
    ' · MIT License · '
    '<a href="https://github.com/EleazarBenSimon/bakshi-and-bitton/blob/main/METHODOLOGY.md">מתודולוגיה</a>'
    '</footer>'
)


def _share_bar(canonical: str, share_title: str) -> str:
    """Static, tracker-free share bar for the canonical landing pages: intent
    URLs only (no third-party widgets or scripts); copy + print use tiny inline
    handlers. Hebrew labels match the prerendered (he) pages and reuse the
    .share-bar / .share-btn styling already in style.css."""
    u = quote(canonical, safe="")
    ttl = quote(share_title, safe="")
    ttl_u = quote(share_title + " — " + canonical, safe="")
    copy_js = (
        "var b=this;navigator.clipboard&&navigator.clipboard.writeText(b.dataset.url);"
        "b.classList.add('copied');b.textContent='הועתק ✓';"
        "setTimeout(function(){b.classList.remove('copied');"
        "b.textContent='העתק קישור';},2000);return false;"
    )
    return (
        '<div class="share-bar" aria-label="שיתוף">'
        '<span class="share-label">שיתוף:</span>'
        '<a class="share-btn" target="_blank" rel="noopener" '
        f'href="https://x.com/intent/post?text={ttl}&amp;url={u}">X</a>'
        '<a class="share-btn" target="_blank" rel="noopener" '
        f'href="https://bsky.app/intent/compose?text={ttl_u}">Bluesky</a>'
        '<a class="share-btn" target="_blank" rel="noopener" '
        f'href="https://wa.me/?text={ttl_u}">WhatsApp</a>'
        f'<a class="share-btn" href="mailto:?subject={ttl}&amp;body={ttl_u}">מייל</a>'
        f'<button type="button" class="share-btn" data-url="{_esc(canonical)}" '
        f'onclick="{copy_js}">העתק קישור</button>'
        '<button type="button" class="share-btn" '
        'onclick="window.print();return false;">הדפסה / PDF</button>'
        '</div>'
    )


def render_ruling_page(r: dict) -> str:
    slug = r.get("case_id_slug", "")
    case_id = r.get("case_id", "")
    name_he = r.get("case_name_he", "")
    summary_he = r.get("summary_he", "")
    spa_url = f"ruling.html?id={slug}"

    # JSON-LD: model each ruling as an Article about a legal decision, with the
    # official ruling as isBasedOn (provenance).
    jsonld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": f"{case_id} — {name_he}",
        "inLanguage": "he",
        "datePublished": r.get("ruling_date", ""),
        "url": f"{SITE_BASE_URL}/ruling-{slug}.html",
        "image": OG_IMAGE,
        "isPartOf": {"@type": "Dataset", "name": "Bakshi&Bitton",
                     "url": f"{SITE_BASE_URL}/"},
        "author": {"@type": "Person", "name": "Eleazar Ben Simon"},
        "publisher": {"@type": "Organization", "name": "Bakshi&Bitton"},
        "abstract": summary_he,
    }
    if r.get("official_url"):
        jsonld["isBasedOn"] = r["official_url"]

    head = _page_head(
        title_he=f"{case_id} — {name_he}" if name_he else case_id,
        description=summary_he, canonical_path=f"ruling-{slug}.html",
        og_type="article", jsonld=jsonld,
    )

    # Detail grid (humanized Hebrew labels)
    rows = []
    def row(label, value):
        if value in (None, "", []):
            return
        rows.append(f"<dt>{_esc(label)}</dt><dd>{value}</dd>")
    row("תאריך הפסיקה", _esc(r.get("ruling_date")))
    if r.get("filing_date"):
        row("תאריך הגשה", _esc(r["filing_date"]))
    row("סוג עותר", _esc(PETITIONER_TYPE_HE.get(r.get("petitioner_type"), r.get("petitioner_type"))))
    row("עותר", _esc(r.get("petitioner_name_he")))
    resp = RESPONDENT_HE.get(r.get("respondent"), r.get("respondent"))
    row("משיב", _esc(resp))
    if r.get("respondent_body_he") or r.get("respondent_body"):
        row("גוף נושא ההחלטה", _esc(r.get("respondent_body_he") or r.get("respondent_body")))
    if r.get("respondent_decision_he"):
        row("ההחלטה המעורערת", _esc(r["respondent_decision_he"]))
    doctrines = ", ".join(DOCTRINE_LABELS_HE.get(d, d) for d in (r.get("doctrine_invoked") or []))
    row("עילות שנטענו", _esc(doctrines))
    outcome = r.get("outcome", "")
    row("תוצאה", f'<span class="outcome-pill outcome-{_esc(outcome)}">'
                 f'{_esc(OUTCOME_LABELS_HE.get(outcome, outcome))}</span>')
    if r.get("vote_majority") is not None:
        row("הצבעה", f'{_esc(r.get("vote_majority"))}–{_esc(r.get("vote_minority") or 0)}')
    if r.get("predicate_ag_opinion_he") or r.get("predicate_ag_opinion"):
        row("חוות-דעת היועמ\"ש שקדמה", _esc(r.get("predicate_ag_opinion_he") or r.get("predicate_ag_opinion")))
    if r.get("compliance_state"):
        row("מצב יישום", _esc(COMPLIANCE_HE.get(r["compliance_state"], r["compliance_state"])))
    if r.get("defiance_signals_he") or r.get("defiance_signals"):
        row("סימני התנגדות", _esc(r.get("defiance_signals_he") or r.get("defiance_signals")))
    if r.get("tags"):
        row("תיוגים", _esc(", ".join(r["tags"])))
    grid = '<dl class="ruling-detail-grid">' + "".join(rows) + '</dl>'

    # Panel
    panel_items = []
    maj = set(r.get("majority_authors") or [])
    minset = set(r.get("minority_authors") or [])
    for j in r.get("panel", []):
        sl = j.get("slug")
        klass = "author-majority" if sl in maj else ("author-minority" if sl in minset else "")
        nm = _esc(j.get("name_he"))
        linkable = sl and not sl.startswith("unverified")
        link = f'<a href="justice.html?slug={_esc(sl)}">{nm}</a>' if linkable else nm
        panel_items.append(f'<li class="{klass}">{link}</li>')
    panel = ('<h2>הרכב</h2><ul class="panel-list">' + "".join(panel_items) + '</ul>')

    secondary = ""
    if r.get("secondary_urls"):
        lis = "".join(f'<li><a href="{_esc(u)}" target="_blank" rel="noopener">{_esc(u)}</a></li>'
                      for u in r["secondary_urls"])
        secondary = f'<h2>מקורות משניים</h2><ul>{lis}</ul>'

    notes = ""
    notes_txt = r.get("notes_he") or r.get("notes")
    if notes_txt:
        notes = f'<h2>הערות</h2><div class="notes-box">{_esc(notes_txt)}</div>'


    print_cite = ""
    if r.get("print_citation"):
        print_cite = (f'<p class="print-citation">מקור רשמי (בדפוס בלבד): '
                      f'<strong>{_esc(r["print_citation"])}</strong></p>')
    official = ""
    if r.get("official_url"):
        # Only court.gov.il is the authoritative ruling; anything else (Versa,
        # encyclopedia) is a secondary description and must not be mislabeled.
        is_court = "court.gov.il" in r["official_url"]
        label = "→ פסק הדין הרשמי" if is_court else "→ מקור מקוון (משני — אינו נוסח פסק הדין)"
        official = (f'<p><a class="source-link" href="{_esc(r["official_url"])}" '
                    f'target="_blank" rel="noopener">{label}</a></p>')

    comic = ""
    if r.get("comic"):
        comic = (f'<p class="ruling-comic-link"><a href="{_esc(r["comic"]["url"])}">'
                 f'🖼 {_esc(r["comic"]["title_he"])} →</a></p>')

    related = ""
    if r.get("related_content"):
        cats = {"essays": "מאמר", "explainers": "הסבר", "patterns": "תיעוד דפוס"}
        items = "".join(
            f'<li><a href="reading-{_esc(p["slug"])}.html">{_esc(p["title_he"])}</a>'
            f' <span style="color:var(--text-muted);font-size:12px">· {_esc(cats.get(p["category"], p["category"]))}</span></li>'
            for p in r["related_content"])
        related = f'<h2>קריאה נוספת</h2><ul class="related-reading">{items}</ul>'

    body = (
        f'<div id="root">{_static_header("rulings")}<main>'
        f'<p><a href="index.html">← פסיקות</a></p>'
        f'<h1>{_esc(case_id)}</h1>'
        f'<p style="color:var(--text-muted);font-size:15px;margin-top:-8px">{_esc(name_he)}</p>'
        f'<p style="font-size:16px;line-height:1.6">{_esc(summary_he)}</p>'
        f'{comic}{print_cite}{official}{grid}{panel}{secondary}{notes}{related}'
        f'<p style="margin-top:24px;font-size:14px"><a href="{_esc(spa_url)}">'
        f'גרסה אינטראקטיבית מלאה / English →</a></p>'
        f'{_share_bar(f"{SITE_BASE_URL}/ruling-{slug}.html", (case_id + " — " + name_he) if name_he else case_id)}'
        f'</main>{_STATIC_FOOTER}</div>'
    )
    # data-spa on the toggle so it routes to this ruling's SPA view
    body = body.replace('class="lang-toggle"', f'class="lang-toggle" data-spa="{_esc(spa_url)}"')
    return head + '\n<body>\n' + body + '\n</body>\n</html>\n'


def render_content_static_page(piece: dict, category: str) -> str:
    slug = piece.get("slug", "")
    title_he = piece.get("title_he") or piece.get("title") or slug
    summary_he = piece.get("summary_he") or piece.get("summary") or ""
    body_html = piece.get("body_html_he") or piece.get("body_html") or ""
    spa_url = f"content.html?slug={slug}"
    badge = {"essays": "מאמר", "explainers": "הסבר", "patterns": "תיעוד דפוס"}.get(category, category)

    jsonld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title_he,
        "inLanguage": "he",
        "datePublished": piece.get("date", ""),
        "url": f"{SITE_BASE_URL}/reading-{slug}.html",
        "image": OG_IMAGE,
        "author": {"@type": "Person", "name": "Eleazar Ben Simon"},
        "publisher": {"@type": "Organization", "name": "Bakshi&Bitton"},
        "abstract": summary_he,
    }
    head = _page_head(title_he=title_he, description=summary_he,
                      canonical_path=f"reading-{slug}.html",
                      og_type="article", jsonld=jsonld)
    qa = (f'<aside class="quick-answer"><div class="quick-answer-label">תשובה מהירה</div>'
          f'<p class="quick-answer-body" dir="auto">{_esc(summary_he)}</p></aside>') if summary_he else ""
    body = (
        f'<div id="root">{_static_header("reading")}<main>'
        f'<p class="breadcrumb"><a href="reading.html">קריאה</a> / {_esc(badge)}</p>'
        f'<article class="content-article" dir="auto">'
        f'<header class="article-header">'
        f'<span class="article-badge article-badge--{_esc(category)}">{_esc(badge)}</span>'
        f'<h1 class="article-title" dir="auto">{_esc(title_he)}</h1>{qa}</header>'
        f'<div class="article-body">{body_html}</div>'
        f'<p style="margin-top:24px;font-size:14px"><a href="{_esc(spa_url)}">'
        f'גרסה אינטראקטיבית מלאה / English →</a></p>'
        f'{_share_bar(f"{SITE_BASE_URL}/reading-{slug}.html", title_he)}'
        f'</article></main>{_STATIC_FOOTER}</div>'
    )
    body = body.replace('class="lang-toggle"', f'class="lang-toggle" data-spa="{_esc(spa_url)}"')
    return head + '\n<body>\n' + body + '\n</body>\n</html>\n'


def build_static_pages(site_dir: Path, rulings: list, content: dict) -> int:
    n = 0
    for r in rulings:
        slug = r.get("case_id_slug")
        if not slug:
            continue
        (site_dir / f"ruling-{slug}.html").write_text(render_ruling_page(r), encoding="utf-8")
        n += 1
    for category, pieces in content.items():
        for piece in pieces:
            slug = piece.get("slug")
            if not slug:
                continue
            (site_dir / f"reading-{slug}.html").write_text(
                render_content_static_page(piece, category), encoding="utf-8")
            n += 1
    return n


def build_sitemap(site_dir: Path, rulings: list, content: dict, justices: list) -> Path:
    urls = ["", "index.html", "reading.html", "justices.html", "cite.html",
            "about.html", "comic-5658-23.html"]
    for r in rulings:
        if r.get("case_id_slug"):
            urls.append(f"ruling-{r['case_id_slug']}.html")
    for pieces in content.values():
        for p in pieces:
            if p.get("slug"):
                urls.append(f"reading-{p['slug']}.html")
    for j in justices:
        if j.get("slug"):
            urls.append(f"justice.html?slug={j['slug']}")
    body = "\n".join(
        f"  <url><loc>{SITE_BASE_URL}/{xml_escape(u)}</loc></url>" for u in urls
    )
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + body + "\n</urlset>\n")
    out = site_dir / "sitemap.xml"
    out.write_text(xml, encoding="utf-8")
    return out


def build_robots(site_dir: Path) -> Path:
    out = site_dir / "robots.txt"
    out.write_text(
        "User-agent: *\nAllow: /\n\n"
        f"Sitemap: {SITE_BASE_URL}/sitemap.xml\n", encoding="utf-8")
    return out


# Google Search Console ownership token (HTML-tag verification). Injected into
# every page's <head> on each build so verification survives rebuilds — Google
# re-checks the tag periodically and silently un-verifies if it disappears.
GOOGLE_SITE_VERIFICATION = "xjBO4qp4oVELM3i_R8MDu1IgT9S9u0hNMyDfKPHIWd4"


def version_assets(site_dir: Path) -> dict:
    """Cache-busting: stamp a content-hash query onto the CSS/JS links in every
    HTML page, so a changed asset is fetched fresh instead of served from a
    stale browser/CDN cache. Runs over shells + generated pages alike; the hash
    only changes when the asset's bytes change, so it's stable otherwise.

    Also injects the Google Search Console verification meta tag into each
    page's <head> (idempotent) so site ownership stays verified across builds."""
    import hashlib
    versions = {}
    for asset in ("assets/style.css", "assets/app.js"):
        p = site_dir / asset
        if p.exists():
            versions[asset] = hashlib.sha1(p.read_bytes()).hexdigest()[:8]
    verify_tag = (
        f'<meta name="google-site-verification" '
        f'content="{GOOGLE_SITE_VERIFICATION}">')
    n = 0
    for html_file in site_dir.glob("*.html"):
        text = html_file.read_text(encoding="utf-8")
        new = text
        for asset, ver in versions.items():
            # match the asset with or without an existing ?v=… and re-stamp it
            new = re.sub(
                rf'{re.escape(asset)}(\?v=[0-9a-f]+)?',
                f'{asset}?v={ver}', new)
        # inject verification tag once, right after the opening <head>
        if "google-site-verification" not in new and "<head>" in new:
            new = new.replace("<head>", "<head>\n" + verify_tag, 1)
        if new != text:
            html_file.write_text(new, encoding="utf-8")
            n += 1
    return {"versions": versions, "pages_stamped": n}


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

    build_labels(OUT_DIR)
    print(f"✓ wrote {OUT_DIR/'labels.json'} (enum → human labels)")

    n_static = build_static_pages(SITE_DIR, rulings, content_out)
    print(f"✓ wrote {n_static} prerendered static pages (ruling-*.html, reading-*.html)")

    sitemap_path = build_sitemap(SITE_DIR, rulings, content_out, justices_list)
    print(f"✓ wrote {sitemap_path}")

    robots_path = build_robots(SITE_DIR)
    print(f"✓ wrote {robots_path}")

    vinfo = version_assets(SITE_DIR)
    print(f"✓ cache-busted assets {vinfo['versions']} on {vinfo['pages_stamped']} pages")

    return 0


if __name__ == "__main__":
    sys.exit(main())
