// Bakshi&Bitton — V0 client-side rendering
// Loads JSON data and renders pages. No framework, no build step.

const i18n = {
  he: {
    site_title: "בקשי וביטון",
    site_subtitle: "פסיקות בית המשפט העליון בעניין החלטות ממשלה ומינויים",
    nav_rulings: "פסיקות",
    nav_justices: "שופטים",
    nav_about: "אודות",
    nav_methodology: "מתודולוגיה",
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
    methodology_notice: "פרויקט זה מפרסם נתונים מובְנים מתוך תיעוד ציבורי של בית המשפט העליון. איננו מפרשים, מאפיינים או נוקטים עמדה. לפרטים, ראו עמוד המתודולוגיה.",
    role_President: "נשיא",
    role_AP: "ממלא מקום נשיא",
    role_DP: "משנה לנשיא",
    role_Justice: "שופט/ת",
    role_RJ: "שופט/ת בדימוס (בחלון סטטוטורי)",
  },
  en: {
    site_title: "Bakshi&Bitton",
    site_subtitle: "Israeli Supreme Court rulings on government decisions and appointments",
    nav_rulings: "Rulings",
    nav_justices: "Justices",
    nav_about: "About",
    nav_methodology: "Methodology",
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
    methodology_notice: "This project publishes structured data from public Israeli Supreme Court records. We do not interpret, characterize, or take positions. See the Methodology page for details.",
    role_President: "President",
    role_AP: "Acting President",
    role_DP: "Deputy President",
    role_Justice: "Justice",
    role_RJ: "Retired Justice (statutory post-retirement window)",
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
        el("a", { href: "justices.html", style: active === "justices" ? "font-weight:600;color:var(--accent)" : "" }, t.nav_justices),
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

window.CO = { lang, t, el, fetchJSON, ruling_name, justice_name, role_label, renderHeader, renderFooter };
