// Bakshi&Bitton — V0 client-side rendering
// Loads JSON data and renders pages. No framework, no build step.

const i18n = {
  he: {
    site_title: "בקשי וביטון",
    site_subtitle: "פסיקות בית המשפט העליון בעניין החלטות ממשלה ומינויים",
    nav_rulings: "פסיקות",
    nav_reading: "קריאה",
    nav_justices: "שופטים",
    nav_cite: "ציטוט והפצה",
    nav_about: "אודות",
    nav_methodology: "מתודולוגיה",
    reading_title: "קריאה",
    reading_intro: "מאמרים, הסברים ומסמכי דפוסים. השכבה המידעית של הפרויקט: חומרים שמחברים את הפסיקות בליבה התיעודית לתמונה הגדולה. כל פריט נסקר על-ידי מתאמים וכולל סעיף 'הוגנות אדברסרית' המביא את העמדה הנגדית בכתבי בעליה שלה.",
    cat_essays: "מאמרים",
    cat_essays_desc: "ניתוחים נושאיים שמחברים מספר פסיקות לקשת אחת.",
    cat_explainers: "הסברים מקצרים",
    cat_explainers_desc: "מבואות תמציתיים לעילות, מוסדות ומונחים מרכזיים.",
    cat_patterns: "תיעוד דפוסים",
    cat_patterns_desc: "ניתוח דפוסים אמפיריים על-פני הליבה התיעודית.",
    content_no_slug: "לא צוין מאמר. חזרה לעמוד הקריאה.",
    content_not_found: "המאמר לא נמצא",
    content_not_found_detail: "ייתכן שהקישור שגוי או שהמאמר טרם פורסם.",
    col_date: "תאריך",
    col_case: "תיק",
    col_outcome: "תוצאה",
    col_vote: "תוצאת הצבעה",
    col_doctrine: "עילה",
    col_panel: "הרכב",
    col_petitioner: "עותר",
    col_authored_majority: "חיבר דעת רוב",
    col_authored_minority: "חיבר דעת מיעוט",
    col_role: "תפקיד",
    col_appearances: "הופעות",
    label_panel: "הרכב",
    label_petitioner: "עותר",
    label_petitioner_type: "סוג עותר",
    label_respondent: "משיב",
    label_respondent_decision: "ההחלטה המעורערת",
    label_doctrine_invoked: "עילות שנטענו",
    label_outcome: "תוצאה",
    label_vote: "הצבעה",
    label_majority_authors: "מחברי דעת הרוב",
    label_minority_authors: "מחברי דעת המיעוט",
    label_official_url: "פסק הדין הרשמי",
    label_secondary_sources: "מקורות משניים",
    label_summary: "תקציר",
    label_predicate_ag: "חוות-דעת היועמ\"ש שקדמה",
    label_respondent_body: "גוף נושא ההחלטה",
    label_compliance: "מצב יישום",
    label_defiance: "סימני התנגדות",
    label_tags: "תיוגים",
    label_notes: "הערות",
    label_filing_date: "תאריך הגשה",
    label_ruling_date: "תאריך הפסיקה",
    filter_all: "הכל",
    filter_outcome: "סנן לפי תוצאה",
    filter_doctrine: "סנן לפי עילה",
    filter_year: "סנן לפי שנה",
    search_placeholder: "חיפוש בתקצירים…",
    no_rulings: "אין פסיקות שעונות על הסינון",
    rulings_count: (n) => `${n} פסיקות`,
    methodology_notice: "השכבה התיעודית של הפרויקט מתעדת עובדות הליכיות בלבד מתוך פרסומי בית המשפט העליון. שכבת התוכן המידעי (קריאה) מציעה חומר פרשני בסקירת מתאמים, עם סעיפי 'הוגנות אדברסרית' בכל פריט.",
    role_President: "נשיא",
    role_AP: "ממלא מקום נשיא",
    role_DP: "משנה לנשיא",
    role_Justice: "שופט/ת",
    role_RJ: "שופט/ת בדימוס (בחלון סטטוטורי)",
    curve_title: "העקומה: 1976–2026",
    curve_subtitle: "העקומה האדומה מצטברת: היא עולה ב-1 בכל פעם שבית המשפט העליון התערב במהותו של תיק נגד רשות נבחרת — בין אם הביטול היה פורמלי ('התערבות') ובין אם היה הליכי ('מעורבות'). הציר האנכי שמשמאל מציין את חריפות הפסיקה הבודדת; הציר שמימין — את הסך המצטבר של מקרי המעורבות עד אותה שנה. לחיצה על נקודה פותחת את הפסיקה.",
    curve_caption: "מה רואים: נורמליזציה הדרגתית של התערבות שיפוטית בתחומים שמעולם לא הוסמכה על-ידי הציבור או הכנסת. כמעט שטוחה לאורך 30 שנה, מתחילה לטפס לאחר 2006, ומאיצה אנכית ב-2021–2026. השכבה השנייה ('קריאה') תדון בפרשנות.",
    cum_axis_label: "סך מצטבר",
    curve_aria: "תרשים פיזור של פסיקות בית המשפט העליון לפי שנה ועוצמת התערבות, 1976–2026",
    sev_1: "דחיית עתירה",
    sev_2: "הצהרתי / מצומצם",
    sev_3: "השבה לדיון",
    sev_4: "ביטול חלקי / צו עשה",
    sev_5: "ביטול חוק או החלטה",
    era_1: "תקופת היסוד",
    era_2: "גל ראשון של פסילות",
    era_3: "תקופת העקיפה החוקתית",
    zoom_all: "תצוגה מלאה",
    zoom_hint: "מעבר בין תקופות לתצוגה מפורטת:",
    ann_dakka: "1976 · המצאת עילת הסבירות",
    ann_mizrahi: "1995 · הטענה לסמכות פסילת חוק-יסוד",
    ann_adalah: "2006 · פסילת חוק ראשונה לאחר מזרחי",
    ann_shafir: "2021 · התראת-בטלות ראשונה",
    ann_5658: "2024 · פסילת תיקון לחוק-יסוד",
    ann_gofman: "2026 · צו להחזיר מינוי במוסד",
  },
  en: {
    site_title: "Bakshi&Bitton",
    site_subtitle: "Israeli Supreme Court rulings on government decisions and appointments",
    nav_rulings: "Rulings",
    nav_reading: "Reading",
    nav_justices: "Justices",
    nav_cite: "Cite & Share",
    nav_about: "About",
    nav_methodology: "Methodology",
    reading_title: "Reading",
    reading_intro: "Essays, explainers, and pattern documents. The project's informative layer: material that connects the rulings in the documentary core into the larger picture. Every piece is moderator-reviewed and includes an 'adversarial fairness' section presenting the opposing position in its own proponents' words.",
    cat_essays: "Essays",
    cat_essays_desc: "Thematic analyses connecting multiple rulings into a single arc.",
    cat_explainers: "Explainers",
    cat_explainers_desc: "Concise introductions to key doctrines, institutions, and terms.",
    cat_patterns: "Pattern documents",
    cat_patterns_desc: "Empirical analysis of patterns across the documentary core.",
    content_no_slug: "No article specified. Return to the reading page.",
    content_not_found: "Article not found",
    content_not_found_detail: "The link may be wrong, or the article may not yet be published.",
    col_date: "Date",
    col_case: "Case",
    col_outcome: "Outcome",
    col_vote: "Vote",
    col_doctrine: "Doctrine",
    col_panel: "Panel",
    col_petitioner: "Petitioner",
    col_authored_majority: "Majority authored",
    col_authored_minority: "Minority authored",
    col_role: "Role",
    col_appearances: "Appearances",
    label_panel: "Panel",
    label_petitioner: "Petitioner",
    label_petitioner_type: "Petitioner type",
    label_respondent: "Respondent",
    label_respondent_decision: "Decision challenged",
    label_doctrine_invoked: "Doctrine invoked",
    label_outcome: "Outcome",
    label_vote: "Vote",
    label_majority_authors: "Majority opinion authors",
    label_minority_authors: "Dissent opinion authors",
    label_official_url: "Official ruling",
    label_secondary_sources: "Secondary sources",
    label_summary: "Summary",
    label_predicate_ag: "Predicate AG opinion",
    label_respondent_body: "Decision-making body",
    label_compliance: "Compliance status",
    label_defiance: "Defiance signals",
    label_tags: "Tags",
    label_notes: "Notes",
    label_filing_date: "Filing date",
    label_ruling_date: "Ruling date",
    filter_all: "All",
    filter_outcome: "Filter by outcome",
    filter_doctrine: "Filter by doctrine",
    filter_year: "Filter by year",
    search_placeholder: "Search summaries…",
    no_rulings: "No rulings match the filter",
    rulings_count: (n) => `${n} rulings`,
    methodology_notice: "The project's documentary layer records only procedural facts from public Israeli Supreme Court records. The informative content layer (Reading) provides interpretive material under moderator review, with an 'adversarial fairness' section in every piece.",
    role_President: "President",
    role_AP: "Acting President",
    role_DP: "Deputy President",
    role_Justice: "Justice",
    role_RJ: "Retired Justice (statutory post-retirement window)",
    curve_title: "The curve: 1976–2026",
    curve_subtitle: "The red curve is cumulative: it climbs by +1 every time the Court substantively engaged with an elected-branch matter — whether the override was formal ('intervention') or procedural ('involvement'). The left axis marks individual-ruling severity; the right axis traces the running total of judicial engagement reaching into elected-branch territory. Click any dot to open the ruling.",
    curve_caption: "What you see: the gradual normalization of judicial intervention in domains the public and Knesset never authorized. Almost flat for 30 years, beginning to climb after 2006, near-vertical 2021–2026. The site's second layer ('Reading') discusses interpretation.",
    cum_axis_label: "Cumulative",
    curve_aria: "Scatter plot of Israeli Supreme Court rulings by year and intervention severity, 1976–2026",
    sev_1: "Petition dismissed",
    sev_2: "Declarative / restricted",
    sev_3: "Remanded",
    sev_4: "Partial strike / mandatory / warning",
    sev_5: "Statute or decision struck",
    era_1: "Foundational doctrine",
    era_2: "First wave of strikes",
    era_3: "Constitutional override era",
    zoom_all: "Full view",
    zoom_hint: "Zoom into a specific era for detail:",
    ann_dakka: "1976 · Reasonableness invented",
    ann_mizrahi: "1995 · Claim to strike Basic Laws",
    ann_adalah: "2006 · First post-Mizrahi statute strike",
    ann_shafir: "2021 · First warning of voidness",
    ann_5658: "2024 · Basic Law amendment struck",
    ann_gofman: "2026 · PM ordered to remand Mossad appointment",
  },
};

