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
import math
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlparse
from xml.sax.saxutils import escape as xml_escape

try:
    import markdown as md
except ImportError:
    print("ERROR: python 'markdown' package not installed.", file=sys.stderr)
    print("Install with: pip3 install --user markdown", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
RULINGS_DIR = REPO_ROOT / "data" / "rulings"
LIBRARY_FILE = REPO_ROOT / "data" / "library" / "quiet-veto-cases.json"
STATEMENTS_FILE = REPO_ROOT / "data" / "library" / "statements.json"
POWER_MECHANISMS_FILE = REPO_ROOT / "data" / "library" / "power-mechanisms.json"
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
            "footnotes",       # [^1] footnote syntax in the long essays
            "fenced_code",     # for any ``` blocks
            "attr_list",       # so we can target classes if needed later
            "sane_lists",      # better list handling
            "smarty",          # smart quotes / dashes
        ],
        output_format="html5",
    )


def is_official_host(url: str) -> bool:
    """True iff `url` sits on an Israeli government host (….gov.il) — the only
    place an official ruling text is published. Anything else (a newspaper, a
    university archive) is a secondary source and is labeled as one, rather
    than being passed off as "the official ruling"."""
    try:
        host = (urlparse(url or "").hostname or "").lower()
    except ValueError:
        return False
    return host.endswith(".gov.il")


def _official_label_he(url: str) -> str:
    """Hebrew link text for a ruling's `official_url` — honest about what sits
    at the other end. Two rulings in the corpus have no official text online at
    all, and their link points at a newspaper / a university archive."""
    return ("פסק הדין הרשמי" if is_official_host(url)
            else "מקור (אין טקסט רשמי זמין באינטרנט)")


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
    # The house-style 12-panel arc — the paradox of authority's source — retells BOTH bookend rulings —
    # Bank Mizrahi (the power claimed) and HCJ 5658/23 (the power used to void a
    # Basic Law) — so both link to it. Replaces the old 5-panel comic-5658-23.
    "6821-93-bank-mizrahi": {
        "url": "comic-6821-93.html",
        "title_he": "פרדוקס מקור הסמכות — סיפור מצויר",
        "title_en": "The Paradox of Authority's Source — illustrated story",
    },
    "5658-23": {
        "url": "comic-6821-93.html",
        "title_he": "פרדוקס מקור הסמכות — סיפור מצויר",
        "title_en": "The Paradox of Authority's Source — illustrated story",
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


_QV_OUTCOME_LABEL = {
    "he": {
        "read_down": "רוקן בפרשנות",
        "struck_down": "בוטל",
        "partially_struck": "בוטל חלקית",
        "warning_of_voidness": "התראת בטלות",
        "dismissed": "נדחה (אך עם הלכה)",
    },
    "en": {
        "read_down": "Read down / gutted",
        "struck_down": "Struck down",
        "partially_struck": "Partially struck",
        "warning_of_voidness": "Warning of voidness",
        "dismissed": "Dismissed (w/ doctrine)",
    },
}
_QV_HEADERS = {
    "he": ("מספר תיק", "שנה", "חוק / רשות שנפגעו", "הכרעה", "סוג התוצאה"),
    "en": ("Case / Citation", "Year", "Law / Authority Affected", "Holding", "Outcome Type"),
}

# The "Holding" column is the project's own condensed paraphrase of each
# ruling's substance (see blurb_he/blurb_en in quiet-veto-cases.json) — NOT
# a quotation of the court's own language and NOT an official translation.
# Per METHODOLOGY.md §10, the project's defamation-law defense rests on facts
# being sourced to the ruling itself, not the project's characterization; a
# terse table cell reads as more authoritative than the same text embedded in
# the cited, moderator-reviewed prose below, so this caption travels with the
# table (generated, not hand-added, so it can't be dropped or go stale).
_QV_CAPTION = {
    "he": (
        "**על מקורות והכרעה:** בכל שורה נגישה, טור 'הכרעה' הוא ניסוח תמציתי משל "
        "הפרויקט של מהות הפסיקה — לא ציטוט מלשון פסק הדין ולא תרגום רשמי — "
        "מעוגן במסמך הרשמי המקושר (↗) ליד מספר התיק. שורה מאופרת (⬚ המסמך "
        "הרשמי חסר) מציינת שטרם אותר עבורה מקור רשמי נגיש בשפה זו; לחצו 'תרם "
        "מסמך' אם בידיכם אחד."
    ),
    "en": (
        "**On sources & holdings:** in each accessible row, the \"Holding\" is "
        "the project's own condensed summary of the ruling's substance — not a "
        "quotation of the court's language and not an official translation — "
        "anchored to the official document linked (↗) beside the case number. A "
        "greyed-out row (⬚ Official document missing) means no accessible "
        "official source has been located for it in this language yet; click "
        "“Contribute the document” if you have one."
    ),
}

# Sentence-boundary detector for _qv_first_sentence: a '.'/'!'/'?' followed by
# whitespace (or end of string) ends a sentence UNLESS it's immediately after
# one of these abbreviations/citation markers (e.g. "sec.", "No.", "etc."),
# in which case it's not a real sentence break and we keep scanning.
_QV_ABBREV_TAIL = re.compile(
    r"\b(?:No|Nos|Sec|Secs|Art|Arts|Rep|Ltd|Inc|Co|St|vs|etc|e\.g|i\.e|"
    r"Mr|Mrs|Dr|Prof|Ord|Amdt|PD|par|para|pt|vol|ed|al)\.$",
    re.IGNORECASE,
)


def _qv_first_sentence(text: str) -> str:
    """Mechanically extract the first real sentence of a free-text field
    (blurb_he/blurb_en), for a one-line, scannable table cell. Purely
    derived — never paraphrases or rewrites the source text. Skips false
    sentence-boundaries caused by abbreviations/citation markers ('sec.',
    'No.', 'etc.') so those don't truncate the holding mid-thought; falls
    back to the full field if no clean boundary is found. Verified safe on
    Hebrew text too (no equivalent abbreviation landmines found in blurb_he
    across all 48 cases)."""
    text = (text or "").strip()
    if not text:
        return ""
    for m in re.finditer(r"[.!?](\s+|$)", text):
        candidate = text[: m.start() + 1]
        if _QV_ABBREV_TAIL.search(candidate):
            continue
        return candidate.strip()
    return text


def _qv_outcome_type(case: dict) -> str:
    """Classify a quiet-veto-cases.json entry into one of 5 outcome buckets,
    derived ONLY from its `action` string + `interpretive_evisceration` flag
    (never from the hand-written prose). Verified to reproduce the exact
    25/12/8/2/1 split already stated in the prose intro and its per-case
    italic tags, so the table stays consistent with the narrative without
    scraping it."""
    a = (case.get("action") or "").lower()
    if case.get("interpretive_evisceration") is True:
        return "read_down"
    if "dismiss" in a:
        return "dismissed"
    if "warning_of_voidness" in a or "warning of voidness" in a:
        return "warning_of_voidness"
    if "partially_struck" in a:
        return "partially_struck"
    return "struck_down"


def _quiet_veto_table_md(lang: str) -> str:
    """Generate the quiet-veto quick-reference table as a raw HTML block,
    straight from data/library/quiet-veto-cases.json at build time.

    Source-gated (per language): each case's `official_sources[lang]` decides
    whether the Holding is shown. If an official/authoritative source IS on
    file, the row is normal and the Holding is anchored to that document
    (linked '↗' beside the docket). If NOT, the row renders 'off-status'
    (greyed identifying details, so a reader still knows WHICH document is
    wanted) with the Holding cell replaced by a '⬚ missing' marker + a
    'Contribute the document' button (wired to a client-side modal in app.js).
    Emitted as raw HTML (not markdown) so rows can carry classes/buttons;
    python-markdown passes a top-level <table> block through untouched, and
    the caption after the blank line is processed as normal markdown.

    KNOWN FOLLOW-UP: the 'Law / Authority Affected' column reads `statute`,
    which has no per-language variant yet (pre-existing gap; needs a
    `statute_he` for all 48 cases — content work, not a code change)."""
    import html as _html
    if not LIBRARY_FILE.exists():
        return ""
    raw = json.loads(LIBRARY_FILE.read_text(encoding="utf-8"))
    cases = raw if isinstance(raw, list) else raw.get("cases", [])

    def e(s):
        return _html.escape(str(s or "").replace("\n", " ").strip())

    blurb_field = "blurb_he" if lang == "he" else "blurb_en"
    statute_field = "statute_he" if lang == "he" else "statute_en"
    h = _QV_HEADERS[lang]
    missing_label = "המסמך הרשמי חסר" if lang == "he" else "Official document missing"
    contribute_label = "תרם מסמך" if lang == "he" else "Contribute the document"
    src_title = "מקור רשמי" if lang == "he" else "official source"

    parts = ['<table class="qv-table"><thead><tr>']
    parts += [f"<th>{e(col)}</th>" for col in h]
    parts.append("</tr></thead><tbody>")
    for c in cases:
        ot = _qv_outcome_type(c)
        src = (c.get("official_sources") or {}).get(lang)
        has = bool(src and src.get("url"))
        # Language-normalised docket (same helper the prose sections use) so the
        # HE table shows בג"ץ… and the EN table shows HCJ…, not the raw
        # bilingual `docket` field.
        docket = e(_qv_docket(c, lang))
        if has:
            docket_cell = (f'{docket} <a class="qv-src" href="{e(src["url"])}" '
                           f'target="_blank" rel="noopener" title="{src_title}">↗</a>')
            holding_cell = e(_qv_first_sentence(c.get(blurb_field)))
        else:
            docket_cell = docket
            holding_cell = (
                f'<span class="qv-missing-label">⬚ {e(missing_label)}</span> '
                f'<button type="button" class="qv-contribute" '
                f'data-docket="{e(c.get("docket_core") or c.get("docket"))}" '
                f'data-name="{e(c.get("name"))}" data-lang="{lang}">{e(contribute_label)}</button>'
            )
        # Each row is a jump target for the content-map: a stable id + a
        # data-toc-label (the case's language-normalised docket + clean name)
        # that both TOC builders (build.py _content_toc and the SPA
        # content.html script) turn into a sidebar bullet pointing here.
        row_id = "qv-row-" + re.sub(r"[^0-9A-Za-z]+", "-", (c.get("docket_core") or "")).strip("-")
        nm = _qv_clean_name(c, lang)
        core_dk = _qv_docket(c, lang)
        row_label = f"{core_dk} — {nm}" if nm else core_dk
        row_attrs = f' id="{row_id}" data-toc-label="{e(row_label)}"'
        if not has:
            row_attrs += ' class="qv-row-off"'
        parts.append(
            f"<tr{row_attrs}>"
            f'<td class="qv-c-docket">{docket_cell}</td>'
            f"<td>{e(c.get('year'))}</td>"
            f'<td class="qv-c-statute">{e(c.get(statute_field) or c.get("statute"))}</td>'
            f'<td class="qv-c-holding">{holding_cell}</td>'
            f"<td>{e(_QV_OUTCOME_LABEL[lang][ot])}</td>"
            f"</tr>"
        )
    parts.append("</tbody></table>")
    # Wrap in .table-scroll (overflow-x:auto) so this wide 5-column table
    # scrolls inside its own box on narrow screens instead of pinning the
    # whole article wider than the viewport (which, with body overflow-x:
    # hidden, clipped the page and broke mobile reflow).
    return '<div class="table-scroll">' + "".join(parts) + "</div>\n\n" + _QV_CAPTION[lang] + "\n"


# Standard bilingual Israeli docket-prefix pairs (the established Versa/Cardozo
# abbreviations — NOT invented): lets each case number be rendered in the page's
# own language regardless of how the source `docket` string happened to be
# authored (some are Hebrew-led, some English-led, some carry both in parens).
_QV_DOCKET_PREFIX_PAIRS = [
    ('בג"ץ', "HCJ"),      # High Court of Justice
    ('דנג"ץ', "HCJFH"),   # Further Hearing (HCJ)
    ('ע"א', "CA"),        # Civil Appeal
    ('ע"פ', "CrimA"),     # Criminal Appeal
    ('דנ"פ', "CrimFH"),   # Criminal Further Hearing
    ('עע"ם', "AAA"),      # Administrative Affairs Appeal
]


def _qv_norm_prefix(tok: str) -> str:
    """Normalise a docket-prefix token for matching: drop gershayim/quote
    variants, apostrophes, and parentheses so 'ע"א', 'ע״א', '(ע"א)' all match."""
    for ch in "\"'()׳״“”‘’":
        tok = tok.replace(ch, "")
    return tok.strip()


_QV_PREFIX_LOOKUP = {}
for _he_pfx, _en_pfx in _QV_DOCKET_PREFIX_PAIRS:
    _QV_PREFIX_LOOKUP[_qv_norm_prefix(_he_pfx)] = (_he_pfx, _en_pfx)
    _QV_PREFIX_LOOKUP[_qv_norm_prefix(_en_pfx)] = (_he_pfx, _en_pfx)


def _qv_docket(case: dict, lang: str) -> str:
    """Render a case's docket in the target language as `{prefix} {core}`.
    The number (`docket_core`) is language-neutral; the prefix is resolved from
    the authored `docket` via the standard bilingual abbreviation map. Never
    fabricates a citation form — if the prefix can't be confidently mapped it
    falls back to the authored docket with any parenthetical stripped."""
    core = (case.get("docket_core") or "").strip()
    raw = (case.get("docket") or "").strip()
    authored = raw.split(core)[0].strip() if core and core in raw else raw
    for tok in re.split(r"\s+", authored):
        pair = _QV_PREFIX_LOOKUP.get(_qv_norm_prefix(tok))
        if pair and core:
            return f"{(pair[0] if lang == 'he' else pair[1])} {core}"
    return re.sub(r"\s*\(.*?\)\s*", " ", raw).strip()


# Docket-citation tokens + leading-junk pattern used by _qv_clean_name to peel
# citation cruft off the (often bilingual, consolidated) `name` field.
_QV_DOCKET_TOK = (
    r'(?:HCJ|HCJ-?FH|CA|CrimA|CrimFH|HCJFH|AAA|EA|LCA|Dnagatz|FH|'
    r'בג"?ץ|דנ"?פ|דנג"?ץ|ע"?א|ע"?פ|עע"?ם|רע"?א)'
)
_QV_LEAD_JUNK = re.compile(r'^\s*(?:[&,]|on\b|and\b|' + _QV_DOCKET_TOK + r'|\(?[-\d/]+\)?)\s*', re.I)
_QV_TRAIL_DOCKET = re.compile(r'\s*' + _QV_DOCKET_TOK + r'\s*[-\d/]+\s*$', re.I)


def _qv_strip_parens(s: str) -> str:
    """Drop parenthetical groups (balanced first, then any dangling open/close)
    so a truncated '(Nation-State Basic Law' can't survive into a heading."""
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"\s*\([^()]*\)\s*", " ", s)
    s = re.sub(r"\s*\([^)]*$", " ", s)
    if s.count(")") and not s.count("("):
        s = re.sub(r"^[^(]*\)\s*", " ", s)
    return s


