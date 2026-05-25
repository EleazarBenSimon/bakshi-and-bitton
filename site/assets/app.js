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
    curve_subtitle: "מדוקטרינה שקטה אל מחוץ-לסטנדרט הדמוקרטי. ציר זמן של 14 פסיקות. גובה כל נקודה — עוצמת ההתערבות בהחלטת הרשות. הקו המקווקו הוא ההתערבות החריפה ביותר עד אותה נקודת זמן. לחיצה על נקודה פותחת את הפסיקה.",
    curve_caption: "מה רואים: חמישה עשורים של עליה כמעט בלתי-מורגשת, ופריצה אנכית ב-2023–2026. הסעיף השני ('קריאה') ידון בפרשנות.",
    curve_aria: "תרשים פיזור של 14 פסיקות בית המשפט העליון לפי שנה ועוצמת התערבות, 1976–2026",
    sev_1: "דחיית עתירה",
    sev_2: "הצהרתי / מצומצם",
    sev_3: "השבה לדיון",
    sev_4: "ביטול חלקי / צו עשה / התראת בטלות",
    sev_5: "ביטול חוק או החלטה",
    ann_dakka: "1976 · המצאת עילת הסבירות",
    ann_mizrahi: "1995 · הטענה לסמכות פסילת חוק-יסוד",
    ann_shafir: "2021 · התראת-בטלות ראשונה",
    ann_5658: "2024 · פסילת תיקון עילת הסבירות",
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
    curve_subtitle: "From quiet doctrine to constitutional outlier. A timeline of 14 rulings. Each dot's height is the severity of the Court's intervention; the dashed envelope traces the highest severity reached up to that point. Click any dot to open the ruling.",
    curve_caption: "What you see: an almost-imperceptible climb over five decades and a vertical break in 2023–2026. The Reading section discusses interpretation.",
    curve_aria: "Scatter plot of 14 Israeli Supreme Court rulings by year and intervention severity, 1976–2026",
    sev_1: "Petition dismissed",
    sev_2: "Declarative / restricted",
    sev_3: "Remanded",
    sev_4: "Partial strike / mandatory order / warning of voidness",
    sev_5: "Statute or decision struck",
    ann_dakka: "1976 · Reasonableness invented",
    ann_mizrahi: "1995 · Claim to strike Basic Laws",
    ann_shafir: "2021 · First warning of voidness",
    ann_5658: "2024 · Reasonableness amendment struck",
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