function getLang() {
  const stored = localStorage.getItem("bakshi-and-bitton-lang");
  if (stored === "he" || stored === "en") return stored;
  return "he";
}

function setLang(lang) {
  localStorage.setItem("bakshi-and-bitton-lang", lang);
  document.documentElement.lang = lang;
  location.reload();
}

const lang = getLang();
const t = i18n[lang];

function el(tag, attrs = {}, ...children) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") e.className = v;
    else if (k === "html") e.innerHTML = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2).toLowerCase(), v);
    else e.setAttribute(k, v);
  }
  for (const child of children.flat()) {
    if (child == null) continue;
    e.append(typeof child === "string" ? document.createTextNode(child) : child);
  }
  return e;
}

function fetchJSON(path) {
  return fetch(path, { cache: "no-store" }).then((r) => {
    if (!r.ok) throw new Error(`Failed to load ${path}: ${r.status}`);
    return r.json();
  });
}

function ruling_name(r) {
  return lang === "he" ? r.case_name_he : r.case_name_en;
}
function justice_name(j) {
  return lang === "he" ? j.name_he : j.name_en;
}
function role_label(role) {
  const map = {
    "President": t.role_President,
    "Acting President": t.role_AP,
    "Deputy President": t.role_DP,
    "Justice": t.role_Justice,
    "Retired Justice": t.role_RJ,
  };
  return map[role] || role;
}