def _qv_clean_name(case: dict, lang: str) -> str:
    """Extract a clean, well-formed case name in the target language from the
    messy `name` field (which is frequently bilingual, carries the docket, and
    concatenates consolidated petitions) — or '' when none can be had cleanly,
    in which case the section falls back to a docket-only heading.

    Strategy: strip parentheticals, pick a segment written purely in the target
    script (never a bare docket), then peel leading/trailing citation junk. A
    STRICT gate rejects anything carrying the other script, too short, or not a
    multi-word name — so a heading can never leak the wrong language or show a
    half-mangled fragment."""
    name = _qv_strip_parens((case.get("name") or "").strip())
    if not name:
        return ""
    other = r"[A-Za-z]" if lang == "he" else r"[֐-׿]"
    tgt = r"[֐-׿]" if lang == "he" else r"[A-Za-z]"
    cand = None
    for s in re.split(r"\s+[—/|]\s+|\s+/\s+|\s+—\s+", name):
        s = s.strip()
        if s and re.search(tgt, s) and not re.search(other, s):
            if len(_QV_LEAD_JUNK.sub("", s).strip()) >= 5:
                cand = s
                break
    if cand is None:
        cand = name if (re.search(tgt, name) and not re.search(other, name)) else ""
    prev = None
    while prev != cand:
        prev = cand
        cand = _QV_LEAD_JUNK.sub("", cand).strip()
        cand = _QV_TRAIL_DOCKET.sub("", cand).strip()
    cand = re.sub(r"\s{2,}", " ", cand).strip(" —-/|·,.'\"")
    if (not cand or re.search(other, cand) or len(cand) < 5
            or " " not in cand or not re.search(tgt, cand)):
        return ""
    return cand


# ─── Statement tracker ("Where the Right Draws the Line") ──────────────────
# Same source-gated, per-language, no-cross-language-fallback machinery as the
# quiet-veto table (that is where the HE/EN leak bug lived). Every display
# field is selected by language up front and passed through a strict script
# gate; a statement with no source in a language renders greyed, never blanked
# and never filled from the other language. The `confidence`/`attribution`
# fields are surfaced as a visible tag so a second-hand private remark can
# never be mistaken for an on-record public statement.
_STMT_HEADERS = {
    "he": ("דובר/ת", "תפקיד / שיוך", "תאריך", "האמירה", "ייחוס"),
    "en": ("Speaker", "Role / Affiliation", "Date", "Statement", "Attribution"),
}
_STMT_CONF = {
    "he": {"VERIFIED": "מאומת", "REPORTED": "מדווח"},
    "en": {"VERIFIED": "Verified", "REPORTED": "Reported"},
}
_STMT_ATTR = {
    "he": {
        "direct-public": "פומבי · על־רקורד",
        "reported-private-single-source": "דיווח פרטי · מקור יחיד",
    },
    "en": {
        "direct-public": "On-record · public",
        "reported-private-single-source": "Reported private · single-source",
    },
}
_STMT_CAPTION = {
    "he": (
        "**על ייחוס ומקורות:** כל שורה מציגה ציטוט מילולי (בגופן הרשומה) לצד "
        "מקורו. תג *מאומת* מציין אמירה פומבית על־רקורד ממקור ראשוני או ממספר "
        "מקורות; תג *מדווח* (המודגש) מציין דיווח ממקור יחיד או אמירה פרטית — "
        "ואין לראות בו אמירה פומבית רשמית. שורה מאופרת (⬚) פירושה שטרם אותר "
        "מקור נגיש לאמירה בשפה זו; התוכן לעולם אינו מוחלף בטקסט בשפה האחרת."
    ),
    "en": (
        "**On attribution & sources:** each row shows a verbatim quote (in the "
        "record typeface) beside its source. A *Verified* tag means an on-record "
        "public statement from a primary source or several; a *Reported* tag "
        "(emphasised) means a single-source report or a private remark — it "
        "should not be read as an on-record public statement. A greyed row (⬚) "
        "means no accessible source has been located for that statement in this "
        "language; the text is never swapped for the other language."
    ),
}


def _stmt_script_ok(s: str, lang: str) -> bool:
    """Strict script gate (same defense as _qv_clean_name): reject a string
    only when it is a FULL wrong-language leak — the other script present and
    the target script absent. A value that is empty, punctuation/number only,
    or merely cites a foreign proper noun (a quote may name 'X' or 'HCJ')
    still passes."""
    s = s or ""
    heb = bool(re.search(r"[֐-׿]", s))
    lat = bool(re.search(r"[A-Za-z]", s))
    return (not (lat and not heb)) if lang == "he" else (not (heb and not lat))


def _statement_table_md(lang: str) -> str:
    """Generate the statement-tracker table as a raw HTML block from
    data/library/statements.json, per language. Quote-only, source-gated,
    with the attribution/confidence surfaced visibly on every row."""
    import html as _html
    if not STATEMENTS_FILE.exists():
        return ""
    raw = json.loads(STATEMENTS_FILE.read_text(encoding="utf-8"))
    stmts = raw if isinstance(raw, list) else raw.get("statements", [])

    def e(s):
        return _html.escape(str(s or "").replace("\n", " ").strip())

    def pick(st, base):
        # per-language field, gated: never return the other language's text
        v = st.get(f"{base}_{lang}") or ""
        return v if _stmt_script_ok(v, lang) else ""

    h = _STMT_HEADERS[lang]
    missing_label = "אין מקור רשום" if lang == "he" else "No source on file"
    src_title = "מקור" if lang == "he" else "source"
    ctx_lead = "הקשר" if lang == "he" else "Context"
    q_open, q_close = "“", "”"

    parts = ['<table class="stmt-table"><thead><tr>']
    parts += [f"<th>{e(col)}</th>" for col in h]
    parts.append("</tr></thead><tbody>")
    for st in stmts:
        conf = st.get("confidence") or ""
        attr = st.get("attribution") or ""
        reported = (conf == "REPORTED") or (attr != "direct-public")
        # A statement's source is LANGUAGE-AGNOSTIC: the outlet that reported the
        # quote is its source whether the page renders HE or EN. So the link
        # comes from the sources[] array (shown identically on both languages) —
        # NOT official_sources[lang], which is a rulings concept (separate HE/EN
        # official texts) that does not apply to statements. official_sources is
        # intentionally ignored for this table. "Is it sourced?" (sources[]) and
        # "on-record vs. reported-private?" (confidence/attribution) are kept
        # separate: a Reported single-source remark is still sourced.
        srcs = st.get("sources") or []
        src0 = srcs[0] if srcs else None
        has_src = bool(src0 and src0.get("url"))

        speaker = e(pick(st, "speaker"))
        role = e(pick(st, "role"))
        affil = e(pick(st, "affiliation"))
        quote = e(pick(st, "quote"))
        context = e(pick(st, "context"))
        date = e(st.get("date"))

        role_bits = [b for b in (role, affil) if b and b != "—"]
        role_cell = " · ".join(role_bits) if role_bits else "—"

        # The verbatim quote wears the record serif (.rec) and links to its
        # source (the reporting outlet, named). It degrades to a ⬚ marker ONLY
        # if the quote is unavailable in this language or the statement carries
        # no source at all — never because a source lacks a same-language URL.
        if quote and has_src:
            src_pub = e(src0.get("publisher") or src_title)
            q = (f'<span class="stmt-quote rec">{q_open}{quote}{q_close}</span> '
                 f'<a class="qv-src" href="{e(src0["url"])}" target="_blank" '
                 f'rel="noopener" title="{src_pub}">↗ {src_pub}</a>')
            if context:
                q += (f'<p class="stmt-context"><span class="stmt-context-lead">'
                      f'{e(ctx_lead)}:</span> {context}</p>')
        else:
            q = f'<span class="qv-missing-label">⬚ {e(missing_label)}</span>'

        conf_lbl = _STMT_CONF[lang].get(conf, conf)
        attr_lbl = _STMT_ATTR[lang].get(attr, attr)
        tag_cls = "stmt-tag stmt-tag-reported" if reported else "stmt-tag stmt-tag-verified"
        tag_cell = (f'<span class="{tag_cls}">{e(conf_lbl)}</span>'
                    f'<span class="stmt-attr">{e(attr_lbl)}</span>')

        # Reported/private → amber caution styling (kept as-is). The greyed
        # 'off' state is now ONLY the degenerate no-source-at-all case, decoupled
        # from confidence — so a Reported-but-sourced row is NOT greyed.
        row_cls = " stmt-row-reported" if reported else ""
        if not has_src:
            row_cls += " stmt-row-off"
        parts.append(
            f'<tr class="stmt-row{row_cls}">'
            f'<td class="stmt-c-speaker">{speaker or "—"}</td>'
            f'<td class="stmt-c-role">{role_cell}</td>'
            f'<td class="stmt-c-date">{date}</td>'
            f'<td class="stmt-c-quote">{q}</td>'
            f'<td class="stmt-c-tag">{tag_cell}</td>'
            f"</tr>"
        )
    parts.append("</tbody></table>")
    return '<div class="table-scroll">' + "".join(parts) + "</div>\n\n" + _STMT_CAPTION[lang] + "\n"


# ─── Power-Structure tabs (data/library/power-mechanisms.json) ────────────
#
# The Power-Structure long-form (content/structure/power-structure.md + .en.md)
# carries only a lede, a <!-- TABS:power-mechanisms --> marker, and the method
# note. The interactive tabbed apparatus — overview + 7 mechanism panels, each
# with a bespoke inline SVG diagram, a computed exits-meter, and a fairness
# aside — is generated HERE, per language, straight from the JSON, so the
# published record can never hand-drift from the audited data. Every display
# string is read ONLY from its `field_{lang}` variant (never cross-language);
# a missing optional field omits its block. All KPI numbers are COMPUTED by
# counting the exits cells at build time, never stored.
#
# The whole apparatus is emitted as a SINGLE top-level raw-HTML line (no
# internal newlines) so python-markdown passes it through untouched — the same
# discipline as _quiet_veto_table_md's emission. SVGs are string-assembled,
# parametric, CSS-var-coloured, role="img" + <title>, with shape-redundant
# status encoding (colour is never the sole carrier). defs ids are prefixed
# pm{num}- (per-mechanism) / pmx- (exit-map); the small portal glyphs carry no
# ids at all (they repeat ~56× on the page).

_PM_CHANNEL_ORDER = ["appeal", "statute", "basic_law", "ballot"]


def _pm_load() -> dict:
    """Load the power-mechanisms data source (or {} if absent)."""
    if not POWER_MECHANISMS_FILE.exists():
        return {}
    return json.loads(POWER_MECHANISMS_FILE.read_text(encoding="utf-8"))


def _pm_prose(md_text: str, lang: str) -> str:
    """Render a markdown fragment to HTML via the shared converter, then
    collapse all newlines so it can live inside the single-line raw-HTML
    block. Internal anchor links (#m-N) and cross-refs survive."""
    if not md_text:
        return ""
    out = relativize_internal_links(markdown_to_html(md_text))
    return re.sub(r"\s*\n\s*", " ", out).strip()


def _pm_t(x, y, s, lang, size=15, anchor="middle", fill="var(--text)", weight=None):
    """One SVG <text> node — RTL direction added for Hebrew, content escaped."""
    attrs = [f'x="{x}"', f'y="{y}"', f'text-anchor="{anchor}"',
             f'font-size="{size}"', f'fill="{fill}"']
    if lang == "he":
        attrs.append('direction="rtl"')
    if weight:
        attrs.append(f'font-weight="{weight}"')
    return f'<text {" ".join(attrs)}>{_esc(s)}</text>'


def _pm_arrow(x1, y1, x2, y2, color="var(--accent)", dashed=False, w=2):
    """A directed line with an inline (id-free) triangular arrowhead at (x2,y2),
    oriented along the segment — safe to repeat many times on one page."""
    ang = math.atan2(y2 - y1, x2 - x1)
    L = 9
    a1, a2 = ang + math.radians(150), ang - math.radians(150)
    p1 = (x2 + L * math.cos(a1), y2 + L * math.sin(a1))
    p2 = (x2 + L * math.cos(a2), y2 + L * math.sin(a2))
    dash = ' stroke-dasharray="6 4"' if dashed else ''
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{w}" stroke-linecap="round"{dash}/>'
            f'<polygon points="{x2:.1f},{y2:.1f} {p1[0]:.1f},{p1[1]:.1f} '
            f'{p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>')


def _pm_xbar(cx, cy, r=14, color="var(--outcome-struck)"):
    """Blocked marker: a horizontal bar PLUS an × — shape-redundant, so the
    'closed' meaning does not rest on colour alone."""
    return (f'<line x1="{cx - r}" y1="{cy}" x2="{cx + r}" y2="{cy}" stroke="{color}" stroke-width="3"/>'
            f'<line x1="{cx - r}" y1="{cy - r}" x2="{cx + r}" y2="{cy + r}" stroke="{color}" stroke-width="3"/>'
            f'<line x1="{cx + r}" y1="{cy - r}" x2="{cx - r}" y2="{cy + r}" stroke="{color}" stroke-width="3"/>')


def _pm_loop(cx, cy, r=12, color="var(--outcome-remanded)"):
    """Contingent/return marker: a loop-arc that curls back on itself — the
    topology (a closed return) carries the meaning, not the colour."""
    return (f'<path d="M {cx - r} {cy} A {r} {r} 0 1 1 {cx + r} {cy}" fill="none" '
            f'stroke="{color}" stroke-width="2.5"/>'
            + _pm_arrow(cx + r, cy, cx + r - 0.5, cy + 7, color, w=2))


def _pm_box(x, y, w, h, label, lang, ghost=False, fill="var(--surface)",
            stroke="var(--accent)", rx=6, size=15, weight="600"):
    """A labelled node box; `ghost` = dashed + muted (the counterfactual tiers)."""
    st = "var(--text-muted)" if ghost else stroke
    dash = ' stroke-dasharray="5 4"' if ghost else ''
    tfill = "var(--text-muted)" if ghost else "var(--text)"
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{st}" stroke-width="2"{dash}/>'
            + _pm_t(x + w / 2, y + h / 2 + size / 3, label, lang, size=size,
                    fill=tfill, weight=weight))


def _pm_svg(h, title, lang, body):
    """Wrap an assembled SVG body: viewBox 0 0 680 H, role=img + localized title."""
    return (f'<svg class="ps-svg" viewBox="0 0 680 {h}" role="img" '
            f'xmlns="http://www.w3.org/2000/svg"><title>{_esc(title)}</title>{body}</svg>')


def _pm_portal_svg(status, id_prefix=""):
    """Status → portal glyph (used in the overview matrix and per-panel meter).
    open = outlined portal + outward arrow; open_untested = dashed outline;
    contingent = portal + loop-arc into a mini court box (amber); closed =
    filled portal + ×-bar (struck-red). Colour is never the sole carrier."""
    arch = "M6 48 L6 24 A16 16 0 0 1 38 24 L38 48 Z"
    acc, red, amb = "var(--accent)", "var(--outcome-struck)", "var(--outcome-remanded)"
    if status == "open":
        body = (f'<path d="{arch}" fill="none" stroke="{acc}" stroke-width="2.5"/>'
                + _pm_arrow(22, 42, 22, 4, acc, w=2.5))
    elif status == "open_untested":
        body = (f'<path d="{arch}" fill="none" stroke="{acc}" stroke-width="2.5" '
                f'stroke-dasharray="4 3"/>'
                f'<circle cx="22" cy="34" r="2.4" fill="{acc}"/>')
    elif status == "contingent":
        court = (f'<rect x="14" y="0" width="16" height="12" fill="none" stroke="{amb}" '
                 f'stroke-width="2"/><polygon points="11,0 33,0 22,-8" fill="{amb}"/>')
        body = (f'<path d="{arch}" fill="none" stroke="{acc}" stroke-width="2.5"/>'
                f'<path d="M22 26 A11 11 0 1 1 31 17" fill="none" stroke="{amb}" '
                f'stroke-width="2.5"/>' + court)
    else:  # closed
        body = (f'<path d="{arch}" fill="{red}" fill-opacity="0.16" stroke="{red}" '
                f'stroke-width="2.5"/>' + _pm_xbar(22, 32, 12, red))
    return (f'<svg class="ps-portal ps-portal--{status}" viewBox="-2 -11 48 65" '
            f'aria-hidden="true" xmlns="http://www.w3.org/2000/svg">{body}</svg>')


# ---- the seven bespoke mechanism topologies ------------------------------

