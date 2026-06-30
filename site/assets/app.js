// Bakshi&Bitton — V0 client-side rendering
// Loads JSON data and renders pages. No framework, no build step.

const i18n = {
  he: {
    site_title: "בקשי&ביטון",
    site_subtitle: "פסיקות בית המשפט העליון בעניין החלטות ממשלה ומינויים",
    nav_rulings: "פסיקות",
    nav_reading: "קריאה",
    nav_justices: "שופטים",
    nav_structure: "מבנה הכוח",
    nav_cite: "ציטוט והפצה",
    nav_about: "אודות",
    nav_methodology: "מתודולוגיה",
    nav_tags: "נושאים",
    tags_title: "נושאים — עיון לפי תחום",
    tags_intro: "כל פסיקה במאגר מתויגת לפי הנושאים המשפטיים והמדיניותיים שבהם היא נוגעת. בחרו נושא כדי לראות את הפסיקות המקושרות אליו — גודל התגית משקף את מספר הפסיקות.",
    tags_hint: "בחרו נושא מהענן כדי לראות את הפסיקות הקשורות אליו.",
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
    label_print_citation: "מקור רשמי (בדפוס בלבד)",
    label_online_secondary: "מקור מקוון (משני — אינו נוסח פסק הדין)",
    label_secondary_sources: "מקורות משניים",
    label_summary: "תקציר",
    label_predicate_ag: "חוות-דעת היועמ\"ש שקדמה",
    label_respondent_body: "גוף נושא ההחלטה",
    label_compliance: "מצב יישום",
    label_defiance: "סימני התנגדות",
    label_tags: "תיוגים",
    label_notes: "הערות",
    label_related_reading: "קריאה נוספת",
    label_filing_date: "תאריך הגשה",
    label_ruling_date: "תאריך הפסיקה",
    filter_all: "הכל",
    filter_outcome: "סנן לפי תוצאה",
    filter_doctrine: "סנן לפי עילה",
    filter_petitioner: "סנן לפי סוג עותר",
    filter_compliance: "סנן לפי מצב יישום",
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
    curve_subtitle: "העקומה האדומה מצטברת ומשוקללת: בכל פסיקה היא עולה לפי סוג ההתפשטות של בית המשפט בה (רכישה +3, הרחבה +1, יישום שגרתי 0). 'רכישה' = פעם ראשונה שבית המשפט מתערב בצירוף (רשות נבחרת × תחום מדיניות) חדש. 'הרחבה' = יישום שיפוטי לתחום-משנה חדש בצירוף שכבר נכבש. 'יישום' = הפעלה שגרתית של דוקטרינה מבוססת. גודל הנקודה מבטא את היקף ההכרעה הפרטנית — כמה מרחיקת-לכת הייתה התוצאה באותה פסיקה (לא 'חומרה'). כל מקרה בספריית פרשנות מצמצמת (חוק שבוטל או רוקן) מוסיף +1, כך שהעקומה מסכמת את מלוא העברת הכוח המתועדת — 70 אירועים, לא רק 22. ראו METHODOLOGY-power-transfer.md לפירוט.",
    curve_caption: "מה רואים: נורמליזציה הדרגתית של ההתפשטות השיפוטית לתחומים שמעולם לא ניתנה לבית המשפט סמכות מפורשת מאת הציבור או נציגיו. נקודות שלא מעלות את העקומה הן 'יישומים' — שגרתיות בתוך תחום שכבר נכבש; נקודות שמעלות אנכית את העקומה הן 'רכישות' של תחום שלם חדש. השכבה השנייה ('קריאה') תדון בפרשנות.",
    cum_axis_label: "מדד הסמכות (מצטבר)",
    curve_aria: "תרשים פיזור של פסיקות בית המשפט העליון לפי שנה ומדד הסמכות המצטבר, 1976–2026",
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
    cat_badge_essays: "מאמר",
    cat_badge_explainers: "הסבר",
    cat_badge_patterns: "תיעוד דפוס",
    filter_category: "סינון:",
    filter_all_categories: "הכל",
    read_time: (n) => `${n} דק׳ קריאה`,
    word_count_label: (n) => `${n} מילים`,
    toc_title: "תוכן העמוד",
    toc_toggle: "תוכן העמוד",
    quick_answer: "תשובה מהירה",
    quick_answer_aria: "תמצית המאמר במשפט אחד",
    read_next: "להמשך קריאה",
    share_label: "שיתוף",
    share_x: "שתף ב-X",
    share_copy: "העתק קישור",
    share_print: "הדפסה / PDF",
    share_email: "שלח במייל",
    copied: "הקישור הועתק",
    back_to_top: "חזרה לראש העמוד",
    reading_progress_aria: "התקדמות הקריאה",
    no_match_filter: "אין פריטים שעונים על הסינון",
    curve_sr_pointer: "אותם נתונים זמינים כטבלה מלאה הניתנת למיון בהמשך העמוד.",
    stat_rulings: "פסיקות במאגר",
    stat_struck: "בוטלו (מלא/חלקי)",
    stat_years: "שנות תיעוד",
    stat_enbanc: "הרכבים מורחבים (9+)",
    stat_documented: "מקרים מתועדים",
    stat_neutralized: "חוקים שבוטלו או רוקנו",
    stat_hollowed: "רוקנו בפרשנות — בשקט",
    scale_note_a: (n) => `${n} התיקים המלאים שלמטה הם רק הליבה.`,
    scale_note_link: (n) => `המאגר המלא: ${n} מקרים מתועדים ←`,
    scale_note_b: "כל אחד מהם — חוק או החלטה של נבחרי הציבור שבית המשפט ביטל או רוקן מתוכן.",
    filter_clear: "נקה סינון",
    filter_search_label: "חיפוש",
    curve_show: "הצג את עקומת הסמכות",
    curve_hide: "הסתר עקומה",
    sort_aria: "מיין לפי טור זה",
  },
  en: {
    site_title: "Bakshi&Bitton",
    site_subtitle: "Israeli Supreme Court rulings on government decisions and appointments",
    nav_rulings: "Rulings",
    nav_reading: "Reading",
    nav_justices: "Justices",
    nav_structure: "Power Structure",
    nav_cite: "Cite & Share",
    nav_about: "About",
    nav_methodology: "Methodology",
    nav_tags: "Topics",
    tags_title: "Topics — browse by theme",
    tags_intro: "Every ruling in the archive is tagged by the legal and policy themes it touches. Pick a topic to see its linked rulings — tag size reflects how many rulings carry it.",
    tags_hint: "Pick a topic from the cloud to see its rulings.",
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
    label_print_citation: "Official source (print only)",
    label_online_secondary: "Online source (secondary — not the ruling text)",
    label_secondary_sources: "Secondary sources",
    label_summary: "Summary",
    label_predicate_ag: "Predicate AG opinion",
    label_respondent_body: "Decision-making body",
    label_compliance: "Compliance status",
    label_defiance: "Defiance signals",
    label_tags: "Tags",
    label_notes: "Notes",
    label_related_reading: "Related reading",
    label_filing_date: "Filing date",
    label_ruling_date: "Ruling date",
    filter_all: "All",
    filter_outcome: "Filter by outcome",
    filter_doctrine: "Filter by doctrine",
    filter_petitioner: "Filter by petitioner",
    filter_compliance: "Filter by compliance",
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
    curve_subtitle: "The red curve is cumulative and weighted: each ruling adds height according to the kind of competence reach it represents (acquisition +3, extension +1, routine application 0). 'Acquisition' = first ruling in a (target-branch × policy-domain) cell. 'Extension' = application to a meaningfully new sub-domain within an already-claimed cell. 'Application' = routine use of settled doctrine. Dot size encodes the reach of the individual disposition — how far-reaching that ruling's result was (not 'severity'). Each reading-down library case (a law struck or hollowed) adds +1, so the curve sums the full documented transfer of power — 70 events, not just 22. See METHODOLOGY-power-transfer.md for full criteria.",
    curve_caption: "What you see: the gradual normalization of judicial reach into domains never expressly authorized by the public or its elected representatives. Dots that do NOT raise the curve are 'applications' — routine use within already-claimed territory; dots that raise the curve sharply are 'acquisitions' of entirely new domains. The site's second layer ('Reading') discusses interpretation.",
    cum_axis_label: "Authority index (cumulative)",
    curve_aria: "Scatter plot of Israeli Supreme Court rulings by year and cumulative authority index, 1976–2026",
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
    cat_badge_essays: "Essay",
    cat_badge_explainers: "Explainer",
    cat_badge_patterns: "Pattern",
    filter_category: "Filter:",
    filter_all_categories: "All",
    read_time: (n) => `${n} min read`,
    word_count_label: (n) => `${n} words`,
    toc_title: "On this page",
    toc_toggle: "Contents",
    quick_answer: "Quick answer",
    quick_answer_aria: "One-sentence summary",
    read_next: "Read next",
    share_label: "Share",
    share_x: "Share on X",
    share_copy: "Copy link",
    share_print: "Print / PDF",
    share_email: "Email",
    copied: "Link copied",
    back_to_top: "Back to top",
    reading_progress_aria: "Reading progress",
    no_match_filter: "No items match the filter",
    curve_sr_pointer: "The same data is available as a full, sortable table below.",
    stat_rulings: "rulings catalogued",
    stat_struck: "struck (full/partial)",
    stat_years: "years covered",
    stat_enbanc: "expanded panels (9+)",
    stat_documented: "documented cases",
    stat_neutralized: "laws struck or hollowed",
    stat_hollowed: "hollowed by reinterpretation — quietly",
    scale_note_a: (n) => `The ${n} full case files below are only the core.`,
    scale_note_link: (n) => `The full evidence base: ${n} documented cases →`,
    scale_note_b: "Each one a law or decision of the people's elected branch that the Court struck or quietly emptied of content.",
    filter_clear: "Clear filters",
    filter_search_label: "Search",
    curve_show: "Show the authority curve",
    curve_hide: "Hide curve",
    sort_aria: "Sort by this column",
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

// ─── Controlled-vocabulary labels ───────────────────────────────────────
// Human-readable Hebrew/English for the enum fields. Kept in sync with
// scripts/build.py (which emits the same maps to _data/labels.json for the
// prerendered static pages). Renders "בוטל" / "Struck down" instead of the
// raw code "struck_down".
const LABELS = {
  outcome: {
    he: { struck_down: "בוטל", partially_struck: "בוטל חלקית", mandatory_order: "צו עשה",
          warning_of_voidness: "התראת בטלות", remanded: "הוחזר לדיון", dismissed: "נדחה",
          declarative: "הצהרתי" },
    en: { struck_down: "Struck down", partially_struck: "Partially struck",
          mandatory_order: "Mandatory order", warning_of_voidness: "Warning of voidness",
          remanded: "Remanded", dismissed: "Dismissed", declarative: "Declarative" },
  },
  doctrine: {
    he: { reasonableness: "עילת הסבירות", proportionality: "מידתיות", ultra_vires: "חריגה מסמכות",
          separation_of_powers: "הפרדת רשויות", judicial_independence: "עצמאות שיפוטית",
          procedural_review: "ביקורת הליכית", conflict_of_interest: "ניגוד עניינים",
          constitutional_supremacy: "עליונות חוקתית", constituent_authority_limits: "גבולות הסמכות המכוננת",
          abuse_of_constituent_power: "שימוש לרעה בסמכות מכוננת", basic_law_judiciary: "חוק-יסוד: השפיטה",
          basic_law_government: "חוק-יסוד: הממשלה", basic_law_human_dignity_and_liberty: "חוק-יסוד: כבוד האדם וחירותו" },
    en: { reasonableness: "Reasonableness", proportionality: "Proportionality", ultra_vires: "Ultra vires",
          separation_of_powers: "Separation of powers", judicial_independence: "Judicial independence",
          procedural_review: "Procedural review", conflict_of_interest: "Conflict of interest",
          constitutional_supremacy: "Constitutional supremacy", constituent_authority_limits: "Constituent-authority limits",
          abuse_of_constituent_power: "Abuse of constituent power", basic_law_judiciary: "Basic Law: The Judiciary",
          basic_law_government: "Basic Law: The Government", basic_law_human_dignity_and_liberty: "Basic Law: Human Dignity and Liberty" },
  },
  petitioner_type: {
    he: { NGO: "ארגון חברה אזרחית", individual: "יחיד/ה", political: "גורם פוליטי",
          local_authority: "רשות מקומית", corporation: "תאגיד", party: "סיעה" },
    en: {},
  },
  compliance_state: {
    he: { complied: "קוים", defied: "לא קוים", partial: "קוים חלקית", pending: "תלוי ועומד", moot: "התייתר" },
    en: {},
  },
  respondent: {
    he: { Knesset: "הכנסת", Government: "הממשלה", Cabinet: "הממשלה", Minister: "שר/ה",
          "Prime Minister": "ראש הממשלה", Statute: "חקיקה", "Local-Authority": "רשות מקומית",
          "Senior-Appointments-Committee": "הוועדה לבדיקת מינויים בכירים" },
    en: {},
  },
  // Theme tags (for the tag browser). HE labels are authoritative; EN falls
  // back to a humanized slug except where the humanized form reads poorly.
  tags: {
    he: {
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
    },
    en: {
      "post-oct7": "Post-Oct 7", "ag-non-defense": "AG declined to defend", "shin-bet": "Shin Bet (GSS)",
      "en-banc": "En banc", "deri": "Deri affair", "holot": "Holot facility", "tal-law": "Tal Law",
      "barak-court": "The Barak Court", "ngo-petitioner": "Civil-society petitioner", "first-of-kind": "First of its kind",
      "civil-wrongs": "Civil wrongs (state liability)", "qatargate": "Qatargate", "gas-framework": "Gas framework",
    },
  },
};
function labelFor(kind, code) {
  if (code == null || code === "") return code;
  const m = (LABELS[kind] && LABELS[kind][lang]) || {};
  if (m[code]) return m[code];
  // English fallback: humanize the raw code (Title case, underscores → spaces)
  return String(code).replace(/_/g, " ");
}
function outcome_label(o) { return labelFor("outcome", o); }
function doctrine_label(d) { return labelFor("doctrine", d); }
function doctrines_label(arr) { return (arr || []).map(doctrine_label).join(", "); }
function petitioner_type_label(p) { return labelFor("petitioner_type", p); }
function compliance_label(c) { return labelFor("compliance_state", c); }
function respondent_label(r) { return labelFor("respondent", r); }
function tag_label(slug) {
  const m = (LABELS.tags && LABELS.tags[lang]) || {};
  if (m[slug]) return m[slug];
  // Humanize the slug: hyphens/underscores → spaces, Title Case (EN fallback).
  return String(slug).replace(/[-_]/g, " ").replace(/\b\w/g, c => c.toUpperCase());
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
        el("a", { href: "tags.html", style: active === "tags" ? "font-weight:600;color:var(--accent)" : "" }, t.nav_tags),
        el("a", { href: "content.html?slug=power-structure", style: active === "structure" ? "font-weight:600;color:var(--accent)" : "" }, t.nav_structure),
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
  };
}

function curveEras() {
  return [
    { start: 1975, end: 2005.5, label: t.era_1, fill: "rgba(90,122,154,0.05)",  stripe: "#5a7a9a" },
    { start: 2005.5, end: 2020.5, label: t.era_2, fill: "rgba(196,125,39,0.07)", stripe: "#c47d27" },
    { start: 2020.5, end: 2027, label: t.era_3, fill: "rgba(176,58,58,0.10)",   stripe: "#b03a3a" },
  ];
}

function renderCurve(rulings, extraEvents = [], domain = null) {
  const NS = "http://www.w3.org/2000/svg";
  const W = 1040, H = 500;
  const M = { top: 88, right: 48, bottom: 80, left: 96 };
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
  // Visible x-domain (year span). null → full range; an era domain re-fits
  // the curve so that slice fills the plot width (a true zoom, not a viewBox
  // crop). The cumulative y-scale stays global, so a focused era's height is
  // still read against the full accumulation.
  const X_LO = domain ? domain[0] : YR_MIN;
  const X_HI = domain ? domain[1] : YR_MAX;
  function xOf(yd) { return M.left + ((yd - X_LO) / (X_HI - X_LO)) * innerW; }
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

  // Muted deep-red gradient for the cumulative line (oxblood → crimson —
  // grave, no bright/warm tones) + a soft glow that lifts it off the grid.
  const curveGrad = svgEl("linearGradient", { id: "curveGrad", x1: "0", y1: "0", x2: "1", y2: "0" });
  curveGrad.append(svgEl("stop", { offset: "0%", "stop-color": "#7e3330" }));
  curveGrad.append(svgEl("stop", { offset: "60%", "stop-color": "#a23635" }));
  curveGrad.append(svgEl("stop", { offset: "100%", "stop-color": "#b83b3b" }));
  defs.append(curveGrad);

  const softGlow = svgEl("filter", { id: "curveSoft", x: "-60%", y: "-60%", width: "220%", height: "220%" });
  softGlow.append(svgEl("feGaussianBlur", { in: "SourceGraphic", stdDeviation: "2.4", result: "sb" }));
  const sgT = svgEl("feComponentTransfer", { in: "sb", result: "sbb" });
  sgT.append(svgEl("feFuncA", { type: "linear", slope: "0.6" }));
  softGlow.append(sgT);
  const sgM = svgEl("feMerge");
  sgM.append(svgEl("feMergeNode", { in: "sbb" }));
  sgM.append(svgEl("feMergeNode", { in: "SourceGraphic" }));
  softGlow.append(sgM);
  defs.append(softGlow);

  // Clip the cumulative line/area to the plot, so a re-fitted (zoomed) view
  // shows only the in-window segment — the line enters at the left edge at the
  // height it had already accumulated to by that year.
  const plotClip = svgEl("clipPath", { id: "plotClip" });
  plotClip.append(svgEl("rect", { x: M.left, y: M.top - 6, width: innerW, height: innerH + 10 }));
  defs.append(plotClip);

  svg.append(defs);

  // ── era backgrounds + headers ────────────────────────────────────
  for (let i = 0; i < eras.length; i++) {
    const era = eras[i];
    // Skip eras entirely outside the visible window; clamp the rest to the plot.
    if (era.end <= X_LO || era.start >= X_HI) continue;
    const x1 = xOf(Math.max(era.start, X_LO));
    const x2 = xOf(Math.min(era.end, X_HI));
    svg.append(svgEl("rect", {
      x: x1, y: M.top, width: x2 - x1, height: innerH,
      fill: era.fill,
    }));
    svg.append(svgEl("rect", {
      x: x1 + 1, y: M.top - 26, width: Math.max(0, x2 - x1 - 2), height: 4,
      fill: era.stripe, opacity: "0.7", rx: "2",
    }));
    svg.append(svgEl("text", {
      x: (x1 + x2) / 2, y: M.top - 34,
      "text-anchor": "middle",
      "font-size": "11.5", "font-weight": "700",
      "letter-spacing": "0.6",
      fill: era.stripe,
    }, era.label.toUpperCase()));
    // Clickable era header → "focus" this era: re-fit the curve to it AND
    // filter the table. renderCurveSection owns that (via the co-era-focus
    // event), so the curve stays decoupled from whatever page hosts it.
    const hit = svgEl("rect", {
      x: x1, y: M.top - 42, width: x2 - x1, height: 40,
      fill: "transparent", "pointer-events": "all",
      class: "era-hit", tabindex: "0", role: "button",
      "aria-label": (lang === "he" ? "התמקדות בתקופה " : "Focus era ") + era.label,
    });
    hit.append(svgEl("title", {}, lang === "he"
      ? "לחצו להתמקדות בתקופה זו — הגדלת העקומה וסינון הטבלה"
      : "Click to focus this era — zoom the curve and filter the table"));
    const fireEra = () => document.dispatchEvent(new CustomEvent("co-era-focus", { detail: { idx: i } }));
    hit.addEventListener("click", fireEra);
    hit.addEventListener("keydown", (ev) => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); fireEra(); } });
    svg.append(hit);
    // Inter-era divider — only when the boundary actually falls inside the view.
    if (i < eras.length - 1 && era.end > X_LO && era.end < X_HI) {
      svg.append(svgEl("line", {
        x1: x2, x2: x2, y1: M.top - 18, y2: M.top + innerH,
        stroke: "#d0d0d0", "stroke-width": "1", "stroke-dasharray": "3 3",
      }));
    }
  }

  // Severity y-axis intentionally removed — dots now sit on the curve
  // at their cumulative contribution height (see dot block below). Outcome
  // severity is re-encoded as dot RADIUS instead of dot Y-position, so the
  // chart has a single coherent y-axis (cumulative engagement) and dots
  // visibly cause the curve they sit on.

  // ── gridlines + x-axis labels (ticks adapt to the visible window) ─
  const tStep = (X_HI - X_LO) > 40 ? 10 : (X_HI - X_LO) > 18 ? 5 : (X_HI - X_LO) > 8 ? 2 : 1;
  const tickYears = [];
  for (let yr = Math.ceil(X_LO / tStep) * tStep; yr <= X_HI; yr += tStep) {
    if (yr >= X_LO && yr <= X_HI) tickYears.push(yr);
  }
  for (const yr of tickYears) {
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
  // Weights per METHODOLOGY-power-transfer.md §4. Rulings without a
  // competence_class (legacy/unclassified) fall through to weight 1 so
  // the curve degrades gracefully if a new ruling is added before being
  // coded against the methodology.
  const WEIGHT_BY_COMPETENCE_CLASS = {
    acquisition: 3,
    extension:   1,
    application: 0,
    ratification: 0,
  };
  function weightOf(r) {
    if (r.competence_class && r.competence_class in WEIGHT_BY_COMPETENCE_CLASS) {
      return WEIGHT_BY_COMPETENCE_CLASS[r.competence_class];
    }
    return 1; // legacy fallback for un-coded rulings
  }

  const CUM_HEADROOM = 0.92;

  // Merge the coded rulings with the reading-down library cases into ONE
  // chronological power-transfer stream. Rulings keep their competence-class
  // weight (acquisition +3, extension +1, application 0); each library case
  // (a law struck or read down) adds +1 — so the curve SUMS the full
  // documented shift of power away from the elected branch, not just the 22
  // deep-file rulings. Library events are tagged 'lib' → smaller dots below.
  const LIB_WEIGHT = 1;
  const mergedEvents = points.map((p) => ({ yd: p.yd, w: weightOf(p.r), kind: "ruling", p }));
  for (const ev of (extraEvents || [])) {
    const yd = yearDecimal(String(ev.when || ""));
    if (yd >= YR_MIN && yd <= YR_MAX) mergedEvents.push({ yd, w: LIB_WEIGHT, kind: "lib", ev });
  }
  mergedEvents.sort((a, b) => a.yd - b.yd);

  let cumTotal = 0;
  for (const e of mergedEvents) cumTotal += e.w;
  function yCum(c) { return M.top + innerH - (c / Math.max(1, cumTotal)) * innerH * CUM_HEADROOM; }

  // Cumulative-after each event; the line climbs through ALL of them, so
  // every documented case visibly raises it — the accumulation IS the story.
  const cumXY = [{ x: xOf(YR_MIN), y: yCum(0) }];
  const cumByCase = {};
  let cum = 0;
  for (const e of mergedEvents) {
    cum += e.w;
    e.cumAfter = cum;
    if (e.kind === "ruling") cumByCase[e.p.r.case_id_slug] = cum;
    cumXY.push({ x: xOf(e.yd), y: yCum(cum) });
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
      // Bezier control points, clamped into the [p1,p2] bounding box so
      // the curve is monotonic in x (no backward dips) and monotonic in
      // y (no overshoots above p2 or below p1 on a cumulative curve).
      // Without these clamps, near-boundary segments and segments where
      // adjacent data points are at very different x-distances cause
      // wild tangent estimates and the curve loops away from the dots.
      const clampX = (v) => Math.max(p1.x, Math.min(p2.x, v));
      const clampY = (v) => Math.max(p2.y, Math.min(p1.y, v));
      const cp1x = clampX(p1.x + (p2.x - p0.x) * t / 6);
      const cp1y = clampY(p1.y + (p2.y - p0.y) * t / 6);
      const cp2x = clampX(p2.x - (p3.x - p1.x) * t / 6);
      const cp2y = clampY(p2.y - (p3.y - p1.y) * t / 6);
      d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`;
    }
    return d;
  }

  const curveLine = catmullRomPath(cumXY);
  const baselineY = yCum(0);
  const curveArea = curveLine + ` L ${cumXY[cumXY.length - 1].x} ${baselineY} L ${cumXY[0].x} ${baselineY} Z`;

  svg.append(svgEl("path", { d: curveArea, fill: "url(#envFill)", "clip-path": "url(#plotClip)" }));
  const cumLineEl = svgEl("path", {
    d: curveLine, fill: "none",
    stroke: "url(#curveGrad)", "stroke-width": "2.8",
    opacity: "0.95",
    "stroke-linecap": "round",
    "stroke-linejoin": "round",
    filter: "url(#curveSoft)",
    "clip-path": "url(#plotClip)",
    class: "cum-line",
  });
  // Animated draw-in (CSS keyframes via --len; reduced-motion disables it).
  try { cumLineEl.style.setProperty("--len", cumLineEl.getTotalLength()); } catch (e) {}
  svg.append(cumLineEl);

  // ── left-side y-axis: cumulative engagement count ────────────────
  // Cumulative is the only y-axis now (severity axis removed). Tick
  // labels and gridlines extend across the chart so dots/curve can be
  // read off the same scale.
  const leftAxisX = M.left;
  // Tick spacing chosen to give ~5 labels at "round" values regardless
  // of the dataset's weighted total (currently 46; will grow with
  // additions). Stepping by 10 keeps the axis legible for totals up to
  // a few hundred without recomputing.
  const tickStep = cumTotal <= 25 ? 5 : (cumTotal <= 80 ? 10 : 20);
  const cumTicks = [];
  for (let c = 0; c <= cumTotal; c += tickStep) cumTicks.push(c);
  for (const c of cumTicks) {
    const y = yCum(c);
    svg.append(svgEl("line", {
      x1: leftAxisX, x2: leftAxisX + innerW, y1: y, y2: y,
      stroke: "#e8e8e8", "stroke-width": "1",
    }));
    svg.append(svgEl("line", {
      x1: leftAxisX - 5, x2: leftAxisX, y1: y, y2: y,
      stroke: "#888", "stroke-width": "1",
    }));
    svg.append(svgEl("text", {
      x: leftAxisX - 9, y: y + 4,
      "text-anchor": "end", "font-size": "11",
      fill: "#555", "font-weight": "600",
    }, String(c)));
  }
  svg.append(svgEl("text", {
    x: leftAxisX - 9, y: M.top - 14,
    "text-anchor": "end", "font-size": "10.5",
    fill: "#7a2828", "font-weight": "700",
    "letter-spacing": "0.3",
  }, t.cum_axis_label));

  // ── secondary event dots: the reading-down library (summed in) ──
  // Each library case is summed into the cumulative line above (weight +1),
  // so these dots sit at the height AFTER they incremented it — visibly
  // contributing to the climb, not merely riding it. Smaller/translucent so
  // the coded-ruling dots stay dominant. Hover shows the case; click opens
  // the library. To revert: drop this block + curve_events.json.
  const EVENT_COLOR = { struck: "#b03a3a", read_down: "#9c6529" };
  for (const e of mergedEvents) {
    if (e.kind !== "lib") continue;
    if (e.yd < X_LO || e.yd > X_HI) continue;
    const ev = e.ev;
    const lbl = lang === "he"
      ? (ev.kind === "struck" ? "בוטל" : "פרשנות מצמצמת")
      : (ev.kind === "struck" ? "struck" : "read down");
    const a = svgEl("a", { href: "reading-quiet-veto.html", class: "curve-ev" });
    const c = svgEl("circle", {
      cx: xOf(e.yd), cy: yCum(e.cumAfter), r: "3.2",
      fill: EVENT_COLOR[ev.kind] || "#888", "fill-opacity": "0.5",
      stroke: "#fff", "stroke-width": "1",
      class: "ev", "data-tip": `${ev.docket} — ${ev.name}`, "data-sub": `${ev.when} · ${lbl}`,
    });
    a.append(c);
    svg.append(a);
  }

  // ── dots (positioned ON the cumulative curve) ───────────────────
  // Each dot sits at (year, cumulative-count-when-added), so it visibly
  // *causes* the curve's climb at that point. Severity is re-encoded as
  // dot RADIUS (sev 5 strikes are biggest, sev 1 dismissals smallest).
  for (const p of points) {
    if (p.yd < X_LO || p.yd > X_HI) continue;
    const x = xOf(p.yd), y = yCum(cumByCase[p.r.case_id_slug]);
    const color = DOT_COLOR_BY_OUTCOME[p.r.outcome] || "#666";
    const radius = 4 + p.sev;
    const a = svgEl("a", { href: `ruling.html?id=${p.r.case_id_slug}` });

    if (p.sev >= 4) {
      const halo = svgEl("circle", {
        cx: x, cy: y, r: String(radius + 5),
        fill: color, "fill-opacity": "0.18",
        filter: "url(#dotGlow)",
      });
      a.append(halo);
    }

    const nm = lang === "he" ? (p.r.case_name_he || p.r.case_name_en) : (p.r.case_name_en || p.r.case_name_he);
    const tipTxt = `${p.r.case_id} — ${nm}`;
    const docs = doctrines_label(p.r.doctrine_invoked || []);
    const tipSub = `${p.r.ruling_date} · ${outcome_label(p.r.outcome)}${docs ? " · " + docs : ""}`;
    const circle = svgEl("circle", {
      cx: x, cy: y, r: String(radius),
      fill: color, "fill-opacity": "0.97",
      stroke: "#fff", "stroke-width": "2.2",
      filter: "url(#dotShadow)",
      class: "ev", "data-tip": tipTxt, "data-sub": tipSub,
    });
    a.append(circle);
    svg.append(a);
  }

  // Hover highlight ring — moved onto the dot under the pointer (kept on top).
  svg.append(svgEl("circle", {
    cx: "-20", cy: "-20", r: "0", fill: "none",
    stroke: "#b03a3a", "stroke-width": "2", "stroke-opacity": "0.95",
    class: "curve-hl", "pointer-events": "none",
  }));

  // ── annotation callouts (boxed, with leader lines) ───────────────
  // Only annotations whose anchor is inside the visible window are drawn,
  // so a re-fitted (zoomed) era stays clean.
  for (const p of points) {
    const ann = annotations[p.r.case_id_slug];
    if (!ann) continue;
    if (p.yd < X_LO || p.yd > X_HI) continue;
    const x = xOf(p.yd), y = yCum(cumByCase[p.r.case_id_slug]);
    // For dots high on the curve, push label below; for dots low, push
    // label above. Ignores the per-annotation `side` setting — those
    // were tuned for the old severity-based dot positions.
    const above = y > M.top + innerH * 0.5;
    const radius = 4 + p.sev;

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

function renderCurveSection(rulings, extraEvents = []) {
  const wrap = el("section", { class: "curve-section", "aria-label": t.curve_title });
  wrap.append(el("h2", { class: "curve-h2" }, t.curve_title));
  wrap.append(el("p", { class: "curve-subtitle" }, t.curve_subtitle));

  let svg = renderCurve(rulings, extraEvents);
  const svgWrap = el("div", { class: "curve-wrap" });
  svgWrap.append(svg);

  // Anchored hover bubble that points at the exact dot, + a highlight ring.
  // Bound per-SVG so it keeps working after the curve is re-rendered for an
  // era focus (the <svg> element is swapped out).
  const cTip = el("div", { class: "curve-tip" });
  const cArr = el("div", { class: "curve-tip-arr" });
  const cTxt = el("span", { class: "curve-tip-main" });
  const cSub = el("span", { class: "curve-tip-sub" });
  cTip.append(cArr, cTxt, cSub);
  svgWrap.append(cTip);

  function bindTip(target) {
    target.addEventListener("pointerover", (e) => {
      const c = e.target;
      if (!c.classList || !c.classList.contains("ev")) return;
      const cx = +c.getAttribute("cx"), cy = +c.getAttribute("cy"), r = +c.getAttribute("r");
      const ring = target.querySelector(".curve-hl");
      if (ring) { ring.setAttribute("cx", cx); ring.setAttribute("cy", cy); ring.setAttribute("r", r + 4); ring.style.opacity = "1"; }
      const vb = target.viewBox.baseVal, rect = target.getBoundingClientRect();
      const px = (cx - vb.x) / vb.width * rect.width;
      const py = (cy - vb.y) / vb.height * rect.height;
      cTxt.textContent = c.getAttribute("data-tip") || "";
      const sub = c.getAttribute("data-sub") || "";
      cSub.textContent = sub;
      cSub.style.display = sub ? "block" : "none";
      cTip.style.opacity = "1";
      const bw = cTip.offsetWidth, bh = cTip.offsetHeight;
      const below = py < bh + 30;
      const left = Math.max(2, Math.min(px - bw / 2, rect.width - bw - 2));
      cTip.style.left = left + "px";
      cTip.style.top = (below ? py + r + 9 : py - r - 9 - bh) + "px";
      cArr.className = "curve-tip-arr " + (below ? "up" : "down");
      cArr.style.left = Math.max(8, Math.min(px - left - 7, bw - 22)) + "px";
      cArr.style.top = (below ? -7 : bh - 1) + "px";
    });
    target.addEventListener("pointerout", (e) => {
      if (e.target.classList && e.target.classList.contains("ev")) {
        cTip.style.opacity = "0";
        const ring = target.querySelector(".curve-hl");
        if (ring) ring.style.opacity = "0";
      }
    });
  }
  bindTip(svg);

  wrap.append(svgWrap);
  // Screen-reader pointer: the chart is decorative-analytical; the same data
  // is available as a sortable table immediately below.
  wrap.append(el("p", { class: "visually-hidden" }, t.curve_sr_pointer));

  // ── Unified era control ──────────────────────────────────────────
  // One accessible segmented control. Selecting an era RE-FITS the curve so
  // that span fills the plot width (a genuine zoom — not a viewBox crop) AND
  // filters the rulings table to that era (via the co-era-filter event the
  // host page listens for). Clicking an era band on the curve does the same
  // (dispatches co-era-focus, handled here). The first segment resets both.
  const ERAS = curveEras();
  const SEGS = [
    { idx: -1, name: t.zoom_all,     range: null,        color: null },
    { idx: 0,  name: ERAS[0].label,  range: "1976–2005", color: ERAS[0].stripe },
    { idx: 1,  name: ERAS[1].label,  range: "2006–2020", color: ERAS[1].stripe },
    { idx: 2,  name: ERAS[2].label,  range: "2021–2026", color: ERAS[2].stripe },
  ];
  function domainFor(idx) {
    if (idx < 0) return null;
    const e = ERAS[idx];
    const pad = (e.end - e.start) * 0.04;  // breathing room so edge dots aren't flush
    return [e.start - pad, e.end + pad];
  }
  function tableRangeFor(idx) {
    if (idx < 0) return null;
    const lo = idx === 0 ? 0 : Math.floor(ERAS[idx].start) + 1;
    const hi = idx === ERAS.length - 1 ? 9999 : Math.floor(ERAS[idx].end);
    return { start: lo, end: hi, label: ERAS[idx].label };
  }

  const control = el("div", { class: "curve-era-control", role: "group", "aria-label": t.zoom_hint });
  const segButtons = [];
  let curIdx = -1;
  for (const s of SEGS) {
    const seg = el("button", {
      class: "era-seg" + (s.idx < 0 ? " era-seg--all" : ""),
      type: "button", "data-idx": String(s.idx),
      "aria-pressed": s.idx < 0 ? "true" : "false",
      style: s.color ? `--seg-color:${s.color}` : "",
    },
      s.color ? el("span", { class: "era-seg-dot", "aria-hidden": "true" }) : null,
      el("span", { class: "era-seg-name" }, s.name),
      s.range ? el("span", { class: "era-seg-range", dir: "ltr" }, s.range) : null
    );
    seg.addEventListener("click", () => selectEra(s.idx));
    segButtons.push(seg);
    control.append(seg);
  }

  function selectEra(idx) {
    curIdx = idx;
    const fresh = renderCurve(rulings, extraEvents, domainFor(idx));
    svg.replaceWith(fresh);
    svg = fresh;
    bindTip(svg);
    for (const b of segButtons) {
      const on = b.getAttribute("data-idx") === String(idx);
      b.classList.toggle("on", on);
      b.setAttribute("aria-pressed", on ? "true" : "false");
    }
    document.dispatchEvent(new CustomEvent("co-era-filter", { detail: tableRangeFor(idx) }));
  }

  // Era-band clicks on the curve (and the table's "clear" affordance) route
  // here, so every entry point drives the one unified behavior. Clicking the
  // already-focused era toggles back to the full view.
  document.addEventListener("co-era-focus", (e) => {
    const idx = (e && e.detail && typeof e.detail.idx === "number") ? e.detail.idx : -1;
    selectEra(idx === curIdx && idx >= 0 ? -1 : idx);
  });
  segButtons[0].classList.add("on");
  wrap.append(control);

  wrap.append(el("p", { class: "curve-caption" }, t.curve_caption));
  return wrap;
}

// Editorial satire (DISPLAY-ONLY): sweep rendered text nodes and render the
// petitioner "Movement for Quality Government" with its "for quality" claim
// struck through + "(for abolition)". The data keeps the org's real name; this
// only decorates what is shown, to match the prerendered pages (build.py).
function decorateMQG(root) {
  if (!root) return;
  const reTest = /(התנועה למען איכות השלטון|Movement for Quality Government)/i;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
  const targets = [];
  let n;
  while ((n = walker.nextNode())) {
    if (n.parentNode && n.parentNode.closest && n.parentNode.closest("del.mqg-strike")) continue;
    if (reTest.test(n.nodeValue)) targets.push(n);
  }
  for (const node of targets) {
    const h = node.nodeValue
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/התנועה למען איכות השלטון/g, 'התנועה למען <del class="mqg-strike">איכות</del>(ביטול) השלטון')
      .replace(/Movement for Quality Government/gi, 'Movement for <del class="mqg-strike">Quality</del> (Abolition of) Government');
    const span = document.createElement("span");
    span.innerHTML = h;
    node.parentNode.replaceChild(span, node);
  }
}

// Bold public-facing hero atop a ruling (SPA view) — mirrors build.py _ruling_hero.
function renderRulingHero(r) {
  const panel = r.panel || [];
  const s2n = {}; for (const j of panel) s2n[j.slug] = lang === "he" ? j.name_he : j.name_en;
  const leads = (r.majority_authors || []).map(s => s2n[s] || s).filter(Boolean);
  const hero = el("div", { class: "ruling-hero" });
  hero.append(el("span", { class: `rh-verdict outcome-pill outcome-${r.outcome}` }, outcome_label(r.outcome)));
  hero.append(el("h1", { class: "rh-case" }, r.case_id));
  hero.append(el("p", { class: "rh-name" }, ruling_name(r)));
  hero.append(el("p", { class: "rh-summary" }, lang === "he" ? r.summary_he : r.summary_en));
  const st = el("div", { class: "rh-stats" }); let any = false;
  if (panel.length) { st.append(el("span", { class: "rh-stat" }, el("b", {}, String(panel.length)), lang === "he" ? " שופטים" : " justices")); any = true; }
  if (r.vote_majority != null) { st.append(el("span", { class: "rh-stat" }, lang === "he" ? "הצבעה " : "vote ", el("b", {}, `${r.vote_majority}–${r.vote_minority ?? 0}`))); any = true; }
  if (leads.length) { st.append(el("span", { class: "rh-stat" }, lang === "he" ? "חוות-הדעת המובילה: " : "lead opinion: ", el("b", {}, leads.join(", ")))); any = true; }
  if (any) hero.append(st);
  return hero;
}

// ─── Tag browser (themes) ────────────────────────────────────────────
// A frequency-weighted cloud of every theme tag in the corpus. Click a tag
// to list the rulings that carry it; deep-linkable via tags.html?tag=slug.
function renderTagBrowser(rulings) {
  const main = el("main", { class: "tags-page" });
  main.append(el("h1", {}, t.tags_title));
  main.append(el("p", { class: "tags-intro" }, t.tags_intro));

  const byTag = new Map();
  for (const r of rulings)
    for (const tg of (r.tags || [])) {
      if (!byTag.has(tg)) byTag.set(tg, []);
      byTag.get(tg).push(r);
    }
  const collator = new Intl.Collator(lang === "he" ? "he" : "en");
  const entries = [...byTag.entries()]
    .sort((a, b) => b[1].length - a[1].length || collator.compare(tag_label(a[0]), tag_label(b[0])));
  const maxN = entries.length ? entries[0][1].length : 1;

  const cloud = el("div", { class: "tag-cloud" });
  const results = el("div", { class: "tag-results" });
  results.append(el("p", { class: "tag-results-hint" }, t.tags_hint));

  let activeChip = null;
  function showTag(slug, chip) {
    if (activeChip) activeChip.classList.remove("on");
    activeChip = chip || null;
    if (chip) chip.classList.add("on");
    const list = (byTag.get(slug) || []).slice()
      .sort((a, b) => (b.ruling_date || "").localeCompare(a.ruling_date || ""));
    results.replaceChildren(
      el("div", { class: "tag-results-head" },
        el("span", { class: "tag-results-title" }, tag_label(slug)),
        el("span", { class: "tag-results-count" }, t.rulings_count(list.length))));
    const ul = el("ul", { class: "tag-result-list" });
    for (const r of list) {
      const href = `ruling-${r.case_id_slug}.html`;
      ul.append(el("li", {},
        el("a", { href },
          el("span", { class: "trl-case" }, r.case_id),
          el("span", { class: "trl-name" }, ruling_name(r))),
        el("span", { class: `outcome-pill outcome-${r.outcome}` }, outcome_label(r.outcome))));
    }
    results.append(ul);
    try { history.replaceState(null, "", `tags.html?tag=${encodeURIComponent(slug)}`); } catch (e) {}
  }

  entries.forEach(([slug, rs]) => {
    const n = rs.length;
    const size = (0.92 + (n - 1) / Math.max(1, maxN - 1) * 0.85).toFixed(2);
    const chip = el("button", { class: "tag-chip", type: "button", style: `font-size:${size}rem` },
      tag_label(slug), el("span", { class: "tag-chip-n" }, String(n)));
    chip.addEventListener("click", () => showTag(slug, chip));
    cloud.append(chip);
  });

  main.append(cloud, results);

  const pre = new URLSearchParams(location.search).get("tag");
  if (pre && byTag.has(pre)) {
    const idx = entries.findIndex(e => e[0] === pre);
    showTag(pre, cloud.children[idx] || null);
  }
  return main;
}

window.CO = { lang, t, el, fetchJSON, ruling_name, justice_name, role_label, renderHeader, renderFooter, renderCurve, renderCurveSection, outcome_label, doctrine_label, doctrines_label, petitioner_type_label, compliance_label, respondent_label, tag_label, renderTagBrowser, SEVERITY_BY_OUTCOME, decorateMQG, renderRulingHero };