function renderHeader(active) {
  const header = el("header",
    {},
    el("div", { class: "header-inner" },
      el("div", {},
        el("a", { class: "logo", href: "index.html" }, t.site_title,
          el("span", { class: "logo-sub" }, t.site_subtitle)
        )
      ),
      el("nav", {},
        el("a", { href: "index.html", style: active === "rulings" ? "font-weight:600;color:var(--accent)" : "" }, t.nav_rulings),
        el("a", { href: "reading.html", style: active === "reading" ? "font-weight:600;color:var(--accent)" : "" }, t.nav_reading),
        el("a", { href: "justices.html", style: active === "justices" ? "font-weight:600;color:var(--accent)" : "" }, t.nav_justices),
        el("a", { href: "cite.html", style: active === "cite" ? "font-weight:600;color:var(--accent)" : "" }, t.nav_cite),
        el("a", { href: "about.html", style: active === "about" ? "font-weight:600;color:var(--accent)" : "" }, t.nav_about),
      ),
      el("button", { class: "lang-toggle", onClick: () => setLang(lang === "he" ? "en" : "he") }, lang === "he" ? "EN" : "עברית")
    )
  );
  return header;
}

function renderFooter() {
  return el("footer", {},
    "Bakshi&Bitton · ",
    el("a", { href: "https://github.com/EleazarBenSimon/bakshi-and-bitton" }, "github.com/EleazarBenSimon/bakshi-and-bitton"),
    " · MIT License · ",
    el("a", { href: "https://github.com/EleazarBenSimon/bakshi-and-bitton/blob/main/METHODOLOGY.md" }, t.nav_methodology)
  );
}

// ─── Intervention-severity curve (homepage hero) ─────────────────────
// SVG built inline; no external libraries. Each ruling is plotted as a
// dot at (ruling year, intervention severity); a stepped running-max
// "envelope" line shows the highest intervention severity reached up
// to that point in time. Inflection points are labeled. Dots link to
// the ruling page.

const SEVERITY_BY_OUTCOME = {
  struck_down: 5,
  partially_struck: 4,
  mandatory_order: 4,
  warning_of_voidness: 4,
  remanded: 3,
  restricted: 2,
  modified: 2,
  declarative: 2,
  dismissed: 1,
  upheld: 1,
};

const DOT_COLOR_BY_OUTCOME = {
  struck_down: "#b03a3a",
  partially_struck: "#b03a3a",
  mandatory_order: "#b03a3a",
  warning_of_voidness: "#b03a3a",
  remanded: "#c47d27",
  restricted: "#c47d27",
  modified: "#c47d27",
  declarative: "#5a7a9a",
  dismissed: "#4a7a4a",
  upheld: "#2a6a2a",
};

const CURVE_NS = "http://www.w3.org/2000/svg";