function renderCurve(rulings) {
  const NS = "http://www.w3.org/2000/svg";
  const W = 920, H = 380;
  const M = { top: 44, right: 32, bottom: 70, left: 60 };
  const innerW = W - M.left - M.right;
  const innerH = H - M.top - M.bottom;
  const YR_MIN = 1975, YR_MAX = 2027;
  const SEV_AXIS_MAX = 5.5;

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
    "156-75-dakka":           { text: t.ann_dakka,   side: "below", align: "middle", dy: 0 },
    "6821-93-bank-mizrahi":   { text: t.ann_mizrahi, side: "above", align: "middle", dy: 0 },
    "5969-20-shafir":         { text: t.ann_shafir,  side: "below", align: "middle", dy: 0 },
    "5658-23":                { text: t.ann_5658,    side: "above", align: "end",    dy: -8 },
    "gofman-mossad-2026-05":  { text: t.ann_gofman,  side: "below", align: "start",  dy: 14 },
  };

  const svg = svgEl("svg", {
    viewBox: `0 0 ${W} ${H}`,
    class: "curve",
    role: "img",
    "aria-label": t.curve_aria,
  });

  // Severity gridlines + y-axis labels
  const sevLabels = [
    [1, t.sev_1], [2, t.sev_2], [3, t.sev_3], [4, t.sev_4], [5, t.sev_5],
  ];
  for (const [s, label] of sevLabels) {
    const y = yOf(s);
    svg.append(svgEl("line", {
      x1: M.left, x2: M.left + innerW, y1: y, y2: y,
      stroke: "#f0f0f0", "stroke-width": "1",
    }));
    svg.append(svgEl("text", {
      x: M.left - 8, y: y + 4,
      "text-anchor": "end",
      "font-size": "10", fill: "#777",
    }, label));
  }

  // Decade gridlines + x-axis labels
  const decadeYears = [1980, 1990, 2000, 2010, 2020, 2026];
  for (const yr of decadeYears) {
    const x = xOf(yr);
    svg.append(svgEl("line", {
      x1: x, x2: x, y1: M.top, y2: M.top + innerH,
      stroke: "#f3f3f3", "stroke-width": "1",
    }));
    svg.append(svgEl("text", {
      x: x, y: M.top + innerH + 20,
      "text-anchor": "middle", "font-size": "12", fill: "#777",
    }, String(yr)));
  }

  // Axes
  svg.append(svgEl("line", {
    x1: M.left, x2: M.left + innerW, y1: M.top + innerH, y2: M.top + innerH,
    stroke: "#999", "stroke-width": "1",
  }));
  svg.append(svgEl("line", {
    x1: M.left, x2: M.left, y1: M.top, y2: M.top + innerH,
    stroke: "#999", "stroke-width": "1",
  }));

  // Running-max envelope (stepped line)
  if (envelope.length) {
    let d = `M ${xOf(envelope[0].yd)} ${yOf(0)} L ${xOf(envelope[0].yd)} ${yOf(envelope[0].sev)}`;
    for (let i = 1; i < envelope.length; i++) {
      const prev = envelope[i - 1], cur = envelope[i];
      d += ` L ${xOf(cur.yd)} ${yOf(prev.sev)} L ${xOf(cur.yd)} ${yOf(cur.sev)}`;
    }
    d += ` L ${xOf(YR_MAX)} ${yOf(envelope[envelope.length - 1].sev)}`;
    svg.append(svgEl("path", {
      d, fill: "none",
      stroke: "#555", "stroke-width": "1.5",
      "stroke-dasharray": "5 4", opacity: "0.6",
    }));
  }

  // Dots — each is a link to the ruling page
  for (const p of points) {
    const x = xOf(p.yd), y = yOf(p.sev);
    const color = DOT_COLOR_BY_OUTCOME[p.r.outcome] || "#666";
    const r = p.sev >= 4 ? 7 : (p.sev >= 3 ? 6 : 5);
    const a = svgEl("a", { href: `ruling.html?id=${p.r.case_id_slug}` });
    const circle = svgEl("circle", {
      cx: x, cy: y, r: String(r),
      fill: color, "fill-opacity": "0.85",
      stroke: "#fff", "stroke-width": "1.5",
    });
    circle.append(svgEl("title", {}, `${p.r.ruling_date} · ${p.r.case_id} · ${p.r.outcome.replace(/_/g, " ")}`));
    a.append(circle);
    svg.append(a);

    const ann = annotations[p.r.case_id_slug];
    if (ann) {
      const above = ann.side === "above";
      const baseLabelY = above ? y - 14 : y + 22;
      const labelY = baseLabelY + (ann.dy || 0);
      svg.append(svgEl("line", {
        x1: x, x2: x,
        y1: above ? y - r - 1 : y + r + 1,
        y2: above ? labelY + 4 : labelY - 10,
        stroke: "#b03a3a", "stroke-width": "1", opacity: "0.55",
      }));
      const labelX = ann.align === "end" ? x - 6 : (ann.align === "start" ? x + 6 : x);
      svg.append(svgEl("text", {
        x: labelX, y: labelY,
        "text-anchor": ann.align || "middle",
        "font-size": "10.5", "font-weight": "600",
        fill: "#b03a3a",
      }, ann.text));
    }
  }

  return svg;
}

function renderCurveSection(rulings) {
  const wrap = el("section", { class: "curve-section" });
  wrap.append(el("h2", { class: "curve-h2" }, t.curve_title));
  wrap.append(el("p", { class: "curve-subtitle" }, t.curve_subtitle));
  const svgWrap = el("div", { class: "curve-wrap" });
  svgWrap.append(renderCurve(rulings));
  wrap.append(svgWrap);
  wrap.append(el("p", { class: "curve-caption" }, t.curve_caption));
  return wrap;
}

window.CO = { lang, t, el, fetchJSON, ruling_name, justice_name, role_label, renderHeader, renderFooter, renderCurve, renderCurveSection };
