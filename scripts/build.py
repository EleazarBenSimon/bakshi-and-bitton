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
LIBRARY_FILE = REPO_ROOT / "data" / "library" / "quiet-veto-cases.json"
STATEMENTS_FILE = REPO_ROOT / "data" / "library" / "statements.json"
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
        f'<title>{_esc(title_he)} · בקשי&amp;ביטון</title>',
        f'<meta name="description" content="{_esc(desc)}">',
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
        stats.append(f'<span class="rh-stat">הצבעה <b>{_esc(r.get("vote_majority"))}–{_esc(r.get("vote_minority") or 0)}</b></span>')
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
        row("הצבעה", f'{_esc(r.get("vote_majority"))}–{_esc(r.get("vote_minority") or 0)}', rec=True)
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
    body = body.replace('class="lang-toggle"', f'class="lang-toggle" data-spa="{_esc(spa_url)}"')
    body = _satirize_mqg(body)
    return head + '\n<body>\n' + body + '\n</body>\n</html>\n'


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
        f'<div id="root">{_static_header("reading")}<main>'
        f'<p class="breadcrumb"><a href="reading.html">קריאה</a> / {_esc(badge)}</p>'
        f'{inner}</main>{_STATIC_FOOTER}</div>'
    )
    body = body.replace('class="lang-toggle"', f'class="lang-toggle" data-spa="{_esc(spa_url)}"')
    body = _satirize_mqg(body)
    # Load the shared script so client-side enhancements work on these
    # otherwise-static pages (the Quiet-Veto "contribute" modal); plus a
    # small self-contained script for the content-map (mobile toggle +
    # scroll-spy). Neither re-renders the already-baked content.
    toc_script = _TOC_SCRIPT if toc_html else ""
    return (head + '\n<body>\n' + body
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