def _pm_diagram_svg(mech, lang):
    """Dispatch to the mechanism-specific topology builder, keyed by id."""
    builder = {
        "first-and-last": _pm_diag_first_last,
        "direct-access": _pm_diag_direct,
        "ag-chain": _pm_diag_ag,
        "panel-composition": _pm_diag_panel,
        "no-standing": _pm_diag_standing,
        "judges-select-judges": _pm_diag_selfselect,
        "everything-justiciable": _pm_diag_justiciable,
    }.get(mech.get("id"))
    if not builder:
        return ""
    lb = (mech.get("diagram") or {}).get("labels", {}).get(lang, {})
    nodes = _PM_NODES.get(lang, {})
    title = mech.get(f"oneliner_{lang}", "")
    return builder(lb, nodes, lang, mech.get("num"), title)


_PM_NODES = {}  # populated at call time from data; set by _power_tabs_md


def _pm_diag_first_last(lb, nodes, lang, num, title):
    """Ghost 3-tier stack (~35% width, left) vs. one tall Court box (right);
    a petition enters the Court, an appeal stub rises out of it and is ×-barred."""
    acc = "var(--accent)"
    b = []
    # left: the usual three tiers, ghosted, with upward arrows between them
    tiers = [nodes.get("first_instance", ""), nodes.get("appeal_court", ""), nodes.get("supreme", "")]
    ys = [250, 165, 80]
    for label, y in zip(tiers, ys):
        b.append(_pm_box(55, y, 175, 52, label, lang, ghost=True, size=13))
    b.append(_pm_arrow(142, 250, 142, 219, "var(--text-muted)", dashed=True))
    b.append(_pm_arrow(142, 165, 142, 134, "var(--text-muted)", dashed=True))
    b.append(_pm_t(142, 42, lb.get("ghost_caption", ""), lang, size=12, fill="var(--text-muted)"))
    # right: the single, tall apex box
    b.append(_pm_box(420, 80, 195, 222, nodes.get("court", ""), lang,
                     fill="var(--accent-soft)", size=18))
    b.append(_pm_t(517, 320, lb.get("actual_caption", ""), lang, size=12, fill="var(--text-muted)"))
    # petition enters from the bottom
    b.append(_pm_arrow(517, 340, 517, 304, acc))
    b.append(_pm_t(517, 356, lb.get("entry_label", ""), lang, size=12, fill=acc))
    # appeal stub rises out of the top and is blocked
    b.append(_pm_arrow(517, 80, 517, 52, acc))
    b.append(_pm_xbar(517, 40, 13))
    b.append(_pm_t(430, 30, lb.get("blocked_label", ""), lang, size=13,
                   anchor="end" if lang == "en" else "start", fill="var(--outcome-struck)", weight="600"))
    return _pm_svg(370, title, lang, "".join(b))


def _pm_diag_direct(lb, nodes, lang, num, title):
    """Horizontal: petitioner → one big arc vaulting two ghost tiers → apex.
    Mirrored across x for Hebrew so the flow reads with the language."""
    acc = "var(--accent)"
    W = 680
    fx = (lambda v: W - v) if lang == "he" else (lambda v: v)
    # petitioner (left in LTR), court (right in LTR); ghosts skipped in the middle
    b = []
    b.append(_pm_box(fx(135) - 55, 150, 110, 52, nodes.get("petitioner", ""), lang, size=14))
    b.append(_pm_box(fx(310) - 60, 150, 120, 52, nodes.get("first_instance", ""), lang, ghost=True, size=12))
    b.append(_pm_box(fx(455) - 60, 150, 120, 52, nodes.get("appeal_court", ""), lang, ghost=True, size=12))
    b.append(_pm_box(fx(610) - 50, 150, 100, 52, nodes.get("court", ""), lang, fill="var(--accent-soft)", size=15))
    b.append(_pm_t(fx(382), 232, lb.get("ghost_caption", ""), lang, size=12, fill="var(--text-muted)"))
    # the vaulting arc from petitioner over the ghosts to the apex
    x0, x1 = fx(135), fx(610)
    b.append(f'<path d="M {x0} 148 C {x0} 34, {x1} 34, {x1} 148" fill="none" '
             f'stroke="{acc}" stroke-width="2.5"/>')
    # arrowhead landing on the apex box
    b.append(_pm_arrow((x1 + fx(560)) / 2, 60, x1, 146, acc))
    b.append(_pm_t(fx(372), 40, lb.get("actual_caption", ""), lang, size=13, fill=acc, weight="600"))
    b.append(_pm_t(fx(372), 120, lb.get("time_label", ""), lang, size=12, fill="var(--outcome-remanded)", weight="600"))
    return _pm_svg(260, title, lang, "".join(b))


def _pm_diag_ag(lb, nodes, lang, num, title):
    """Vertical: government → valve-gate (AG) → court. A dashed authority arrow
    runs FROM the court down to the gate (the gate's power derives from the
    Court's own doctrine); a thin dashed bypass skirts the gate (private counsel)."""
    acc = "var(--accent)"
    amb = "var(--outcome-remanded)"
    b = []
    b.append(_pm_box(270, 285, 140, 52, nodes.get("government", ""), lang, size=15))
    b.append(_pm_box(270, 70, 140, 52, nodes.get("court", ""), lang, fill="var(--accent-soft)", size=15))
    # the valve gate: an hourglass/bowtie the government's position must pass
    b.append(f'<polygon points="306,160 374,160 340,192" fill="var(--surface)" '
             f'stroke="{acc}" stroke-width="2"/>')
    b.append(f'<polygon points="306,224 374,224 340,192" fill="var(--surface)" '
             f'stroke="{acc}" stroke-width="2"/>')
    b.append(_pm_t(340, 148, nodes.get("ag", ""), lang, size=14, fill=acc, weight="600"))
    b.append(_pm_t(340, 246, lb.get("gate_label", ""), lang, size=12, fill="var(--text-muted)"))
    # solid upward flow through the gate
    b.append(_pm_arrow(340, 285, 340, 226, acc))
    b.append(_pm_arrow(340, 158, 340, 124, acc))
    # dashed authority arrow FROM the court down to the gate
    b.append(_pm_arrow(412, 100, 384, 178, amb, dashed=True))
    b.append(_pm_t(548, 150, lb.get("authority_label", ""), lang, size=11, fill=amb, anchor="end"))
    # thin dashed bypass skirting the gate on the left
    b.append(f'<path d="M 268 300 C 150 280, 150 120, 268 100" fill="none" '
             f'stroke="var(--text-muted)" stroke-width="1.5" stroke-dasharray="4 4"/>')
    b.append(_pm_t(140, 200, lb.get("bypass_label", ""), lang, size=11, fill="var(--text-muted)", anchor="start"))
    # ministry advisors feeding into the gate from the side
    b.append(_pm_box(470, 250, 175, 40, lb.get("ministry_label", ""), lang, ghost=True, size=11, weight="400"))
    b.append(_pm_arrow(470, 256, 378, 210, "var(--text-muted)", dashed=True))
    return _pm_svg(360, title, lang, "".join(b))