function curveSvgEl(tag, attrs = {}, ...children) {
  const e = document.createElementNS(CURVE_NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  for (const c of children.flat()) {
    if (c == null) continue;
    e.append(typeof c === "string" ? document.createTextNode(c) : c);
  }
  return e;
}

function curveYearDecimal(d) {
  const yr = parseInt(d.slice(0, 4), 10);
  const mo = parseInt(d.slice(5, 7), 10) || 1;
  return yr + (mo - 1) / 12;
}

function curveAnnotationsMap() {
  return {
    "156-75-dakka":                t.ann_dakka,
    "6821-93-bank-mizrahi":        t.ann_mizrahi,
    "8276-05-adalah-civil-wrongs": t.ann_adalah,
    "5969-20-shafir":              t.ann_shafir,
    "5658-23":                     t.ann_5658,
    "gofman-mossad-2026-05":       t.ann_gofman,
  };
}

function curveEras() {
  return [
    { start: 1975, end: 2005.5, label: t.era_1, fill: "rgba(90,122,154,0.05)",  stripe: "#5a7a9a" },
    { start: 2005.5, end: 2020.5, label: t.era_2, fill: "rgba(196,125,39,0.07)", stripe: "#c47d27" },
    { start: 2020.5, end: 2027, label: t.era_3, fill: "rgba(176,58,58,0.10)",   stripe: "#b03a3a" },
  ];
}

function renderCurve(rulings) {
  const NS = "http://www.w3.org/2000/svg";
  const W = 1040, H = 500;
  const M = { top: 88, right: 96, bottom: 80, left: 160 };
  const innerW = W - M.left - M.right;
  const innerH = H - M.top - M.bottom;
  const YR_MIN = 1975, YR_MAX = 2027;
  const SEV_AXIS_MAX = 5.6;

  function svgEl(tag, attrs = {}, ...children) {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    for (const c of children.flat()) {
      if (c == null) continue;
      e.append(typeof c === "string" ? document.createTextNode(c) : c);
    }
    return e;
  }
  function yearDecimal(d) {
    const yr = parseInt(d.slice(0, 4), 10);
    const mo = parseInt(d.slice(5, 7), 10) || 1;
    return yr + (mo - 1) / 12;
  }
  function xOf(yd) { return M.left + ((yd - YR_MIN) / (YR_MAX - YR_MIN)) * innerW; }
  function yOf(sev) { return M.top + innerH - (sev / SEV_AXIS_MAX) * innerH; }

  const points = rulings.map((r) => ({
    r,
    yd: yearDecimal(r.ruling_date),
    sev: SEVERITY_BY_OUTCOME[r.outcome] ?? 1,
  })).sort((a, b) => a.yd - b.yd);

  let envMax = 0;
  const envelope = points.map((p) => {
    envMax = Math.max(envMax, p.sev);
    return { yd: p.yd, sev: envMax };
  });

  const annotations = {
    "156-75-dakka":              { text: t.ann_dakka,   side: "below", align: "middle", dy: 8 },
    "6821-93-bank-mizrahi":      { text: t.ann_mizrahi, side: "above", align: "middle", dy: 0 },
    "8276-05-adalah-civil-wrongs": { text: t.ann_adalah, side: "below", align: "start",  dy: 6 },
    "5969-20-shafir":            { text: t.ann_shafir,  side: "below", align: "middle", dy: 16 },
    "5658-23":                   { text: t.ann_5658,    side: "above", align: "end",    dy: -10 },
    "gofman-mossad-2026-05":     { text: t.ann_gofman,  side: "below", align: "start",  dy: 18 },
  };

  const eras = [
    { start: 1975, end: 2005.5, label: t.era_1, fill: "rgba(90,122,154,0.05)",  stripe: "#5a7a9a" },
    { start: 2005.5, end: 2020.5, label: t.era_2, fill: "rgba(196,125,39,0.07)", stripe: "#c47d27" },
    { start: 2020.5, end: 2027, label: t.era_3, fill: "rgba(176,58,58,0.10)",   stripe: "#b03a3a" },
  ];

  const svg = svgEl("svg", {
    viewBox: `0 0 ${W} ${H}`,
    class: "curve",
    role: "img",
    "aria-label": t.curve_aria,
  });

  // ── defs: gradients & filters ────────────────────────────────────
  const defs = svgEl("defs");

  const envGrad = svgEl("linearGradient", { id: "envFill", x1: "0", y1: "0", x2: "0", y2: "1" });
  envGrad.append(svgEl("stop", { offset: "0%",  "stop-color": "#b03a3a", "stop-opacity": "0.28" }));
  envGrad.append(svgEl("stop", { offset: "100%", "stop-color": "#b03a3a", "stop-opacity": "0.02" }));
  defs.append(envGrad);

  const shadow = svgEl("filter", { id: "dotShadow", x: "-60%", y: "-60%", width: "220%", height: "220%" });
  shadow.append(svgEl("feGaussianBlur",  { in: "SourceAlpha", stdDeviation: "1.6" }));
  shadow.append(svgEl("feOffset",        { dx: "0", dy: "1.5", result: "off" }));
  shadow.append(svgEl("feComponentTransfer",
    {},
    svgEl("feFuncA", { type: "linear", slope: "0.4" })
  ));
  const sMerge = svgEl("feMerge");
  sMerge.append(svgEl("feMergeNode"));
  sMerge.append(svgEl("feMergeNode", { in: "SourceGraphic" }));
  shadow.append(sMerge);
  defs.append(shadow);

  const glow = svgEl("filter", { id: "dotGlow", x: "-80%", y: "-80%", width: "260%", height: "260%" });
  glow.append(svgEl("feGaussianBlur", { in: "SourceGraphic", stdDeviation: "3", result: "blur" }));
  const gMerge = svgEl("feMerge");
  gMerge.append(svgEl("feMergeNode", { in: "blur" }));
  gMerge.append(svgEl("feMergeNode", { in: "SourceGraphic" }));
  glow.append(gMerge);
  defs.append(glow);

  svg.append(defs);

  // ── era backgrounds + headers ────────────────────────────────────
  for (let i = 0; i < eras.length; i++) {
    const era = eras[i];
    const x1 = xOf(era.start);
    const x2 = xOf(era.end);
    svg.append(svgEl("rect", {
      x: x1, y: M.top, width: x2 - x1, height: innerH,
      fill: era.fill,
    }));
    svg.append(svgEl("rect", {
      x: x1 + 1, y: M.top - 26, width: x2 - x1 - 2, height: 4,
      fill: era.stripe, opacity: "0.7", rx: "2",
    }));
    svg.append(svgEl("text", {
      x: (x1 + x2) / 2, y: M.top - 34,
      "text-anchor": "middle",
      "font-size": "11.5", "font-weight": "700",
      "letter-spacing": "0.6",
      fill: era.stripe,
    }, era.label.toUpperCase()));
    if (i < eras.length - 1) {
      svg.append(svgEl("line", {
        x1: x2, x2: x2, y1: M.top - 18, y2: M.top + innerH,
        stroke: "#d0d0d0", "stroke-width": "1", "stroke-dasharray": "3 3",
      }));
    }
  }

  // ── severity gridlines + y-axis labels ───────────────────────────
  const sevLabels = [
    [1, t.sev_1], [2, t.sev_2], [3, t.sev_3], [4, t.sev_4], [5, t.sev_5],
  ];
  for (const [s, label] of sevLabels) {
    const y = yOf(s);
    svg.append(svgEl("line", {
      x1: M.left, x2: M.left + innerW, y1: y, y2: y,
      stroke: "#e8e8e8", "stroke-width": "1",
    }));
    svg.append(svgEl("text", {
      x: M.left - 10, y: y + 4,
      "text-anchor": "end",
      "font-size": "10.5", fill: "#666",
    }, label));
  }

  // ── decade gridlines + x-axis labels ─────────────────────────────
  const decadeYears = [1980, 1990, 2000, 2010, 2020, 2026];
  for (const yr of decadeYears) {
    const x = xOf(yr);
    svg.append(svgEl("line", {
      x1: x, x2: x, y1: M.top, y2: M.top + innerH,
      stroke: "#e8e8e8", "stroke-width": "1", "stroke-dasharray": "1 4",
    }));
    svg.append(svgEl("text", {
      x: x, y: M.top + innerH + 22,
      "text-anchor": "middle", "font-size": "12.5", "font-weight": "500", fill: "#555",
    }, String(yr)));
  }

  // axes
  svg.append(svgEl("line", {
    x1: M.left, x2: M.left + innerW, y1: M.top + innerH, y2: M.top + innerH,
    stroke: "#888", "stroke-width": "1.2",
  }));
  svg.append(svgEl("line", {
    x1: M.left, x2: M.left, y1: M.top, y2: M.top + innerH,
    stroke: "#888", "stroke-width": "1.2",
  }));

  // ── cumulative-engagement curve (smooth, monotonic) ──────────────
  // For each ruling, the curve climbs by +1 — capturing both formal
  // intervention (override) and involvement (process-insertion). The
  // y-axis on the RIGHT shows the cumulative engagement count; on the
  // LEFT it remains outcome severity for the dots. Two y-meanings, one
  // chart: dots tell the case-level story, curve tells the process story.
  const CUM_HEADROOM = 0.92;
  const cumTotal = points.length;
  function yCum(c) { return M.top + innerH - (c / Math.max(1, cumTotal)) * innerH * CUM_HEADROOM; }

  // Build (year, cumulative) sequence including a (YR_MIN, 0) anchor.
  const cumXY = [{ x: xOf(YR_MIN), y: yCum(0) }];
  let cum = 0;
  for (const p of points) {
    cum += 1;
    cumXY.push({ x: xOf(p.yd), y: yCum(cum) });
  }
  cumXY.push({ x: xOf(YR_MAX), y: yCum(cum) });

  // Catmull-Rom-to-Bezier path (tension 0.5) — smooth, passes through
  // every data point. Cumulative values are monotonic non-decreasing,
  // so the spline never dips backwards visually.
  function catmullRomPath(pts) {
    if (pts.length < 2) return "";
    let d = `M ${pts[0].x} ${pts[0].y}`;
    const t = 0.5;
    for (let i = 0; i < pts.length - 1; i++) {
      const p0 = pts[Math.max(0, i - 1)];
      const p1 = pts[i];
      const p2 = pts[i + 1];
      const p3 = pts[Math.min(pts.length - 1, i + 2)];
      const cp1x = p1.x + (p2.x - p0.x) * t / 6;
      const cp1y = Math.min(p1.y, Math.max(p2.y, p1.y + (p2.y - p0.y) * t / 6));
      const cp2x = p2.x - (p3.x - p1.x) * t / 6;
      const cp2y = Math.max(p2.y, Math.min(p1.y, p2.y - (p3.y - p1.y) * t / 6));
      d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`;
    }
    return d;
  }

  const curveLine = catmullRomPath(cumXY);
  const baselineY = yCum(0);
  const curveArea = curveLine + ` L ${cumXY[cumXY.length - 1].x} ${baselineY} L ${cumXY[0].x} ${baselineY} Z`;

  svg.append(svgEl("path", { d: curveArea, fill: "url(#envFill)" }));
  svg.append(svgEl("path", {
    d: curveLine, fill: "none",
    stroke: "#b03a3a", "stroke-width": "2.8",
    opacity: "0.92",
    "stroke-linecap": "round",
    "stroke-linejoin": "round",
  }));

  // ── right-side y-axis: cumulative engagement count ───────────────
  const rightAxisX = M.left + innerW;
  svg.append(svgEl("line", {
    x1: rightAxisX, x2: rightAxisX, y1: M.top, y2: M.top + innerH,
    stroke: "#b03a3a", "stroke-width": "1", opacity: "0.4",
  }));
  const cumTicks = cumTotal <= 25
    ? [0, 5, 10, 15, 20].filter((c) => c <= cumTotal)
    : [0, Math.round(cumTotal / 4), Math.round(cumTotal / 2), Math.round(3 * cumTotal / 4), cumTotal];
  for (const c of cumTicks) {
    const y = yCum(c);
    svg.append(svgEl("line", {
      x1: rightAxisX - 4, x2: rightAxisX + 4, y1: y, y2: y,
      stroke: "#b03a3a", "stroke-width": "1", opacity: "0.6",
    }));
    svg.append(svgEl("text", {
      x: rightAxisX + 8, y: y + 4,
      "text-anchor": "start", "font-size": "10.5",
      fill: "#7a2828", "font-weight": "600",
    }, String(c)));
  }
  svg.append(svgEl("text", {
    x: rightAxisX + 8, y: M.top - 12,
    "text-anchor": "start", "font-size": "10",
    fill: "#7a2828", "font-weight": "700",
    "letter-spacing": "0.3",
  }, t.cum_axis_label));

  // ── dots ─────────────────────────────────────────────────────────
  for (const p of points) {
    const x = xOf(p.yd), y = yOf(p.sev);
    const color = DOT_COLOR_BY_OUTCOME[p.r.outcome] || "#666";
    const radius = p.sev >= 4 ? 8 : (p.sev >= 3 ? 7 : 6);
    const a = svgEl("a", { href: `ruling.html?id=${p.r.case_id_slug}` });

    if (p.sev >= 4) {
      const halo = svgEl("circle", {
        cx: x, cy: y, r: String(radius + 5),
        fill: color, "fill-opacity": "0.18",
        filter: "url(#dotGlow)",
      });
      a.append(halo);
    }

    const circle = svgEl("circle", {
      cx: x, cy: y, r: String(radius),
      fill: color, "fill-opacity": "0.97",
      stroke: "#fff", "stroke-width": "2.2",
      filter: "url(#dotShadow)",
    });
    circle.append(svgEl("title", {}, `${p.r.ruling_date} · ${p.r.case_id} · ${p.r.outcome.replace(/_/g, " ")}`));
    a.append(circle);
    svg.append(a);
  }

  // ── annotation callouts (boxed, with leader lines) ───────────────
  // Each annotation is wrapped in a <g class="annotation" data-x="…">
  // so the zoom-bar handler can hide callouts whose anchor falls
  // outside the active viewBox (keeps zoomed eras visually clean).
  for (const p of points) {
    const ann = annotations[p.r.case_id_slug];
    if (!ann) continue;
    const x = xOf(p.yd), y = yOf(p.sev);
    const above = ann.side === "above";
    const radius = p.sev >= 4 ? 8 : (p.sev >= 3 ? 7 : 6);

    // estimate text box dimensions
    const text = ann.text;
    const charW = 6.8;
    const padX = 9, padY = 5;
    const boxW = Math.round(text.length * charW + padX * 2);
    const boxH = 22;

    let boxX;
    if (ann.align === "end")       boxX = x - boxW + 6;
    else if (ann.align === "start") boxX = x - 6;
    else                            boxX = x - boxW / 2;
    // clamp inside chart area so callouts never overflow
    const rightLimit = M.left + innerW - 2;
    const leftLimit  = M.left + 2;
    if (boxX + boxW > rightLimit) boxX = rightLimit - boxW;
    if (boxX < leftLimit) boxX = leftLimit;

    const baseBoxY = above ? y - 32 : y + 14;
    const boxY = baseBoxY + (ann.dy || 0);

    // leader line
    const leadFromY = above ? y - radius - 2 : y + radius + 2;
    const leadToY   = above ? boxY + boxH    : boxY;

    const annEra = p.yd < 2005.5 ? "era1" : (p.yd < 2020.5 ? "era2" : "era3");
    const g = svgEl("g", {
      class: "annotation",
      "data-x": String(Math.round(x)),
      "data-era": annEra,
    });
    g.append(svgEl("line", {
      x1: x, x2: x, y1: leadFromY, y2: leadToY,
      stroke: "#b03a3a", "stroke-width": "1.2", opacity: "0.7",
    }));
    g.append(svgEl("rect", {
      x: boxX, y: boxY, width: boxW, height: boxH,
      rx: "4", ry: "4",
      fill: "#ffffff",
      stroke: "#b03a3a", "stroke-width": "1.2",
      filter: "url(#dotShadow)",
    }));
    g.append(svgEl("text", {
      x: boxX + boxW / 2, y: boxY + boxH / 2 + 4,
      "text-anchor": "middle",
      "font-size": "11.5", "font-weight": "600",
      fill: "#7a2828",
    }, text));
    svg.append(g);
  }

  return svg;
}

// ─── (Vertical-orientation variant removed — replaced by viewBox-based
// era zooming. Kept the function name reserved for future revisits.)

function renderCurveMobile_DEPRECATED(rulings) {
  const W = 380, H = 1100;
  const M = { top: 24, right: 14, bottom: 28, left: 78 };
  const innerW = W - M.left - M.right;
  const innerH = H - M.top - M.bottom;
  const YR_MIN = 1975, YR_MAX = 2027;
  const SEV_AXIS_MAX = 5.6;

  function xOf(sev) { return M.left + (sev / SEV_AXIS_MAX) * innerW; }
  function yOf(yd)  { return M.top  + ((yd - YR_MIN) / (YR_MAX - YR_MIN)) * innerH; }

  const points = rulings.map((r) => ({
    r,
    yd: curveYearDecimal(r.ruling_date),
    sev: SEVERITY_BY_OUTCOME[r.outcome] ?? 1,
  })).sort((a, b) => a.yd - b.yd);

  let envMax = 0;
  const envelope = points.map((p) => {
    envMax = Math.max(envMax, p.sev);
    return { yd: p.yd, sev: envMax };
  });

  const annotations = curveAnnotationsMap();
  const eras = curveEras();

  const svg = curveSvgEl("svg", {
    viewBox: `0 0 ${W} ${H}`,
    class: "curve curve-mobile",
    role: "img",
    "aria-label": t.curve_aria,
  });

  // defs
  const defs = curveSvgEl("defs");
  const envGrad = curveSvgEl("linearGradient", { id: "envFillV", x1: "0", y1: "0", x2: "1", y2: "0" });
  envGrad.append(curveSvgEl("stop", { offset: "0%",  "stop-color": "#b03a3a", "stop-opacity": "0.02" }));
  envGrad.append(curveSvgEl("stop", { offset: "100%", "stop-color": "#b03a3a", "stop-opacity": "0.30" }));
  defs.append(envGrad);
  const shadow = curveSvgEl("filter", { id: "dotShadowV", x: "-60%", y: "-60%", width: "220%", height: "220%" });
  shadow.append(curveSvgEl("feGaussianBlur", { in: "SourceAlpha", stdDeviation: "1.4" }));
  shadow.append(curveSvgEl("feOffset", { dx: "0", dy: "1.2", result: "off" }));
  shadow.append(curveSvgEl("feComponentTransfer", {},
    curveSvgEl("feFuncA", { type: "linear", slope: "0.4" })
  ));
  const sMerge = curveSvgEl("feMerge");
  sMerge.append(curveSvgEl("feMergeNode"));
  sMerge.append(curveSvgEl("feMergeNode", { in: "SourceGraphic" }));
  shadow.append(sMerge);
  defs.append(shadow);
  svg.append(defs);

  // Era horizontal bands + side stripes
  for (const era of eras) {
    const y1 = yOf(era.start);
    const y2 = yOf(era.end);
    svg.append(curveSvgEl("rect", {
      x: M.left, y: y1, width: innerW, height: y2 - y1,
      fill: era.fill,
    }));
    svg.append(curveSvgEl("rect", {
      x: M.left - 20, y: y1 + 3, width: 4, height: y2 - y1 - 6,
      fill: era.stripe, opacity: "0.75", rx: "2",
    }));
    const labelY = (y1 + y2) / 2;
    svg.append(curveSvgEl("text", {
      x: M.left - 30, y: labelY,
      "text-anchor": "middle",
      "font-size": "10", "font-weight": "700",
      "letter-spacing": "0.4",
      fill: era.stripe,
      transform: `rotate(-90 ${M.left - 30} ${labelY})`,
    }, era.label.toUpperCase()));
  }

  // Decade year labels + horizontal gridlines
  const decadeYears = [1980, 1990, 2000, 2010, 2020, 2026];
  for (const yr of decadeYears) {
    const y = yOf(yr);
    svg.append(curveSvgEl("line", {
      x1: M.left, x2: M.left + innerW, y1: y, y2: y,
      stroke: "#e8e8e8", "stroke-width": "1", "stroke-dasharray": "1 4",
    }));
    svg.append(curveSvgEl("text", {
      x: M.left - 4, y: y + 4,
      "text-anchor": "end",
      "font-size": "11", "font-weight": "500", fill: "#555",
    }, String(yr)));
  }

  // Y-axis line (time axis on left of chart area)
  svg.append(curveSvgEl("line", {
    x1: M.left, x2: M.left, y1: M.top, y2: M.top + innerH,
    stroke: "#888", "stroke-width": "1.2",
  }));

  // Envelope (filled area to the LEFT of running-max severity, then line)
  if (envelope.length) {
    let dArea = `M ${xOf(0)} ${yOf(YR_MIN)} L ${xOf(envelope[0].sev)} ${yOf(YR_MIN)} L ${xOf(envelope[0].sev)} ${yOf(envelope[0].yd)}`;
    for (let i = 1; i < envelope.length; i++) {
      const prev = envelope[i - 1], cur = envelope[i];
      dArea += ` L ${xOf(prev.sev)} ${yOf(cur.yd)} L ${xOf(cur.sev)} ${yOf(cur.yd)}`;
    }
    const lastSev = envelope[envelope.length - 1].sev;
    dArea += ` L ${xOf(lastSev)} ${yOf(YR_MAX)} L ${xOf(0)} ${yOf(YR_MAX)} Z`;
    svg.append(curveSvgEl("path", { d: dArea, fill: "url(#envFillV)" }));

    let dLine = `M ${xOf(envelope[0].sev)} ${yOf(YR_MIN)} L ${xOf(envelope[0].sev)} ${yOf(envelope[0].yd)}`;
    for (let i = 1; i < envelope.length; i++) {
      const prev = envelope[i - 1], cur = envelope[i];
      dLine += ` L ${xOf(prev.sev)} ${yOf(cur.yd)} L ${xOf(cur.sev)} ${yOf(cur.yd)}`;
    }
    dLine += ` L ${xOf(lastSev)} ${yOf(YR_MAX)}`;
    svg.append(curveSvgEl("path", {
      d: dLine, fill: "none",
      stroke: "#b03a3a", "stroke-width": "2",
      opacity: "0.85",
      "stroke-linejoin": "round",
    }));
  }

  // Dots
  for (const p of points) {
    const x = xOf(p.sev), y = yOf(p.yd);
    const color = DOT_COLOR_BY_OUTCOME[p.r.outcome] || "#666";
    const radius = p.sev >= 4 ? 6 : (p.sev >= 3 ? 5.5 : 5);
    const a = curveSvgEl("a", { href: `ruling.html?id=${p.r.case_id_slug}` });
    const circle = curveSvgEl("circle", {
      cx: x, cy: y, r: String(radius),
      fill: color, "fill-opacity": "0.97",
      stroke: "#fff", "stroke-width": "1.8",
      filter: "url(#dotShadowV)",
    });
    circle.append(curveSvgEl("title", {}, `${p.r.ruling_date} · ${p.r.case_id} · ${p.r.outcome.replace(/_/g, " ")}`));
    a.append(circle);
    svg.append(a);
  }

  // Annotation callouts beside the dot (alternating sides)
  // High-sev dots are on the right → label goes LEFT.
  // Low-sev dots are toward the left → label goes RIGHT.
  for (const p of points) {
    const ann = annotations[p.r.case_id_slug];
    if (!ann) continue;
    const x = xOf(p.sev), y = yOf(p.yd);
    const radius = p.sev >= 4 ? 6 : (p.sev >= 3 ? 5.5 : 5);
    const placeRight = p.sev <= 3;

    const text = ann;
    const charW = 5.8;
    const padX = 7;
    const boxW = Math.min(Math.round(text.length * charW + padX * 2), innerW - 30);
    const boxH = 22;
    const boxY = y - boxH / 2;

    let boxX = placeRight ? (x + radius + 8) : (x - radius - 8 - boxW);
    const rightLimit = M.left + innerW - 2;
    const leftLimit  = M.left + 2;
    if (boxX + boxW > rightLimit) boxX = rightLimit - boxW;
    if (boxX < leftLimit) boxX = leftLimit;

    const leadFromX = placeRight ? (x + radius + 1) : (x - radius - 1);
    const leadToX   = placeRight ? boxX : (boxX + boxW);
    svg.append(curveSvgEl("line", {
      x1: leadFromX, x2: leadToX, y1: y, y2: y,
      stroke: "#b03a3a", "stroke-width": "1.1", opacity: "0.7",
    }));

    svg.append(curveSvgEl("rect", {
      x: boxX, y: boxY, width: boxW, height: boxH,
      rx: "4", ry: "4",
      fill: "#ffffff",
      stroke: "#b03a3a", "stroke-width": "1.1",
      filter: "url(#dotShadowV)",
    }));
    svg.append(curveSvgEl("text", {
      x: boxX + boxW / 2, y: boxY + boxH / 2 + 4,
      "text-anchor": "middle",
      "font-size": "10", "font-weight": "600",
      fill: "#7a2828",
    }, text));
  }

  return svg;
}

function renderCurveSection(rulings) {
  const wrap = el("section", { class: "curve-section" });
  wrap.append(el("h2", { class: "curve-h2" }, t.curve_title));
  wrap.append(el("p", { class: "curve-subtitle" }, t.curve_subtitle));

  const svg = renderCurve(rulings);
  const svgWrap = el("div", { class: "curve-wrap" });
  svgWrap.append(svg);
  wrap.append(svgWrap);

  // Era zoom controls — change the SVG viewBox to focus on a slice.
  // Same chart, but text/dots grow as the viewBox shrinks → higher
  // legibility on phones; useful on desktop too for close inspection.
  // viewBox values match the desktop chart's geometry with margins
  // M.left=160, M.right=96, innerW=784. Era boundaries (1976→1995→2005.5
  // →2020.5→2026) map to SVG x ≈ 160 → 460 → 620 → 846 → 944. Each era
  // zoom includes a small buffer for context + the right-axis labels.
  const ZOOMS = [
    { id: "all",  label: t.zoom_all,    viewBox: "0 0 1040 500" },
    { id: "era1", label: "1976–2005",  viewBox: "0 0 700 500" },
    { id: "era2", label: "2006–2020",  viewBox: "560 0 360 500" },
    { id: "era3", label: "2021–2026",  viewBox: "790 0 250 500" },
  ];
  const zoomBar = el("div", { class: "curve-zoom-bar", "aria-label": t.zoom_hint });
  zoomBar.append(el("span", { class: "curve-zoom-label" }, t.zoom_hint));
  const buttons = [];
  for (const z of ZOOMS) {
    // dir="ltr" on year-range buttons so "1976–2005" doesn't reverse to
    // "2005–1976" in the Hebrew RTL layout. The "Full view" / "תצוגה מלאה"
    // label is intrinsically directional so dir="auto" handles it.
    const isYearRange = z.id !== "all";
    const btn = el("button", {
      class: "curve-zoom-btn",
      "data-zoom": z.id,
      dir: isYearRange ? "ltr" : "auto",
    }, z.label);
    btn.addEventListener("click", () => {
      svg.setAttribute("viewBox", z.viewBox);
      // Show only annotations whose tagged era matches the active zoom
      // (or all annotations when zoom is "all"). Era is set in renderCurve
      // from each ruling's year, so the filter is robust to boundary cases
      // where a dot sits inside a neighboring era's viewBox margin.
      for (const g of svg.querySelectorAll(".annotation")) {
        const annEra = g.getAttribute("data-era");
        const inView = z.id === "all" || annEra === z.id;
        g.style.display = inView ? "" : "none";
      }
      for (const b of buttons) {
        b.classList.toggle("active", b === btn);
      }
    });
    buttons.push(btn);
    zoomBar.append(btn);
  }
  buttons[0].classList.add("active");
  wrap.append(zoomBar);

  wrap.append(el("p", { class: "curve-caption" }, t.curve_caption));
  return wrap;
}

window.CO = { lang, t, el, fetchJSON, ruling_name, justice_name, role_label, renderHeader, renderFooter, renderCurve, renderCurveSection };