def _pm_diag_panel(lb, nodes, lang, num, title):
    """President node fanning to 3 / 9 / 15 dot-arcs; then a 15-segment vote bar,
    8 accent + 7 muted, labelled from the vote_label (8–7)."""
    acc = "var(--accent)"
    muted = "var(--text-muted)"
    cx, cy = 340, 78
    b = [_pm_box(cx - 80, 44, 160, 40, nodes.get("president", ""), lang, fill="var(--accent-soft)", size=14)]
    fans = [(3, 78, lb.get("fan_3", "3")), (9, 128, lb.get("fan_9", "9")), (15, 182, lb.get("fan_15", "15"))]
    for count, r, flabel in fans:
        # spread the dots along a downward fan (200°..340°)
        a0, a1 = math.radians(202), math.radians(338)
        for i in range(count):
            t = a0 + (a1 - a0) * (i / (count - 1))
            dx, dy = cx + r * math.cos(t), cy + 12 + r * math.sin(t)
            b.append(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="4.5" fill="{acc}"/>')
        b.append(_pm_t(cx - r - 14, cy + 16, flabel, lang, size=13, fill=muted, weight="600"))
    # the 15-segment vote bar — panel size that settled the outcome
    bx, bw, by, bh = 120, 440, 344, 30
    seg = bw / 15
    for i in range(15):
        fill = acc if i < 8 else muted
        b.append(f'<rect x="{bx + i * seg:.1f}" y="{by}" width="{seg - 2:.1f}" height="{bh}" '
                 f'rx="2" fill="{fill}"/>')
    b.append(_pm_t(cx, by - 8, lb.get("vote_label", ""), lang, size=16, fill=acc, weight="700"))
    b.append(_pm_t(cx, by + bh + 24, lb.get("default_note", ""), lang, size=11, fill=muted))
    return _pm_svg(410, title, lang, "".join(b))


def _pm_diag_standing(lb, nodes, lang, num, title):
    """Funnel: a cloud of petitioner dots → two filter walls swung OPEN (the
    standing gate) → court. A dashed arrow runs from the court back to the
    hinges (the Court itself opened the gate)."""
    acc = "var(--accent)"
    amb = "var(--outcome-remanded)"
    b = []
    # petitioner dots on the left
    pts = [(50, 90), (95, 70), (75, 120), (110, 150), (55, 165), (100, 200),
           (72, 225), (120, 105), (45, 130), (92, 245)]
    for (px, py) in pts:
        b.append(f'<circle cx="{px}" cy="{py}" r="6" fill="{acc}"/>')
    b.append(_pm_t(85, 275, lb.get("petitioners_label", ""), lang, size=13, fill="var(--text-muted)"))
    # two filter walls, hinged and swung open (doors rotated outward)
    b.append(f'<line x1="330" y1="150" x2="250" y2="70" stroke="{acc}" stroke-width="4" stroke-linecap="round"/>')
    b.append(f'<line x1="330" y1="150" x2="250" y2="230" stroke="{acc}" stroke-width="4" stroke-linecap="round"/>')
    b.append(f'<circle cx="330" cy="150" r="5" fill="none" stroke="{acc}" stroke-width="2"/>')
    b.append(_pm_t(300, 300, lb.get("gate_label", ""), lang, size=12, fill="var(--text-muted)"))
    b.append(_pm_t(300, 48, lb.get("open_label", ""), lang, size=12, fill=amb, weight="600"))
    # court on the right
    b.append(_pm_box(555, 120, 100, 60, nodes.get("court", ""), lang, fill="var(--accent-soft)", size=15))
    # straight admission arrow through the opened gap
    b.append(_pm_arrow(140, 150, 553, 150, acc))
    # dashed arrow: the court reaches back to the hinge that opened the gate
    b.append(f'<path d="M 605 120 C 560 60, 400 60, 336 146" fill="none" '
             f'stroke="{amb}" stroke-width="1.8" stroke-dasharray="5 4"/>')
    b.append(_pm_arrow(360, 120, 335, 146, amb))
    return _pm_svg(320, title, lang, "".join(b))


def _pm_diag_selfselect(lb, nodes, lang, num, title):
    """Nine committee seats (3 filled justices / 2 mid bar / 4 outlined elected);
    an appoint-7 bracket under all nine, a block-3 bracket over the three
    justices; a loop-arc court ↔ the three justice seats; three dashed vacant
    seats (the deadlock outcome)."""
    acc = "var(--accent)"
    amb = "var(--outcome-remanded)"
    b = [_pm_box(280, 40, 120, 40, nodes.get("court", ""), lang, fill="var(--accent-soft)", size=14)]
    sx, sy, sw, gap = 70, 165, 42, 20
    seats = []
    for i in range(9):
        x = sx + i * (sw + gap)
        seats.append(x)
        if i < 3:
            fill, st = acc, acc          # justices
        elif i < 5:
            fill, st = "var(--accent-soft)", acc   # bar
        else:
            fill, st = "var(--surface)", "var(--text-muted)"  # elected
        b.append(f'<rect x="{x}" y="{sy}" width="{sw}" height="{sw + 4}" rx="5" '
                 f'fill="{fill}" stroke="{st}" stroke-width="2"/>')
    # group labels
    b.append(_pm_t(seats[1] + sw / 2, sy + sw + 26, lb.get("seats_justices", ""), lang, size=11, fill=acc, weight="600"))
    b.append(_pm_t((seats[3] + seats[4]) / 2 + sw / 2, sy + sw + 26, lb.get("seats_bar", ""), lang, size=11, fill="var(--text-muted)"))
    b.append(_pm_t((seats[5] + seats[8]) / 2 + sw / 2, sy + sw + 26, lb.get("seats_elected", ""), lang, size=11, fill="var(--text-muted)"))
    # block-3 bracket over the three justice seats
    bl, br = seats[0], seats[2] + sw
    b.append(f'<path d="M {bl} 150 L {bl} 142 L {br} 142 L {br} 150" fill="none" '
             f'stroke="{amb}" stroke-width="2"/>')
    b.append(_pm_t((bl + br) / 2, 134, lb.get("block_label", ""), lang, size=12, fill=amb, weight="600"))
    # appoint-7 bracket under seven seats
    al, ar = seats[0], seats[6] + sw
    ay = sy + sw + 40
    b.append(f'<path d="M {al} {ay} L {al} {ay + 8} L {ar} {ay + 8} L {ar} {ay}" fill="none" '
             f'stroke="{acc}" stroke-width="2"/>')
    b.append(_pm_t((al + ar) / 2, ay + 24, lb.get("appoint_label", ""), lang, size=12, fill=acc, weight="600"))
    # loop-arc: court ↔ the three justice seats (self-selection)
    b.append(f'<path d="M 340 80 C 250 110, 150 120, {seats[0] + sw / 2:.0f} 160" fill="none" '
             f'stroke="{acc}" stroke-width="2" stroke-dasharray="1 0"/>')
    b.append(_pm_arrow(300, 96, 340, 82, acc))
    # three dashed vacant seats (the deadlock)
    vx = 500
    for i in range(3):
        x = vx + i * (sw + gap)
        b.append(f'<rect x="{x}" y="70" width="{sw}" height="{sw + 4}" rx="5" fill="none" '
                 f'stroke="var(--outcome-struck)" stroke-width="2" stroke-dasharray="5 4"/>')
    b.append(_pm_t(vx + (3 * sw + 2 * gap) / 2, 130, lb.get("vacant_label", ""), lang, size=11, fill="var(--outcome-struck)", weight="600"))
    return _pm_svg(300, title, lang, "".join(b))


def _pm_diag_justiciable(lb, nodes, lang, num, title):
    """Court box at centre; a dashed self-drawn boundary circle enclosing the
    domain chips; an incoming redraw segment from the Knesset is ×-barred at
    the boundary; the votes are noted."""
    acc = "var(--accent)"
    cx, cy, R = 340, 185, 150
    b = [f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{acc}" '
         f'stroke-width="2" stroke-dasharray="7 5"/>']
    b.append(_pm_t(cx, cy - R - 12, lb.get("boundary_label", ""), lang, size=12, fill=acc, weight="600"))
    b.append(_pm_box(cx - 55, cy - 25, 110, 50, nodes.get("court", ""), lang, fill="var(--accent-soft)", size=15))
    # domain chips arranged around the court, inside the circle
    domains = [d.strip() for d in (lb.get("domains", "") or "").split("·") if d.strip()]
    n = len(domains)
    for i, dom in enumerate(domains):
        t = math.radians(-90 + (360 / max(n, 1)) * i)
        dx, dy = cx + 95 * math.cos(t), cy + 95 * math.sin(t)
        w = 8 * len(dom) + 16
        b.append(f'<rect x="{dx - w / 2:.1f}" y="{dy - 13:.1f}" width="{w:.1f}" height="24" rx="12" '
                 f'fill="var(--surface)" stroke="var(--text-muted)" stroke-width="1.5"/>')
        b.append(_pm_t(dx, dy + 4, dom, lang, size=11, fill="var(--text)"))
    # incoming redraw segment from the Knesset, ×-barred at the boundary
    b.append(_pm_box(cx - 70, 385, 140, 44, nodes.get("knesset", ""), lang, size=14))
    b.append(_pm_arrow(cx, 385, cx, cy + R + 18, acc))
    b.append(_pm_xbar(cx, cy + R, 14))
    b.append(_pm_t(cx + 110, cy + R + 6, lb.get("redraw_label", ""), lang, size=12, fill="var(--outcome-struck)", weight="600"))
    b.append(_pm_t(624, 24, lb.get("votes", ""), lang, size=12, fill="var(--text-muted)", anchor="end"))
    return _pm_svg(440, title, lang, "".join(b))


def _pm_exitmap_svg(mechs, nodes, lang, title):
    """The full exit map. Right side: the accountability ladder — hatched public
    base, Knesset, Government (AG side-node), the Court on top — with solid
    upward authority arrows. Left side: seven RETURN PATHS fanning down from
    the Court, one per mechanism (numbered chip riding each path, linked to its
    tab). Each path terminates per that mechanism's audited dominant state:
    an exercised-open channel reaches the public band (only mechanism 2 —
    the honest exception); ≥2 closed channels → the path dies at an ×-bar;
    otherwise it loops back into the Court itself. An inert ballot glyph on
    the public band records the 0-of-7 ballot row. All states are computed
    from the exits cells — nothing hardcoded."""
    acc = "var(--accent)"
    b = ['<defs><pattern id="pmx-hatch" width="10" height="10" patternUnits="userSpaceOnUse" '
         'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="10" '
         'stroke="var(--text-muted)" stroke-width="1.4"/></pattern></defs>']
    # ladder (shifted right to make room for the return fan)
    b.append(f'<rect x="230" y="610" width="330" height="70" rx="6" fill="url(#pmx-hatch)" '
             f'stroke="{acc}" stroke-width="2"/>')
    b.append(f'<rect x="230" y="610" width="330" height="70" rx="6" fill="var(--surface)" opacity="0.55"/>')
    b.append(_pm_t(395, 651, nodes.get("public", ""), lang, size=16, fill="var(--text)", weight="600"))
    b.append(_pm_box(245, 470, 300, 60, nodes.get("knesset", ""), lang, size=16))
    b.append(_pm_box(245, 330, 300, 60, nodes.get("government", ""), lang, size=16))
    b.append(_pm_box(245, 120, 300, 72, nodes.get("court", ""), lang, fill="var(--accent-soft)", size=18))
    b.append(_pm_box(560, 212, 108, 48, nodes.get("ag", ""), lang, size=13))
    b.append(_pm_arrow(590, 260, 530, 348, "var(--text-muted)", dashed=True))  # AG → government
    # solid upward authority arrows (the public's delegation)
    b.append(_pm_arrow(395, 610, 395, 532, acc, w=2.5))
    b.append(_pm_arrow(395, 470, 395, 392, acc, w=2.5))
    b.append(_pm_arrow(395, 330, 395, 194, acc, w=2.5))
    # inert ballot on the public band: the voter's only direct channel — 0/7 open
    b.append(f'<g opacity="0.75"><rect x="585" y="628" width="42" height="30" rx="3" '
             f'fill="var(--surface)" stroke="var(--text-muted)" stroke-width="2"/>'
             f'<line x1="595" y1="636" x2="617" y2="636" stroke="var(--text-muted)" stroke-width="3"/>'
             + _pm_xbar(606, 673, 8) + '</g>')
    b.append(_pm_t(606, 622, nodes.get("ballot", ""), lang, size=12, fill="var(--text-muted)"))
    # ── the return fan: one path per mechanism, state computed from its audit ──
    origin_x, origin_y = 245, 165          # court box, lower-left edge
    chip_x = 78
    ys = [210, 272, 334, 396, 458, 520, 574]
    for mech, y in zip(mechs, ys):
        n = mech.get("num")
        exits = mech.get("exits", {})
        sts = [(exits.get(k) or {}).get("status") for k in _PM_CHANNEL_ORDER]
        closed_n = sts.count("closed")
        if "open" in sts:
            state = "open"          # exercised successfully — the path arrives
        elif closed_n >= 2:
            state = "blocked"
        else:
            state = "loop"
        muted = "var(--text-muted)"
        red = "var(--outcome-struck)"
        amb = "var(--outcome-remanded)"
        if state == "open":
            # solid path: court → chip → down to the public band (it lands)
            b.append(f'<path d="M {origin_x} {origin_y} Q 130 {y - 34} {chip_x + 16} {y}" '
                     f'fill="none" stroke="{acc}" stroke-width="2.2"/>')
            b.append(f'<path d="M {chip_x} {y + 16} Q 90 {(y + 640) / 2} 224 640" '
                     f'fill="none" stroke="{acc}" stroke-width="2.2"/>')
            b.append(_pm_arrow(210, 638, 228, 640, acc, w=2.2))
        elif state == "loop":
            # path leaves the court, dips to the chip, and curls straight back in
            b.append(f'<path d="M {origin_x} {origin_y} Q 120 {y - 30} {chip_x + 16} {y}" '
                     f'fill="none" stroke="{amb}" stroke-width="2.2" stroke-dasharray="7 4"/>')
            b.append(f'<path d="M {chip_x + 16} {y} Q 190 {y + 6} {origin_x + 22} 192" '
                     f'fill="none" stroke="{amb}" stroke-width="2.2" stroke-dasharray="7 4"/>')
            b.append(_pm_arrow(origin_x + 14, 196, origin_x + 24, 192, amb, w=2.2))
        else:
            # the path dies: dashed descent that terminates at an ×-bar
            b.append(f'<path d="M {origin_x} {origin_y} Q 120 {y - 30} {chip_x + 16} {y}" '
                     f'fill="none" stroke="{red}" stroke-width="2.2" stroke-dasharray="7 4"/>')
            b.append(f'<line x1="{chip_x - 16}" y1="{y}" x2="{chip_x - 34}" y2="{y}" '
                     f'stroke="{red}" stroke-width="2.2"/>')
            b.append(_pm_xbar(chip_x - 46, y, 11))
        chip_fill = {"open": acc, "loop": amb, "blocked": red}[state]
        b.append(f'<a href="#m-{n}"><circle cx="{chip_x}" cy="{y}" r="16" fill="var(--surface)" '
                 f'stroke="{chip_fill}" stroke-width="2.5"/>'
                 + _pm_t(chip_x, y + 5, str(n), lang, size=15, fill=chip_fill, weight="700")
                 + '</a>')
    return _pm_svg(700, title, lang, "".join(b))


# ---- meter, panels, overview, assembly -----------------------------------

def _pm_meter_html(mech, statuses, channels, lang):
    """The per-mechanism exits meter: four portal glyphs (one per correction
    channel) with the channel label, its audited status, and the cited source
    (record serif). Counts drive an aggregate line; role=img label mirrors it."""
    exits = mech.get("exits", {})
    counts = {"open": 0, "open_untested": 0, "contingent": 0, "closed": 0}
    cells = []
    for key in _PM_CHANNEL_ORDER:
        cell = exits.get(key) or {}
        status = cell.get("status", "")
        counts[status] = counts.get(status, 0) + 1
        chan_label = channels.get(key, "")
        status_label = statuses.get(status, {}).get(f"label_{lang}", "")
        cite = cell.get(f"cite_{lang}", "")
        cells.append(
            f'<div class="ps-meter-cell ps-meter-cell--{status}">'
            f'{_pm_portal_svg(status)}'
            f'<span class="ps-meter-chan">{_esc(chan_label)}</span>'
            f'<span class="ps-meter-status">{_esc(status_label)}</span>'
            f'<span class="ps-meter-cite rec">{_esc(cite)}</span>'
            f'</div>'
        )
    opn = counts["open"] + counts["open_untested"]
    if lang == "he":
        line = f'מתוך 4 ערוצי תיקון: {counts["closed"]} סגורים · {counts["contingent"]} מותנים · {opn} פתוחים'
    else:
        line = f'Of 4 correction channels: {counts["closed"]} closed · {counts["contingent"]} contingent · {opn} open'
    return (f'<div class="ps-meter" role="img" aria-label="{_esc(line)}">'
            + "".join(cells)
            + f'<p class="ps-meter-line">{_esc(line)}</p></div>')


def _pm_panel_html(mech, statuses, channels, lang):
    """One mechanism panel: numbered heading (preset id m-N), severity-ramped
    hero (outcome), bespoke diagram, exits meter, mechanism prose, optional
    comparative block, fairness aside, and the cited case links."""
    num = mech.get("num")
    title = mech.get(f"title_{lang}", "")
    title = re.sub(r"^\s*\d+\.\s*", "", title)   # ps-num already prints the number
    outcome = _pm_prose(mech.get(f"outcome_{lang}", ""), lang)
    mechanism = _pm_prose(mech.get(f"mechanism_{lang}", ""), lang)
    oneliner = mech.get(f"oneliner_{lang}", "")
    closed_n = sum(1 for k in _PM_CHANNEL_ORDER
                   if (mech.get("exits", {}).get(k) or {}).get("status") == "closed")
    parts = [
        f'<section class="ps-panel" data-ps-panel="{num}" aria-labelledby="m-{num}">',
        f'<h2 id="m-{num}"><span class="ps-num" aria-hidden="true">{num}</span> {_esc(title)}</h2>',
        f'<div class="ps-hero ps-sev-{closed_n}">{outcome}</div>',
        f'<figure class="ps-diagram">{_pm_diagram_svg(mech, lang)}'
        f'<figcaption>{_esc(oneliner)}</figcaption></figure>',
        _pm_meter_html(mech, statuses, channels, lang),
        f'<div class="ps-mech-prose">{mechanism}</div>',
    ]
    comparative = mech.get(f"comparative_{lang}")
    if comparative:
        parts.append(f'<div class="ps-compare">{_pm_prose(comparative, lang)}</div>')
    counter_label = "הצד השני של הטיעון" if lang == "he" else "The other side of the argument"
    fairness = mech.get(f"fairness_{lang}", "")
    # the JSON fairness text opens with that same label — strip it so the
    # dedicated label span does not double-print it.
    fairness = re.sub(r"^\s*" + re.escape(counter_label) + r"\s*[:：]\s*", "", fairness)
    if fairness:
        parts.append(
            f'<aside class="ps-counter"><span class="ps-counter-label">{_esc(counter_label)}</span>'
            f'{_pm_prose(fairness, lang)}</aside>'
        )
    cases = mech.get("cases") or []
    if cases:
        links = "".join(
            f'<a class="ps-case-link rec" href="ruling-{_esc(c.get("slug"))}.html">'
            f'{_esc(c.get("docket") if lang == "he" else c.get("docket_en"))}</a>'
            for c in cases if c.get("slug")
        )
        if links:
            parts.append(f'<p class="ps-cases">{links}</p>')
    parts.append('</section>')
    return "".join(parts)


def _pm_overview_html(data, lang):
    """The overview panel (data-ps-panel=0): intro, the full exit-map figure,
    three computed KPI stats + a 4th 'open' line, the 7×4 exits matrix, a card
    grid, the labelled assessment, and the awareness line. Every KPI is COUNTED
    from the exits cells here — nothing is read from a stored total."""
    ov = data.get("overview", {})
    mechs = data.get("mechanisms", [])
    statuses = data.get("statuses", {})
    channels = {c["key"]: c.get(f"label_{lang}", "") for c in data.get("channels", [])}
    nodes = _PM_NODES.get(lang, {})

    # COUNT every exits cell across all mechanisms
    total = closed = contingent = opn = ballot_open = 0
    for m in mechs:
        for k in _PM_CHANNEL_ORDER:
            st = (m.get("exits", {}).get(k) or {}).get("status")
            if st is None:
                continue
            total += 1
            if st == "closed":
                closed += 1
            elif st == "contingent":
                contingent += 1
            elif st in ("open", "open_untested"):
                opn += 1
                if k == "ballot":
                    ballot_open += 1

    def stat(mod, num, label):
        return (f'<div class="ps-stat ps-stat--{mod}"><span class="ps-stat-num rec">{num}</span>'
                f'<span class="ps-stat-label">{_esc(label)}</span></div>')

    # ballot KPI shows "open-of-7" — the voter's only direct channel (0/7 today,
    # but counted, never assumed)
    ballot_num = f"{ballot_open}/7"
    stats = (
        '<div class="ps-stats">'
        + stat("audited", total, ov.get(f"kpi_audited_{lang}", ""))
        + stat("closed", closed, ov.get(f"kpi_closed_{lang}", ""))
        + stat("ballot", ballot_num, ov.get(f"kpi_ballot_{lang}", ""))
        + stat("contingent", contingent, ov.get(f"kpi_contingent_{lang}", ""))
        + f'<p class="ps-stat-open"><span class="ps-stat-num rec">{opn}</span> '
        + f'{_esc(ov.get(f"kpi_open_{lang}", ""))}</p>'
        + '</div>'
    )

    # 7×4 matrix — row label links to #m-N, each cell titled with status + cite
    mx = [f'<div class="ps-matrix"><h3 class="ps-matrix-title">{_esc(ov.get(f"matrix_title_{lang}", ""))}</h3>',
          '<div class="ps-matrix-grid" role="table">', '<div class="ps-matrix-corner"></div>']
    for key in _PM_CHANNEL_ORDER:
        mx.append(f'<div class="ps-matrix-head">{_esc(channels.get(key, ""))}</div>')
    for m in mechs:
        n = m.get("num")
        mx.append(f'<a class="ps-matrix-rowlabel" href="#m-{n}">{_esc(m.get(f"tab_{lang}", ""))}</a>')
        for key in _PM_CHANNEL_ORDER:
            cell = m.get("exits", {}).get(key) or {}
            st = cell.get("status", "")
            st_label = statuses.get(st, {}).get(f"label_{lang}", "")
            cite = cell.get(f"cite_{lang}", "")
            mx.append(
                f'<div class="ps-matrix-cell ps-matrix-cell--{st}" title="{_esc(st_label + " — " + cite)}">'
                f'{_pm_portal_svg(st)}</div>'
            )
    mx.append('</div></div>')

    # card grid
    grid = ['<div class="ps-grid">']
    for m in mechs:
        n = m.get("num")
        grid.append(
            f'<a class="ps-card" href="#m-{n}"><span class="ps-card-num">{n}</span>'
            f'<strong>{_esc(m.get(f"tab_{lang}", ""))}</strong>'
            f'<span>{_esc(m.get(f"summary_{lang}", ""))}</span></a>'
        )
    grid.append('</div>')

    exitmap = _pm_exitmap_svg(mechs, nodes, lang, ov.get(f"map_title_{lang}", ""))

    return (
        f'<section class="ps-panel" data-ps-panel="0" aria-labelledby="m-0">'
        f'<h2 id="m-0">{_esc(ov.get(f"title_{lang}", ""))}</h2>'
        f'<p class="ps-intro">{_esc(ov.get(f"intro_{lang}", ""))}</p>'
        f'<figure class="ps-exitmap">{exitmap}'
        f'<figcaption>{_esc(ov.get(f"exitmap_oneliner_{lang}", ""))}</figcaption></figure>'
        f'{stats}'
        + "".join(mx)
        + "".join(grid)
        + f'<aside class="ps-assessment">{_pm_prose(ov.get(f"assessment_{lang}", ""), lang)}</aside>'
        + f'<p class="ps-awareness">{_esc(ov.get(f"awareness_{lang}", ""))}</p>'
        + '</section>'
    )


def _power_tabs_md(lang: str) -> str:
    """Assemble the whole Power-Structure apparatus (tab strip + overview panel
    + seven mechanism panels) as ONE top-level raw-HTML line + trailing newline,
    so python-markdown passes it through untouched. Strictly per-language."""
    data = _pm_load()
    if not data:
        return ""
    # publish the diagram-node vocabulary for the SVG builders (per language)
    global _PM_NODES
    _PM_NODES = data.get("diagram_nodes", {})
    mechs = data.get("mechanisms", [])
    statuses = data.get("statuses", {})
    channels = {c["key"]: c.get(f"label_{lang}", "") for c in data.get("channels", [])}
    ov = data.get("overview", {})
    nav_label = "מנגנוני מבנה הכוח" if lang == "he" else "Power-structure mechanisms"

    nav = [f'<nav class="ps-tabs" aria-label="{_esc(nav_label)}">',
           f'<a class="ps-tab is-active" href="#m-0" data-ps-tab="0" aria-current="true">'
           f'{_esc(ov.get(f"tab_{lang}", ""))}</a>']
    for m in mechs:
        n = m.get("num")
        nav.append(
            f'<a class="ps-tab" href="#m-{n}" data-ps-tab="{n}">'
            f'<span class="ps-tab-num">{n}</span> '
            f'<span class="ps-tab-label">{_esc(m.get(f"tab_{lang}", ""))}</span></a>'
        )
    nav.append('</nav>')

    panels = [_pm_overview_html(data, lang)]
    for m in mechs:
        panels.append(_pm_panel_html(m, statuses, channels, lang))

    block = ('<div class="ps-tabs-block">' + "".join(nav)
             + '<div class="ps-panels">' + "".join(panels) + '</div></div>')
    # guarantee the single-line invariant (no stray newline can split the block)
    block = block.replace("\n", "")
    return block + "\n"


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

            # Piece-specific build-time table injection: the source .md files
            # carry only a marker comment (see METHODOLOGY-adjacent note in
            # quiet-veto.md); the actual rows are generated here from the
            # library JSON so they can never hand-drift from it.
            if f.stem == "quiet-veto":
                qv_marker = "<!-- TABLE:quiet-veto-cases -->"
                body_he_raw = body_he_raw.replace(qv_marker, _quiet_veto_table_md("he"))
                body_en_raw = body_en_raw.replace(qv_marker, _quiet_veto_table_md("en"))
            elif f.stem == "where-the-line":
                st_marker = "<!-- TABLE:statements -->"
                body_he_raw = body_he_raw.replace(st_marker, _statement_table_md("he"))
                body_en_raw = body_en_raw.replace(st_marker, _statement_table_md("en"))
            elif f.stem == "power-structure":
                ps_marker = "<!-- TABS:power-mechanisms -->"
                body_he_raw = body_he_raw.replace(ps_marker, _power_tabs_md("he"))
                body_en_raw = body_en_raw.replace(ps_marker, _power_tabs_md("en"))

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
            f'<p><a href="{xml_escape(r.get("official_url",""))}">'
            f'{xml_escape(_official_label_he(r.get("official_url","")))}</a></p>'
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
        f'    <title>Bakshi&amp;Bitton · בקשי&amp;ביטון</title>\n'
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
        "tags": {"he": TAG_LABELS_HE},
    }
    (out_dir / "labels.json").write_text(
        json.dumps(labels, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ─── Ruling-day kit (share cards + post text) ────────────────────────────
# One shareable kit per ruling, under site/assets/kits/<slug>/:
#   card-he.png / card-en.png — 1200×675 social cards, drawn with PIL
#   post-he.txt / post-en.txt — ready-to-paste post text
# Everything on a card comes from the ruling record; nothing is characterized
# or invented. A field the record does not carry is printed as "—" and named
# in the build summary.
#
# Typography follows the site's semantic split: David Libre (serif) for text
# taken from the court record — case id, case name, panel/vote, date — and
# Assistant (sans) for the project's own words and UI (brand, page URL, and
# the outcome chip, which prints our canonical OUTCOME_LABELS_* label rather
# than the court's own wording).
# The site self-hosts those faces as woff2, which PIL/FreeType cannot read, and
# neither family exists as TTF/OTF on this machine; scripts/fonts/ therefore
# holds the *same* Google-Fonts faces losslessly decompressed from the site's
# own woff2 subsets (fontTools), never a substitute typeface. The subsets are
# split hebrew/latin, so each line is drawn as a sequence of script runs.

KITS_DIR = SITE_DIR / "assets" / "kits"
KIT_FONTS_DIR = REPO_ROOT / "scripts" / "fonts"
CARD_W, CARD_H = 1200, 675

# Palette mirrors site/assets/style.css (:root)
C_BG = (250, 249, 247)          # --bg      warm paper
C_INK = (31, 35, 40)            # --text
C_MUTED = (91, 97, 107)         # --text-muted
C_BORDER = (232, 228, 221)      # --border
C_ACCENT = (35, 63, 102)        # --accent  deep navy
C_ACCENT_DEEP = (22, 38, 63)    # --accent-deep
C_ACCENT_SOFT = (233, 238, 246)  # --accent-soft

_HEB_RANGE = ((0x0590, 0x05FF), (0xFB1D, 0xFB4F))

try:
    from PIL import Image, ImageDraw, ImageFont
    from bidi.algorithm import get_display
    _KIT_DEPS_ERR = None
except ImportError as _e:  # pragma: no cover - environment guard
    _KIT_DEPS_ERR = str(_e)


def kit_dir_url(slug: str) -> str:
    return f"{SITE_BASE_URL}/assets/kits/{slug}"


def kit_card_url(slug: str, lang: str = "he") -> str:
    return f"{kit_dir_url(slug)}/card-{lang}.png"


_font_cache: dict = {}


def _font(family: str, weight: int, script: str, size: int):
    """Load one subset face (family/weight/script) at `size`. BASIC layout is
    forced: bidi reordering is done explicitly with python-bidi, and a Raqm
    layout engine would reorder a second time."""
    key = (family, weight, script, size)
    f = _font_cache.get(key)
    if f is None:
        path = KIT_FONTS_DIR / f"{family}-{script}-{weight}.ttf"
        if not path.exists():
            raise SystemExit(f"kit: missing build font {path}")
        f = ImageFont.truetype(str(path), size,
                               layout_engine=ImageFont.Layout.BASIC)
        _font_cache[key] = f
    return f


def _is_heb(ch: str) -> bool:
    o = ord(ch)
    return any(lo <= o <= hi for lo, hi in _HEB_RANGE)


def _script_runs(text: str):
    """Split a visual-order string into (run_text, script) pairs, so each run
    is drawn with the subset that actually carries its glyphs."""
    runs, cur, cur_s = [], "", None
    for ch in text:
        s = "hebrew" if _is_heb(ch) else "latin"
        if cur_s is None or s == cur_s:
            cur, cur_s = cur + ch, s
        else:
            runs.append((cur, cur_s))
            cur, cur_s = ch, s
    if cur:
        runs.append((cur, cur_s))
    return runs


# LRM markers keep a self-contained LTR token (the vote pair) from being
# re-ordered by the bidi pass — "2–1" must not surface as "1–2", since the
# first number is the majority. They are stripped again before drawing: they
# are zero-width formatting characters with no glyph in the subsets.
_LRM = "\u200e"


def _visual(text: str, rtl: bool) -> str:
    return get_display(text or "", base_dir="R" if rtl else "L").replace(
        _LRM, "").replace("\u200f", "")


def _line_w(text: str, family: str, weight: int, size: int, rtl: bool) -> float:
    return sum(_font(family, weight, s, size).getlength(t)
               for t, s in _script_runs(_visual(text, rtl)))


def _draw_line(draw, text: str, x_edge: int, baseline: int, family: str,
               weight: int, size: int, fill, rtl: bool,
               align_right: bool | None = None) -> float:
    """Draw one line on `baseline`, anchored at `x_edge` — the right edge when
    the line is right-aligned (RTL by default), the left edge otherwise.
    `rtl` sets the bidi base direction; `align_right` overrides alignment only
    (an LTR-shaped line, e.g. a URL, flushed right on a Hebrew card). Returns
    the drawn width."""
    if align_right is None:
        align_right = rtl
    runs = _script_runs(_visual(text, rtl))
    widths = [_font(family, weight, s, size).getlength(t) for t, s in runs]
    total = sum(widths)
    x = (x_edge - total) if align_right else x_edge
    for (t, s), w in zip(runs, widths):
        draw.text((x, baseline), t, font=_font(family, weight, s, size),
                  fill=fill, anchor="ls")
        x += w
    return total


def _fit_size(text: str, family: str, weight: int, size: int, max_w: int,
              rtl: bool, floor: int = 20) -> int:
    """Largest size ≤ `size` (stepping down by 2) whose line fits `max_w`."""
    while size > floor and _line_w(text, family, weight, size, rtl) > max_w:
        size -= 2
    return size


def _wrap2(text: str, family: str, weight: int, size: int, max_w: int,
           rtl: bool) -> list:
    """Greedy word wrap to at most 2 lines; the 2nd is ellipsized when the text
    does not fit. Wrapping happens in logical order; bidi runs at draw time."""
    words = (text or "").split()
    if not words:
        return [""]
    rem = list(words)
    lines = []
    while rem and len(lines) < 2:
        cur = [rem.pop(0)]
        while rem and _line_w(" ".join(cur + [rem[0]]), family, weight, size,
                              rtl) <= max_w:
            cur.append(rem.pop(0))
        lines.append(" ".join(cur))
    if rem:  # more text than two lines hold → ellipsize the last one
        last = lines[-1].split()
        while last and _line_w(" ".join(last) + "…", family, weight, size,
                               rtl) > max_w:
            last.pop()
        lines[-1] = (" ".join(last) + "…") if last else "…"
    return lines


def _kit_fields(r: dict, lang: str) -> tuple[dict, list]:
    """Card/post fields for one ruling, straight from the record. Returns
    (fields, missing_field_names). Missing values are rendered as '—'."""
    dash = "—"
    missing = []

    def take(value, name):
        if value in (None, "", []):
            missing.append(name)
            return dash
        return str(value)

    case_id = take(r.get("case_id"), "case_id")
    name_key = "case_name_he" if lang == "he" else "case_name_en"
    case_name = take(r.get(name_key), name_key)
    outcome = r.get("outcome")
    labels = OUTCOME_LABELS_HE if lang == "he" else OUTCOME_LABELS_EN
    outcome_txt = (labels.get(outcome, outcome) if outcome
                   else take(outcome, "outcome"))
    date = take(r.get("ruling_date"), "ruling_date")

    panel = r.get("panel") or []
    if not panel:
        missing.append("panel")
        panel_names = dash
        panel_count = dash
    else:
        key = "name_he" if lang == "he" else "name_en"
        panel_names = ", ".join(j.get(key) or j.get("name_he") or "" for j in panel)
        panel_count = (f"{len(panel)} שופטים" if lang == "he"
                       else f"{len(panel)} justices")
    if r.get("vote_majority") in (None, ""):
        missing.append("vote_majority")
        vote = dash
    else:
        vote = f'{r.get("vote_majority")}–{r.get("vote_minority") or 0}'

    lbl_panel, lbl_vote = ("הרכב", "הצבעה") if lang == "he" else ("Panel", "Vote")
    return ({
        "case_id": case_id,
        "case_name": case_name,
        "outcome": outcome_txt,
        "date": date,
        "panel_names": panel_names,
        "panel_count": panel_count,
        "vote": vote,
        # plain (logical order) for the post files; LRM-fenced vote for the
        # cards, which are rendered here rather than by a bidi-aware client
        "panel_line": f"{lbl_panel}: {panel_names} · {lbl_vote}: {vote}",
        "panel_line_card":
            f"{lbl_panel}: {panel_names} · {lbl_vote}: {_LRM}{vote}{_LRM}",
        "panel_line_short_card":
            f"{lbl_panel}: {panel_count} · {lbl_vote}: {_LRM}{vote}{_LRM}",
        "page_url": f"{SITE_BASE_URL}/ruling-{r.get('case_id_slug', '')}.html",
        "official_url": r.get("official_url") or "",
    }, missing)


def render_kit_card(r: dict, lang: str):
    """Draw one 1200×675 RGB share card. Deterministic: no timestamps, no
    randomness — same record in, same bytes out."""
    rtl = (lang == "he")
    f, _ = _kit_fields(r, lang)
    img = Image.new("RGB", (CARD_W, CARD_H), C_BG)
    d = ImageDraw.Draw(img)
    m = 64                      # page margin
    edge = (CARD_W - m) if rtl else m
    max_w = CARD_W - 2 * m

    # Top band — brand (project voice, sans)
    band_h = 96
    d.rectangle([0, 0, CARD_W, band_h], fill=C_ACCENT)
    brand = "בקשי&ביטון" if rtl else "Bakshi&Bitton"
    _draw_line(d, brand, edge, 62, "assistant", 700, 36, C_BG, rtl)

    # Ruling date (record, serif)
    _draw_line(d, f["date"], edge, 172, "david-libre", 400, 26, C_MUTED, rtl)

    # Case id (record, serif, large)
    cid_size = _fit_size(f["case_id"], "david-libre", 700, 56, max_w, rtl, 28)
    _draw_line(d, f["case_id"], edge, 252, "david-libre", 700, cid_size, C_INK, rtl)

    # Case name (record, serif, ≤ 2 lines)
    for i, line in enumerate(_wrap2(f["case_name"], "david-libre", 500, 34,
                                    max_w, rtl)):
        _draw_line(d, line, edge, 316 + i * 46, "david-libre", 500, 34,
                   C_INK, rtl)

    # Outcome chip — the project's own canonical label (OUTCOME_LABELS_HE/_EN),
    # not the court's wording, so it is set in the voice sans (Assistant 700).
    chip_font_size, pad_x, chip_h, chip_top = 32, 26, 64, 412
    chip_w = _line_w(f["outcome"], "assistant", 700, chip_font_size, rtl) + 2 * pad_x
    x0 = (CARD_W - m - chip_w) if rtl else m
    d.rounded_rectangle([x0, chip_top, x0 + chip_w, chip_top + chip_h],
                        radius=chip_h // 2, fill=C_ACCENT_SOFT,
                        outline=C_ACCENT, width=2)
    asc, desc = _font("assistant", 700, "latin", chip_font_size).getmetrics()
    chip_base = chip_top + (chip_h - (asc + desc)) // 2 + asc
    _draw_line(d, f["outcome"], (x0 + chip_w - pad_x) if rtl else (x0 + pad_x),
               chip_base, "assistant", 700, chip_font_size, C_ACCENT_DEEP, rtl)

    # Panel · vote (record, serif) — names when they fit, else the panel size
    pv, pv_size = f["panel_line_card"], 26
    if _line_w(pv, "david-libre", 400, pv_size, rtl) > max_w:
        pv_size = _fit_size(pv, "david-libre", 400, pv_size, max_w, rtl, 22)
        if _line_w(pv, "david-libre", 400, pv_size, rtl) > max_w:
            pv, pv_size = f["panel_line_short_card"], 26
    _draw_line(d, pv, edge, 540, "david-libre", 400, pv_size, C_INK, rtl)

    # Bottom band — page URL (project voice, sans). Legibility floor is 26px,
    # so the scheme is dropped (browser-style display of the same URL) and the
    # band runs to a tighter margin; the full URL stays in the post text and in
    # the page's own meta. The longest slug in the corpus fits at 26px.
    foot_h, foot_m = 84, 44
    d.rectangle([0, CARD_H - foot_h, CARD_W, CARD_H], fill=C_ACCENT_DEEP)
    url_txt = f["page_url"].split("://", 1)[-1]
    url_size = _fit_size(url_txt, "assistant", 600, 28, CARD_W - 2 * foot_m,
                         False, 26)
    _draw_line(d, url_txt, (CARD_W - foot_m) if rtl else foot_m,
               CARD_H - foot_h + 54, "assistant", 600, url_size, C_BG, False,
               align_right=rtl)
    return img


def render_kit_posts(r: dict) -> dict:
    """post-he.txt (5 lines) and post-en.txt (3 lines), record fields only.
    An English field the record does not carry becomes NOT AVAILABLE."""
    he, _ = _kit_fields(r, "he")
    en, _ = _kit_fields(r, "en")
    na = "NOT AVAILABLE"

    def en_or_na(v, dash_ok=("—", "")):
        return na if (v in dash_ok or not v) else v

    # A source line that is NOT on a .gov.il host is prefixed, so a pasted post
    # never presents a newspaper or an archive as the official ruling text.
    src_he = he["official_url"]
    if src_he and not is_official_host(src_he):
        src_he = f"מקור משני: {src_he}"
    post_he = "\n".join([
        f'{he["case_id"]} — {he["outcome"]}',
        he["case_name"],
        he["panel_line"],
        src_he or "—",
        he["page_url"],
    ]) + "\n"
    en_id = en_or_na(en["case_id"])
    en_outcome = en_or_na(en["outcome"])
    src_en = en["official_url"]
    if src_en and not is_official_host(src_en):
        src_en = f"Secondary source: {src_en}"
    post_en = "\n".join([
        f'{en_id} — {en_outcome}',
        en_or_na(en["case_name"]),
        f'{src_en or na} · {en["page_url"]}',
    ]) + "\n"
    return {"post-he.txt": post_he, "post-en.txt": post_en}


def build_kits(site_dir: Path, rulings: list) -> dict:
    """Write site/assets/kits/<slug>/ for every ruling. Deterministic output:
    re-running the build rewrites byte-identical PNGs."""
    if _KIT_DEPS_ERR:
        print(f"ERROR: kit step needs Pillow + python-bidi ({_KIT_DEPS_ERR}).",
              file=sys.stderr)
        print("Install with: pip3 install --user Pillow python-bidi",
              file=sys.stderr)
        raise SystemExit(2)
    out_root = site_dir / "assets" / "kits"
    out_root.mkdir(parents=True, exist_ok=True)
    cards = posts = 0
    gaps = []
    for r in rulings:
        slug = r.get("case_id_slug")
        if not slug:
            continue
        d = out_root / slug
        d.mkdir(parents=True, exist_ok=True)
        miss = set()
        for lang in ("he", "en"):
            _, m = _kit_fields(r, lang)
            miss |= set(m)
            render_kit_card(r, lang).save(d / f"card-{lang}.png", format="PNG")
            cards += 1
        if not (r.get("official_url") or "").strip():
            miss.add("official_url")
        for fname, text in render_kit_posts(r).items():
            (d / fname).write_text(text, encoding="utf-8")
            posts += 1
        if miss:
            gaps.append((slug, sorted(miss)))
    return {"rulings": len(rulings), "cards": cards, "posts": posts,
            "gaps": gaps}


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
               og_image: str = OG_IMAGE,
               og_image_size: tuple | None = None) -> str:
    """Full <head> with localized title, description, OG, Twitter, canonical,
    favicon, and optional JSON-LD. `og_image_size` is the (w, h) of `og_image`
    — declared only when known, since the default card and the per-ruling kit
    cards are different sizes."""
    canonical = f"{SITE_BASE_URL}/{canonical_path}"
    desc = " ".join((description or "").split())[:300]
    parts = [
        '<!DOCTYPE html>',
        '<html lang="he" dir="rtl">',
        '<head>',
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f'<title>{_esc(title_he)} · בקשי&amp;ביטון</title>',
        f'<meta name="description" content="{_esc(desc)}">',
        # Let search engines show a large image preview (Discover eligibility)
        '<meta name="robots" content="max-image-preview:large">',
        f'<link rel="canonical" href="{_esc(canonical)}">',
        '<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">',
        '<link rel="stylesheet" href="assets/style.css">',
        '<link rel="alternate" type="application/rss+xml" title="Bakshi&Bitton — new rulings" href="feed.xml">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:site_name" content="Bakshi&amp;Bitton · בקשי&amp;ביטון">',
        f'<meta property="og:title" content="{_esc(title_he)}">',
        f'<meta property="og:description" content="{_esc(desc)}">',
        f'<meta property="og:url" content="{_esc(canonical)}">',
        f'<meta property="og:image" content="{_esc(og_image)}">',
    ]
    if og_image_size:
        parts += [
            f'<meta property="og:image:width" content="{int(og_image_size[0])}">',
            f'<meta property="og:image:height" content="{int(og_image_size[1])}">',
        ]
    parts += [
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
        '<div><a class="logo" href="index.html">בקשי&amp;ביטון'
        '<span class="logo-sub">פסיקות בית המשפט העליון בעניין החלטות ממשלה ומינויים</span>'
        '</a></div>'
        '<nav>'
        + nav("index.html", "פסיקות", "rulings")
        + nav("reading.html", "קריאה", "reading")
        + nav("justices.html", "שופטים", "justices")
        + nav("tags.html", "נושאים", "tags")
        + nav("timeline.html", "ציר זמן", "timeline")
        + nav("reading-power-structure.html", "מבנה הכוח", "structure")
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


# Editorial satire (DISPLAY-ONLY): render the petitioner "Movement for Quality
# Government" with its "for quality" claim struck through and annotated
# "(for abolition)". The documentary data keeps the org's real, factual name;
# this transform runs at render time over the visible <body> only (never the
# head/title/OG/JSON-LD), so the structured record and SEO stay accurate.
_MQG_HE = re.compile(r'התנועה למען איכות השלטון')
_MQG_EN = re.compile(r'Movement for Quality Government', re.IGNORECASE)


def _satirize_mqg(html: str) -> str:
    if not html:
        return html
    html = _MQG_HE.sub('התנועה למען <del class="mqg-strike">איכות</del>(ביטול) השלטון', html)
    html = _MQG_EN.sub('Movement for <del class="mqg-strike">Quality</del> (Abolition of) Government', html)
    return html


# Hidden 1×1 visitor pixel (no account, no cookie): a third counter key for the
# content pages — the four hub shells keep their own keys, untouched. The
# clip-based hiding is load-bearing: an off-screen `left:-9999px` would break
# the RTL layout.
_VISITOR_PIXEL_CONTENT = (
    '<img src="https://visitor-badge.laobi.icu/badge?page_id='
    'eleazarbensimon.bakshi-content" alt="" aria-hidden="true" width="1" '
    'height="1" style="position:absolute;width:1px;height:1px;overflow:hidden;'
    'clip:rect(0,0,0,0);opacity:0;pointer-events:none" />'
)


def _ruling_hero(r: dict) -> str:
    """Bold public-facing hero atop each ruling page: the verdict in large type,
    the case, the sharp summary, and a stat strip foregrounding WHO acted —
    panel size, vote, and the justices who authored the lead opinion."""
    outcome = r.get("outcome", "")
    label = OUTCOME_LABELS_HE.get(outcome, outcome)
    panel = r.get("panel") or []
    n = len(panel)
    slug2name = {j.get("slug"): j.get("name_he") for j in panel}
    leads = [slug2name.get(s, s) for s in (r.get("majority_authors") or []) if slug2name.get(s, s)]
    stats = []
    if n:
        stats.append(f'<span class="rh-stat"><b>{n}</b> שופטים</span>')
    if r.get("vote_majority") is not None:
        # <bdi dir="ltr">: inside RTL text the en dash between two digits makes
        # bidi resolve the pair right-to-left, so "2–1" would display as "1–2"
        # — inverting majority and minority. The isolate pins majority-first.
        stats.append(f'<span class="rh-stat">הצבעה <b><bdi dir="ltr">'
                     f'{_esc(r.get("vote_majority"))}–{_esc(r.get("vote_minority") or 0)}'
                     f'</bdi></b></span>')
    if leads:
        stats.append(f'<span class="rh-stat">חוות-הדעת המובילה: <b>{_esc(", ".join(leads))}</b></span>')
    stat_html = ('<div class="rh-stats">' + "".join(stats) + '</div>') if stats else ''
    return (
        '<div class="ruling-hero">'
        f'<span class="rh-verdict outcome-pill outcome-{_esc(outcome)}">{_esc(label)}</span>'
        f'<h1 class="rh-case">{_esc(r.get("case_id", ""))}</h1>'
        f'<p class="rh-name">{_esc(r.get("case_name_he", ""))}</p>'
        f'<p class="rh-summary">{_esc(r.get("summary_he", ""))}</p>'
        f'{stat_html}'
        '</div>'
    )


def render_ruling_page(r: dict) -> str:
    slug = r.get("case_id_slug", "")
    case_id = r.get("case_id", "")
    name_he = r.get("case_name_he", "")
    summary_he = r.get("summary_he", "")
    spa_url = f"ruling.html?id={slug}"
    # The ruling's own share card is this page's social preview.
    card_url = kit_card_url(slug, "he")

    # JSON-LD: model each ruling as an Article about a legal decision, with the
    # official ruling as isBasedOn (provenance).
    jsonld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": f"{case_id} — {name_he}",
        "inLanguage": "he",
        "datePublished": r.get("ruling_date", ""),
        "url": f"{SITE_BASE_URL}/ruling-{slug}.html",
        "image": card_url,
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
        og_image=card_url, og_image_size=(CARD_W, CARD_H),
    )

    # Detail grid (humanized Hebrew labels)
    rows = []
    # `rec=True` marks a value taken verbatim from the court record (dates,
    # party names, doctrine, vote) → rendered in the record serif via .rec. The
    # project's own classifications (petitioner type, outcome label, compliance,
    # our description of the appealed decision, tags) stay in the voice sans.
    def row(label, value, rec=False):
        if value in (None, "", []):
            return
        cls = ' class="rec"' if rec else ''
        rows.append(f"<dt>{_esc(label)}</dt><dd{cls}>{value}</dd>")
    row("תאריך הפסיקה", _esc(r.get("ruling_date")), rec=True)
    if r.get("filing_date"):
        row("תאריך הגשה", _esc(r["filing_date"]), rec=True)
    row("סוג עותר", _esc(PETITIONER_TYPE_HE.get(r.get("petitioner_type"), r.get("petitioner_type"))))
    row("עותר", _esc(r.get("petitioner_name_he")), rec=True)
    resp = RESPONDENT_HE.get(r.get("respondent"), r.get("respondent"))
    row("משיב", _esc(resp), rec=True)
    if r.get("respondent_body_he") or r.get("respondent_body"):
        row("גוף נושא ההחלטה", _esc(r.get("respondent_body_he") or r.get("respondent_body")), rec=True)
    if r.get("respondent_decision_he"):
        row("ההחלטה המעורערת", _esc(r["respondent_decision_he"]))
    doctrines = ", ".join(DOCTRINE_LABELS_HE.get(d, d) for d in (r.get("doctrine_invoked") or []))
    row("עילות שנטענו", _esc(doctrines), rec=True)
    outcome = r.get("outcome", "")
    row("תוצאה", f'<span class="outcome-pill outcome-{_esc(outcome)}">'
                 f'{_esc(OUTCOME_LABELS_HE.get(outcome, outcome))}</span>')
    if r.get("vote_majority") is not None:
        # bdi isolate: majority first, not bidi-reversed (see _ruling_hero)
        row("הצבעה", f'<bdi dir="ltr">{_esc(r.get("vote_majority"))}–'
                     f'{_esc(r.get("vote_minority") or 0)}</bdi>', rec=True)
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
        # Only a .gov.il host carries the authoritative ruling; anything else
        # (a newspaper, Versa) is a stand-in for a text that is not online, and
        # the link must say so rather than promise "the official ruling".
        label = "→ " + _official_label_he(r["official_url"])
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

    why = ""
    wm_he = r.get("why_matters_he")
    if wm_he:
        why = ('<details class="why-matters" open>'
               '<summary>למה זה חשוב</summary>'
               f'<div class="why-matters-body">{_esc(wm_he)}</div></details>')

    body = (
        f'<div id="root">{_static_header("rulings")}<main>'
        f'<p><a href="index.html">← פסיקות</a></p>'
        f'{_ruling_hero(r)}'
        f'{why}'
        f'{comic}{print_cite}{official}{grid}{panel}{secondary}{notes}{related}'
        f'<p style="margin-top:24px;font-size:14px"><a href="{_esc(spa_url)}">'
        f'גרסה אינטראקטיבית מלאה / English →</a></p>'
        f'{_share_bar(f"{SITE_BASE_URL}/ruling-{slug}.html", (case_id + " — " + name_he) if name_he else case_id)}'
        f'</main>{_STATIC_FOOTER}</div>'
    )
    # data-spa on the toggle so it routes to this ruling's SPA view
    body = _spa_toggle(body, spa_url)
    body = _satirize_mqg(body)
    return (head + '\n<body>\n' + _VISITOR_PIXEL_CONTENT + '\n' + body
            + '\n</body>\n</html>\n')


def _toc_slug(text: str) -> str:
    """Mirror the SPA slugify (app.js): lowercase, keep Hebrew, strip
    punctuation, spaces->hyphens, cap length — so static-page anchors are
    stable and internally consistent with their TOC links."""
    s = (text or "").lower().strip()
    s = re.sub(r"[^\w֐-׿\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    return s[:80]


def _content_toc(body_html: str, lang: str):
    """Build an 'On this page' content-map for a static article, matching the
    SPA's `.toc-sidebar` markup so the static and interactive views agree.
    Injects stable ids onto h2/h3 in the body; returns (body_with_ids,
    toc_html). Returns the body unchanged + '' if there are < 2 headings."""
    seen = set()
    entries = []

    def repl(m):
        # Two alternatives in the pattern: a heading (groups 1-3) or a table row
        # carrying data-toc-label (groups 4-5). Rows already have an id, so they
        # become h3-level bullets pointing at that row; headings get an id
        # injected if missing. re.sub processes matches in document order, so
        # entries stay ordered (e.g. table h2, then its rows).
        if m.group(1):  # heading
            level, attrs, inner = m.group(1), m.group(2), m.group(3)
            text = re.sub(r"<[^>]+>", "", inner).strip()
            if not text:
                return m.group(0)
            idm = re.search(r'id="([^"]+)"', attrs)
            if idm:
                hid, out = idm.group(1), m.group(0)
            else:
                base = "h-" + (_toc_slug(text) or f"section-{len(entries)}")
                hid, n = base, 1
                while hid in seen:
                    n += 1
                    hid = f"{base}-{n}"
                out = f'<{level}{attrs} id="{hid}">{inner}</{level}>'
            seen.add(hid)
            entries.append((level, hid, text))
            return out
        # tagged table row: group(4)=attrs, group(5)=label
        tr_attrs, label = m.group(4), (m.group(5) or "").strip()
        idm = re.search(r'id="([^"]+)"', tr_attrs)
        if idm and label:
            seen.add(idm.group(1))
            entries.append(("h3", idm.group(1), label))
        return m.group(0)

    new_body = re.sub(
        r'<(h2|h3)([^>]*)>(.*?)</\1>|<tr\b([^>]*\bdata-toc-label="([^"]*)"[^>]*)>',
        repl, body_html, flags=re.S,
    )
    if len(entries) < 2:
        return body_html, ""
    title = "תוכן העמוד" if lang == "he" else "On this page"
    items = "".join(
        f'<li class="toc-item toc-item--{lvl}"><a class="toc-link" href="#{hid}">{txt}</a></li>'
        for lvl, hid, txt in entries
    )
    toc = (f'<aside class="toc-sidebar" aria-label="{title}">'
           f'<div class="toc-title">{title}</div>'
           f'<ol class="toc-list">{items}</ol></aside>')
    return new_body, toc


# Self-contained content-map behaviour (mobile toggle + scroll-spy) for the
# static reading pages — mirrors the SPA's TOC without needing app.js.
_TOC_SCRIPT = (
    '<script>(function(){'
    'var b=document.querySelector(".toc-mobile-toggle"),s=document.querySelector(".toc-sidebar");'
    'if(b&&s){var o=false;b.addEventListener("click",function(){o=!o;s.classList.toggle("toc-sidebar--open",o);b.classList.toggle("active",o);});'
    's.addEventListener("click",function(e){if(e.target.closest(".toc-link")&&o){o=false;s.classList.remove("toc-sidebar--open");b.classList.remove("active");}});}'
    'var ls=[].slice.call(document.querySelectorAll(".toc-link"));'
    'if(ls.length&&"IntersectionObserver"in window){var mp={};ls.forEach(function(l){var h=document.getElementById(l.getAttribute("href").slice(1));if(h)mp[h.id]=l;});'
    'var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){ls.forEach(function(l){l.classList.remove("active");});if(mp[en.target.id])mp[en.target.id].classList.add("active");}});},{rootMargin:"0px 0px -75% 0px"});'
    'Object.keys(mp).forEach(function(id){io.observe(document.getElementById(id));});}'
    '})();</script>'
)


def render_content_static_page(piece: dict, category: str) -> str:
    slug = piece.get("slug", "")
    title_he = piece.get("title_he") or piece.get("title") or slug
    summary_he = piece.get("summary_he") or piece.get("summary") or ""
    body_html = piece.get("body_html_he") or piece.get("body_html") or ""
    spa_url = f"content.html?slug={slug}"
    badge = {"essays": "מאמר", "explainers": "הסבר", "patterns": "תיעוד דפוס",
             "structure": "מבנה הכוח"}.get(category, category)

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
    # Content-map: inject heading ids + build the same sidebar the SPA shows,
    # so the static SEO page and the interactive view match.
    body_html, toc_html = _content_toc(body_html, "he")
    toc_btn = ('<button type="button" class="toc-mobile-toggle">תוכן העמוד ▾</button>'
               if toc_html else "")
    article = (
        f'<article class="content-article" dir="auto">'
        f'<header class="article-header">'
        f'<span class="article-badge article-badge--{_esc(category)}">{_esc(badge)}</span>'
        f'<h1 class="article-title" dir="auto">{_esc(title_he)}</h1>{qa}</header>'
        f'{toc_btn}'
        f'<div class="article-body">{body_html}</div>'
        f'<p style="margin-top:24px;font-size:14px"><a href="{_esc(spa_url)}">'
        f'גרסה אינטראקטיבית מלאה / English →</a></p>'
        f'{_share_bar(f"{SITE_BASE_URL}/reading-{slug}.html", title_he)}'
        f'</article>'
    )
    inner = f'<div class="content-layout">{article}{toc_html}</div>' if toc_html else article
    body = (
        f'<div id="root">{_static_header("structure" if category == "structure" else "reading")}<main>'
        f'<p class="breadcrumb"><a href="reading.html">קריאה</a> / {_esc(badge)}</p>'
        f'{inner}</main>{_STATIC_FOOTER}</div>'
    )
    body = _spa_toggle(body, spa_url)
    body = _satirize_mqg(body)
    # Load the shared script so client-side enhancements work on these
    # otherwise-static pages (the Quiet-Veto "contribute" modal); plus a
    # small self-contained script for the content-map (mobile toggle +
    # scroll-spy). Neither re-renders the already-baked content.
    toc_script = _TOC_SCRIPT if toc_html else ""
    return (head + '\n<body>\n' + _VISITOR_PIXEL_CONTENT + '\n' + body
            + '\n<script src="assets/app.js"></script>\n' + toc_script + '\n</body>\n</html>\n')


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


# ─── Prerendered hub shells (index / reading / tags / about) ─────────────
# The four hub pages stay client-rendered SPAs, but each ships a baked
# Hebrew body inside its <div id="root"> so crawlers and no-JS readers get
# real content (and every ruling / reading page is linked from a static
# href). The shells carry PRERENDER marker pairs; the generators below fill
# the space between them on every build, idempotently.
# mirrors the inline scripts of site/index.html / reading.html / tags.html
# and app.js i18n.he — keep text in sync.

def _inject_block(text: str, name: str, html_block: str, fname: str) -> str:
    """Replace whatever sits between the BEGIN/END markers for `name` with
    `html_block` (the markers themselves stay). A function replacement is used
    (never a template string) because the generated HTML may contain
    backslashes that re.sub would otherwise read as group references."""
    pat = re.compile(
        r'(<!-- PRERENDER:' + re.escape(name) + r':BEGIN -->)'
        r'.*?'
        r'(<!-- PRERENDER:' + re.escape(name) + r':END -->)',
        flags=re.S)
    if not pat.search(text):
        raise SystemExit(f"prerender marker {name} missing in {fname}")
    return pat.sub(lambda m: m.group(1) + "\n" + html_block + "\n" + m.group(2),
                   text, count=1)


def _spa_toggle(header_html: str, spa_url: str) -> str:
    """Point the header's EN toggle at the interactive SPA route for the page."""
    return header_html.replace(
        'class="lang-toggle"', f'class="lang-toggle" data-spa="{_esc(spa_url)}"')


# mirrors app.js LABELS.tags.he — keep in sync
TAG_LABELS_HE = {
    "knesset-internal-vote": "הצבעה פנימית בכנסת", "secret-ballot": "הצבעה חשאית", "state-comptroller": "מבקר המדינה",
    "headliner": "תיק דגל", "reasonableness": "עילת הסבירות", "basic-law-strike": "פסילה מכוח חוק-יסוד",
    "doctrine-anchor": "עוגן דוקטרינרי", "basic-law-amendment": "תיקון לחוק-יסוד", "expanded-panel": "הרכב מורחב",
    "post-oct7": "אחרי ה-7 באוקטובר", "abuse-of-constituent-power": "שימוש לרעה בסמכות מכוננת",
    "anti-infiltration": "חוק למניעת הסתננות", "appointment-block": "חסימת מינויים", "asylum-seekers": "מבקשי מקלט",
    "conflict-of-interest": "ניגוד עניינים", "constituent-authority": "סמכות מכוננת", "constitutional-revolution": "המהפכה החוקתית",
    "en-banc": "הרכב מלא", "mandatory-order": "צו עשה", "pre-digital": "טרום-העידן הדיגיטלי", "shin-bet": "השב״כ",
    "administrative-failure": "כשל מינהלי", "administrative-review": "ביקורת מינהלית", "ag-non-defense": "סירוב היועמ״ש להגן על החוק",
    "appointments-committee": "ועדת המינויים", "attorney-general": "היועץ המשפטי לממשלה", "barak-court": "בית המשפט של ברק",
    "basic-law-government": "חוק-יסוד: הממשלה", "basic-law-supremacy": "עליונות חוקי-היסוד", "borderline-scope": "תחום גבולי",
    "cabinet-resolution": "החלטת ממשלה", "civil-wrongs": "עוולות אזרחיות (אחריות המדינה)", "coalition-arrangement": "הסדר קואליציוני",
    "conscription": "גיוס", "consolidated-petitions": "עתירות מאוחדות", "contempt": "ביזיון בית המשפט",
    "declaratory": "סעד הצהרתי", "deri": "פרשת דרעי", "detention": "מעצר והחזקה", "doctrinal-foundation": "תשתית דוקטרינרית",
    "executive-action": "פעולת הרשות המבצעת", "first-of-kind": "תקדים ראשון מסוגו", "gas-framework": "מתווה הגז",
    "gatekeeper": "שומרי הסף", "haredi-conscription": "גיוס חרדים", "haredi-draft": "גיוס בני ישיבות", "haredi-politics": "פוליטיקה חרדית",
    "holot": "מתקן חולות", "incapacitation": "נבצרות", "judicial-review": "ביקורת שיפוטית",
    "judicial-selection-committee": "הוועדה לבחירת שופטים", "local-authority": "רשות מקומית", "minister-appointment": "מינוי שר",
    "ministerial-appointment": "מינוי שרים", "ministerial-decision": "החלטת שר", "ministerial-duty": "חובת שר",
    "ngo-petitioner": "עותר מהחברה האזרחית", "personal-legislation": "חקיקה פרסונלית", "prison-conditions": "תנאי מאסר",
    "privatization": "הפרטה", "property-rights": "זכות הקניין", "qatargate": "פרשת קטארגייט", "reliance-interest": "אינטרס ההסתמכות",
    "religion-and-state": "דת ומדינה", "religious-services": "שירותי דת", "security-appointment": "מינוי ביטחוני",
    "security-sector": "מערכת הביטחון", "senior-appointments": "מינויים בכירים", "settlements": "התנחלויות",
    "sovereign-function": "תפקיד שלטוני", "state-immunity": "חסינות המדינה", "supreme-court-president": "נשיא בית המשפט העליון",
    "tal-law": "חוק טל", "transition-period": "תקופת מעבר", "ultra-vires": "חריגה מסמכות", "warning-of-voidness": "התראת בטלות",
    "welfare-policy": "מדיניות רווחה",
}


def _tag_label_he(slug: str) -> str:
    """HE label for a theme tag; falls back to a humanized slug (mirrors the
    tag_label() fallback in app.js)."""
    if slug in TAG_LABELS_HE:
        return TAG_LABELS_HE[slug]
    humanized = str(slug).replace("-", " ").replace("_", " ")
    return re.sub(r'\b\w', lambda m: m.group(0).upper(), humanized)


def _tag_label_lint(rulings: list) -> None:
    """Warn-only: theme tags used in the corpus with no Hebrew label. Never
    fails the build — the humanized slug is shown meanwhile."""
    used = {tg for r in rulings for tg in (r.get("tags") or [])}
    missing = sorted(t for t in used if t not in TAG_LABELS_HE)
    if not missing:
        print("✓ tag labels: every corpus tag has a Hebrew label")
        return
    print(f"⚠ tag labels: {len(missing)} tag(s) without a TAG_LABELS_HE entry "
          f"(showing humanized slug)")
    for t in missing:
        print(f"    - {t}")


def prerender_home(rulings: list, corpus: dict) -> str:
    """Static Hebrew body for index.html: hero, headline stat, stat band,
    scale notes, methodology note and the full rulings table (no curve, no
    filter bar — the SPA re-renders those on top once JS runs)."""
    L = [_spa_toggle(_static_header("rulings"), "index.html")]
    L.append('<main class="home">')

    L.append('<div class="home-hero">')
    L.append('<h1>בקשי&amp;ביטון</h1>')
    L.append('<p class="home-tagline">פסיקות בית המשפט העליון בעניין החלטות ממשלה ומינויים</p>')
    L.append('</div>')

    # Headline stat — same guard as the JS: only when the library figures exist.
    if corpus and corpus.get("library_total") is not None \
            and corpus.get("library_interpretive_gutted") is not None:
        L.append('<div class="home-headline">')
        L.append(
            '<p class="home-headline-text">'
            f'<strong class="home-headline-num">{_esc(corpus["library_total"])}</strong>'
            f' חוקי כנסת שביטל או רוקן בית המשפט העליון מאז {_esc(corpus.get("year_min"))} — '
            f'<strong class="home-headline-num">{_esc(corpus["library_interpretive_gutted"])}</strong>'
            ' מהם בלי שבוטלו רשמית אף פעם.'
            '<a href="reading-quiet-veto.html">המאגר המלא ←</a>'
            '</p>')
        L.append('</div>')

    # Stat band — final numbers (the SPA animates them; static shows the result).
    struck = {"struck_down", "partially_struck"}
    years = [int((r.get("ruling_date") or "")[:4]) for r in rulings if (r.get("ruling_date") or "")[:4].isdigit()]
    if corpus:
        tiles = [
            (str(corpus.get("total_cases")), "מקרים מתועדים", False),
            (str(corpus.get("neutralized_total")), "חוקים שבוטלו או רוקנו", True),
            (f'{corpus.get("year_min")}–{corpus.get("year_max")}', "שנות תיעוד", False),
            (str(corpus.get("library_hollowed")), "רוקנו בפרשנות — בשקט", False),
        ]
    else:
        tiles = [
            (str(len(rulings)), "פסיקות במאגר", False),
            (str(sum(1 for r in rulings if r.get("outcome") in struck)), "בוטלו (מלא/חלקי)", True),
            (f'{min(years)}–{max(years)}' if years else "—", "שנות תיעוד", False),
            (str(sum(1 for r in rulings if len(r.get("panel") or []) >= 9)), "הרכבים מורחבים (9+)", False),
        ]
    L.append('<div class="stat-band">')
    for num, label, accent in tiles:
        cls = "stat-tile stat-tile--accent" if accent else "stat-tile"
        L.append(f'<div class="{cls}"><div class="stat-num">{_esc(num)}</div>'
                 f'<div class="stat-label">{_esc(label)}</div></div>')
    L.append('</div>')

    # Scale note — the deep case files are only the core; point at the rest.
    if corpus:
        L.append(
            '<p class="home-scale-note">'
            f'{_esc(corpus.get("rulings_total"))} התיקים המלאים שלמטה הם רק הליבה. '
            '<a href="reading-quiet-veto.html">'
            f'המאגר המלא: {_esc(corpus.get("total_cases"))} מקרים מתועדים ←</a>'
            ' כל אחד מהם — חוק או החלטה של נבחרי הציבור שבית המשפט ביטל או רוקן מתוכן.'
            '</p>')
    L.append(
        '<p class="home-scale-note">חדש — '
        '<a href="reading-where-the-line.html">היכן הימין מסמן את הקו: '
        'אמירות מיוחסות בנוגע לאי-הציות של הממשלה</a></p>')

    L.append('<p class="home-method">השכבה התיעודית של הפרויקט מתעדת עובדות הליכיות בלבד מתוך '
             'פרסומי בית המשפט העליון. שכבת התוכן המידעי (קריאה) מציעה חומר פרשני בסקירת מתאמים, '
             'עם סעיפי \'הוגנות אדברסרית\' בכל פריט.</p>')

    # Rulings table — every row links to its prerendered ruling page.
    L.append('<div class="table-scroll">')
    L.append('<table class="rulings-table">')
    L.append('<thead><tr>'
             '<th>תאריך</th>'
             '<th>תיק</th>'
             '<th>תוצאה</th>'
             '<th class="col-num">תוצאת הצבעה</th>'
             '<th class="col-soft">עילה</th>'
             '<th class="col-soft">עותר</th>'
             '</tr></thead>')
    L.append('<tbody>')
    for r in sorted(rulings, key=lambda x: x.get("ruling_date") or "", reverse=True):
        outcome = r.get("outcome") or ""
        vote = (f'{r.get("vote_majority")}–{r.get("vote_minority") or 0}'
                if r.get("vote_majority") is not None else "—")
        doctrines = ", ".join(DOCTRINE_LABELS_HE.get(d, d)
                              for d in (r.get("doctrine_invoked") or []))
        L.append(
            '<tr class="rrow">'
            f'<td class="col-date">{_esc(r.get("ruling_date"))}</td>'
            f'<td><a href="ruling-{_esc(r.get("case_id_slug"))}.html" class="rrow-case">{_esc(r.get("case_id"))}</a>'
            f'<div class="rrow-name">{_esc(r.get("case_name_he"))}</div></td>'
            f'<td><span class="outcome-pill outcome-{_esc(outcome)}">'
            f'{_esc(OUTCOME_LABELS_HE.get(outcome, outcome))}</span></td>'
            f'<td class="col-num vote"><bdi dir="ltr">{_esc(vote)}</bdi></td>'
            f'<td class="col-soft">{_esc(doctrines)}</td>'
            f'<td class="col-soft">{_esc(r.get("petitioner_name_he"))}</td>'
            '</tr>')
    L.append('</tbody>')
    L.append('</table>')
    L.append('</div>')

    L.append('</main>')
    L.append(_STATIC_FOOTER)
    return _satirize_mqg("\n".join(L))


_READING_BADGE_HE = {"essays": "מאמר", "explainers": "הסבר", "patterns": "תיעוד דפוס"}


def prerender_reading(content: dict) -> str:
    """Static Hebrew body for reading.html: hero, featured comic card and the
    card grid. Cards link to the prerendered reading-*.html pages (deliberate:
    it de-orphans them for crawlers); the SPA swaps in its own hrefs."""
    L = [_spa_toggle(_static_header("reading"), "reading.html")]
    L.append('<main class="reading-page">')

    L.append('<header class="reading-hero">')
    L.append('<h1 class="reading-hero-title">קריאה</h1>')
    L.append('<p class="reading-hero-intro">מאמרים, הסברים ומסמכי דפוסים. השכבה המידעית של הפרויקט: '
             'חומרים שמחברים את הפסיקות בליבה התיעודית לתמונה הגדולה. כל פריט נסקר על-ידי מתאמים '
             'וכולל סעיף \'הוגנות אדברסרית\' המביא את העמדה הנגדית בכתבי בעליה שלה.</p>')
    L.append('</header>')

    # Featured visual story — above-the-fold entry point (HE branch).
    L.append('<a class="featured-card" href="comic-6821-93.html">')
    L.append('<div class="featured-card-art">'
             '<img src="assets/comics/mizrahi-arc/page-he.png" '
             'alt="סיפור מצויר: פרדוקס מקור הסמכות" class="featured-card-img" '
             'style="object-position:top" loading="lazy"></div>')
    L.append('<div class="featured-card-text">')
    L.append('<span class="featured-card-eyebrow">סיפור מצויר · חדש</span>')
    L.append('<h2 class="featured-card-title">פרדוקס מקור הסמכות</h2>')
    L.append('<p class="featured-card-body">סיפור מצויר ב-12 לוחות: כיצד סכסוך חוב קטן בקיבוץ הפך '
             'לכלי שבאמצעותו שאב בית משפט בלתי-נבחר את סמכותו מתוך חוקי-היסוד של הכנסת עצמה — '
             'ולאחר מכן השתמש באותה סמכות כדי לחסן את עצמו מפני ניסיון הכנסת היחיד לרסן אותה. '
             'גרסה ידידותית, מצוירת, של מאמר היסוד של הפרויקט.</p>')
    L.append('<span class="featured-card-cta">התחל לקרוא →</span>')
    L.append('</div>')
    L.append('</a>')

    L.append('<div class="reading-grid">')
    for cat in ("essays", "explainers", "patterns"):  # "structure" is deliberately skipped
        for item in (content.get(cat) or []):
            slug = item.get("slug") or ""
            title = item.get("title_he") or item.get("title") or slug
            summary = item.get("summary_he") or item.get("summary") or ""
            minutes = item.get("reading_minutes_he") or item.get("reading_minutes")
            L.append(f'<a class="reading-card reading-card--{_esc(cat)}" href="reading-{_esc(slug)}.html">')
            L.append(f'<span class="card-badge card-badge--{_esc(cat)}">'
                     f'<span>{_esc(_READING_BADGE_HE.get(cat, cat))}</span></span>')
            L.append(f'<h3 class="card-title" dir="auto">{_esc(title)}</h3>')
            if summary:
                L.append(f'<p class="card-summary" dir="auto">{_esc(summary)}</p>')
            meta = []
            if minutes:
                meta.append(f'<span>{_esc(minutes)} דק׳ קריאה</span>')
            if item.get("date"):
                if meta:
                    meta.append('<span class="card-meta-sep">·</span>')
                meta.append(f'<span>{_esc(item.get("date"))}</span>')
            if meta:
                L.append('<div class="card-meta">' + "".join(meta) + '</div>')
            L.append('</a>')
    L.append('</div>')

    L.append('</main>')
    L.append(_STATIC_FOOTER)
    return _satirize_mqg("\n".join(L))


def prerender_tags(rulings: list) -> str:
    """Static Hebrew body for tags.html: every theme tag with its rulings
    listed (the SPA replaces this with the interactive cloud + browser).
    Mirrors the list markup of renderTagBrowser() in app.js."""
    L = [_spa_toggle(_static_header("tags"), "tags.html")]
    L.append('<main class="tags-page">')
    L.append('<h1>נושאים — עיון לפי תחום</h1>')
    L.append('<p class="tags-intro">כל פסיקה במאגר מתויגת לפי הנושאים המשפטיים והמדיניותיים שבהם '
             'היא נוגעת. בחרו נושא כדי לראות את הפסיקות המקושרות אליו — גודל התגית משקף את מספר '
             'הפסיקות.</p>')

    by_tag: dict = {}
    for r in rulings:
        for tg in (r.get("tags") or []):
            by_tag.setdefault(tg, []).append(r)
    for slug, rs in sorted(by_tag.items(), key=lambda kv: (-len(kv[1]), _tag_label_he(kv[0]))):
        L.append(f'<section class="tag-results" id="tag-{_esc(slug)}">')
        L.append('<div class="tag-results-head">'
                 f'<span class="tag-results-title">{_esc(_tag_label_he(slug))}</span>'
                 f'<span class="tag-results-count">{len(rs)} פסיקות</span></div>')
        L.append('<ul class="tag-result-list">')
        for r in sorted(rs, key=lambda x: x.get("ruling_date") or "", reverse=True):
            outcome = r.get("outcome") or ""
            L.append(
                '<li>'
                f'<a href="ruling-{_esc(r.get("case_id_slug"))}.html">'
                f'<span class="trl-case">{_esc(r.get("case_id"))}</span>'
                f'<span class="trl-name">{_esc(r.get("case_name_he"))}</span></a>'
                f'<span class="outcome-pill outcome-{_esc(outcome)}">'
                f'{_esc(OUTCOME_LABELS_HE.get(outcome, outcome))}</span>'
                '</li>')
        L.append('</ul>')
        L.append('</section>')

    L.append('</main>')
    L.append(_STATIC_FOOTER)
    return _satirize_mqg("\n".join(L))


def prerender_shells(site_dir: Path, rulings: list, content: dict, corpus: dict) -> int:
    """Inject the generated Hebrew blocks into the four hub shells. Idempotent:
    the markers stay put and only the space between them is rewritten."""
    _tag_label_lint(rulings)
    jobs = {
        "index.html": {"MAIN": prerender_home(rulings, corpus)},
        "reading.html": {"MAIN": prerender_reading(content)},
        "tags.html": {"MAIN": prerender_tags(rulings)},
        "about.html": {"HEADER": _spa_toggle(_static_header("about"), "about.html"),
                       "FOOTER": _STATIC_FOOTER},
    }
    n = 0
    for fname, blocks in jobs.items():
        path = site_dir / fname
        text = path.read_text(encoding="utf-8")
        new = text
        for name, block in blocks.items():
            new = _inject_block(new, name, block, fname)
        if new != text:
            path.write_text(new, encoding="utf-8")
        n += 1
    return n


def build_sitemap(site_dir: Path, rulings: list, content: dict, justices: list) -> Path:
    urls = ["", "index.html", "reading.html", "justices.html", "tags.html", "timeline.html", "cite.html",
            "about.html", "comic-6821-93.html"]
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


# Bilingual lint (warn-only): catch voice/summary edits that touch one language
# but not its pair, or drop a paired field. Guards the editorial-voice pass so
# he/en stay in sync. Reports drift; never fails the build.
_LINT_PAIRS = [
    ("summary_he", "summary_en"),
    ("why_matters_he", "why_matters_en"),
    ("case_name_he", "case_name_en"),
    ("petitioner_name_he", "petitioner_name_en"),
    ("respondent_decision_he", "respondent_decision_en"),
    ("notes_he", "notes"),
    ("defiance_signals_he", "defiance_signals"),
    ("predicate_ag_opinion_he", "predicate_ag_opinion"),
    ("respondent_body_he", "respondent_body"),
]


def _bilingual_lint(rulings: list) -> None:
    def filled(v):
        return isinstance(v, str) and v.strip() != ""
    unpaired, divergent = [], []
    for r in rulings:
        slug = r.get("case_id_slug", "?")
        for he, en in _LINT_PAIRS:
            a, b = filled(r.get(he)), filled(r.get(en))
            if a != b:
                have, miss = (he, en) if a else (en, he)
                unpaired.append(f"{slug}: {have} present but {miss} empty")
        sh, se = r.get("summary_he") or "", r.get("summary_en") or ""
        if filled(sh) and filled(se):
            ratio = len(sh) / max(1, len(se))
            if ratio > 2.5 or ratio < 0.4:
                divergent.append(f"{slug}: summary he/en length ratio {ratio:.2f} (possible voice drift)")
    if not unpaired and not divergent:
        print("✓ bilingual lint: all he/en pairs in sync")
        return
    print(f"⚠ bilingual lint: {len(unpaired)} unpaired field(s), {len(divergent)} length-divergent summary(ies)")
    for m in unpaired + divergent:
        print(f"    - {m}")


def build_corpus_stats(out_dir: Path, rulings: list) -> dict:
    """Aggregate the FULL documentary footprint — the in-depth rulings PLUS the
    Quiet-Veto library — into _data/corpus_stats.json so the homepage hero
    reflects the true scale, not just the 22-row rulings table. The 22 rulings
    are deep case files; the library catalogues every law the Court struck OR
    quietly hollowed out. Dedup by core docket so a case documented in both
    tracks is never double-counted."""
    def core(s):
        if not s:
            return None
        m = re.search(r"(\d{3,6}/\d{2,4})", str(s))
        return m.group(1) if m else None

    def year_of(*vals):
        for v in vals:
            if not v:
                continue
            m = re.search(r"(\d{4})", str(v))
            if m:
                return int(m.group(1))
        return None

    struck = {"struck_down", "partially_struck"}
    r_struck = [r for r in rulings if r.get("outcome") in struck]
    r_dockets = {core(r.get("case_id")) for r in rulings} - {None}
    years = [year_of(r.get("ruling_date")) for r in rulings]

    lib = []
    if LIBRARY_FILE.exists():
        raw = json.loads(LIBRARY_FILE.read_text(encoding="utf-8"))
        lib = raw if isinstance(raw, list) else raw.get("cases", [])

    def act(x):
        return (x.get("action") or x.get("category") or "").lower()

    # "dismissed" = the Court DECLINED to touch the law (honest counter-evidence);
    # everything else neutralised a law — by striking it or emptying it of content.
    l_dismissed = [x for x in lib if "dismiss" in act(x)]
    l_neutralized = [x for x in lib if "dismiss" not in act(x)]
    l_struck = [x for x in lib if "struck" in act(x)]
    l_hollowed = [x for x in l_neutralized if "struck" not in act(x)]
    # Precise "gutted via interpretation, never formally repealed" count — the
    # project's signature soundbite. Distinct from l_hollowed above (which is
    # the looser "not dismissed and no 'struck' in the action string" bucket,
    # e.g. also catches warning_of_voidness cases that touched nothing yet):
    # this reads the case's own interpretive_evisceration flag directly, the
    # same definition already used in the prose intro's stated count and
    # verified in the quiet-veto table's outcome classifier.
    l_interpretive_gutted = [x for x in lib if x.get("interpretive_evisceration") is True]
    l_dockets = {core(x.get("docket") or x.get("case_id") or x.get("case"))
                 for x in lib} - {None}
    years += [year_of(x.get("date"), x.get("year")) for x in lib]

    overlap = r_dockets & l_dockets
    years = [y for y in years if y]
    stats = {
        "rulings_total": len(rulings),
        "rulings_struck": len(r_struck),
        "library_total": len(lib),
        "library_struck": len(l_struck),
        "library_hollowed": len(l_hollowed),
        "library_interpretive_gutted": len(l_interpretive_gutted),
        "library_neutralized": len(l_neutralized),
        "library_dismissed": len(l_dismissed),
        "total_cases": len(rulings) + len(lib) - len(overlap),
        "neutralized_total": len(r_struck) + len(l_neutralized) - len(overlap),
        "overlap": len(overlap),
        "year_min": min(years) if years else None,
        "year_max": max(years) if years else None,
    }
    (out_dir / "corpus_stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    return stats


def build_curve_events(out_dir: Path) -> int:
    """Emit _data/curve_events.json — the Quiet-Veto (reading-down) library
    cases as light SECONDARY dots for the homepage curve. These do NOT feed
    the cumulative line (that stays driven only by the coded rulings, so the
    curve's logic is unchanged); they only add real, dated point events so the
    graph reflects the fuller ~70-event footprint. Revert = drop this file."""
    if not LIBRARY_FILE.exists():
        return 0
    raw = json.loads(LIBRARY_FILE.read_text(encoding="utf-8"))
    cases = raw if isinstance(raw, list) else raw.get("cases", [])
    out = []
    for c in cases:
        when = c.get("date") or c.get("year")
        if not when:
            continue
        act = (c.get("action") or "").lower()
        out.append({
            "when": str(when),
            "docket": c.get("docket_core") or c.get("docket") or "",
            "name": c.get("name") or "",
            "kind": "struck" if "struck" in act else "read_down",
        })
    (out_dir / "curve_events.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(out)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rulings = build_rulings(OUT_DIR)
    print(f"✓ wrote {OUT_DIR/'rulings.json'} ({len(rulings)} rulings)")
    _bilingual_lint(rulings)

    cs = build_corpus_stats(OUT_DIR, rulings)
    print(f"✓ wrote {OUT_DIR/'corpus_stats.json'} "
          f"({cs['total_cases']} documented cases, {cs['neutralized_total']} "
          f"struck/hollowed, {cs['year_min']}–{cs['year_max']})")

    ne = build_curve_events(OUT_DIR)
    print(f"✓ wrote {OUT_DIR/'curve_events.json'} ({ne} library event dots)")

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

    kit = build_kits(SITE_DIR, rulings)
    print(f"✓ wrote ruling-day kits for {kit['rulings']} rulings "
          f"({kit['cards']} cards, {kit['posts']} post files) → "
          f"{KITS_DIR.relative_to(REPO_ROOT)}/")
    if kit["gaps"]:
        print(f"  ⚠ {len(kit['gaps'])} ruling(s) with fields the record does "
              f"not carry (rendered as “—”):")
        for slug, fields in kit["gaps"]:
            print(f"    · {slug}: {', '.join(fields)}")
    else:
        print("  · no missing card fields")

    n_static = build_static_pages(SITE_DIR, rulings, content_out)
    print(f"✓ wrote {n_static} prerendered static pages (ruling-*.html, reading-*.html)")

    n_pre = prerender_shells(SITE_DIR, rulings, content_out, cs)
    print(f"✓ injected prerendered content into {n_pre} shell pages")

    sitemap_path = build_sitemap(SITE_DIR, rulings, content_out, justices_list)
    print(f"✓ wrote {sitemap_path}")

    robots_path = build_robots(SITE_DIR)
    print(f"✓ wrote {robots_path}")

    vinfo = version_assets(SITE_DIR)
    print(f"✓ cache-busted assets {vinfo['versions']} on {vinfo['pages_stamped']} pages")

    return 0


if __name__ == "__main__":
    # `--kit-only` regenerates just site/assets/kits/ (fast iteration on the
    # cards); the plain build always runs the kit step too.
    if "--kit-only" in sys.argv[1:]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        _rulings = build_rulings(OUT_DIR)
        _kit = build_kits(SITE_DIR, _rulings)
        print(f"✓ wrote ruling-day kits for {_kit['rulings']} rulings "
              f"({_kit['cards']} cards, {_kit['posts']} post files)")
        for _slug, _fields in _kit["gaps"]:
            print(f"    · {_slug}: {', '.join(_fields)}")
        sys.exit(0)
    sys.exit(main())
