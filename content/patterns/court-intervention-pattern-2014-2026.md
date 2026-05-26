---
title: "Pattern: Israeli Supreme Court interventions in elected-branch decisions, 1976-2026"
title_he: "דפוס: התערבויות בית המשפט העליון בהחלטות הרשויות הנבחרות, 1976–2026"
title_en: "Pattern: Israeli Supreme Court interventions in elected-branch decisions, 1976-2026"
contributor: "@EleazarBenSimon"
date: 2026-05-25
summary: An empirical pattern analysis drawn from the 14 rulings in this project's documentary core. The data spans 50 years and three doctrinal layers — foundational power-assertion (1976-1995), abuse-of-constituent-power crystallization (2021-2024), and active intervention (2014-2026). 13 of 14 cases either struck the challenged measure or asserted new Court authority over it; 1 declined.
summary_he: "ניתוח דפוסים אמפירי המבוסס על 14 הפסיקות שבליבה התיעודית של הפרויקט. הנתונים פרושים על-פני 50 שנה ושלוש שכבות דוקטרינריות — הצהרת סמכות יסודית (1995-1976), גיבוש דוקטרינת השימוש לרעה בסמכות מכוננת (2024-2021), והתערבות אקטיבית (2026-2014). ב-13 מתוך 14 המקרים בית המשפט ביטל את הפעולה שעמדה לביקורת או הצהיר על סמכות חדשה לגביה; באחד נמנע."
summary_en: An empirical pattern analysis drawn from the 14 rulings in this project's documentary core. The data spans 50 years and three doctrinal layers — foundational power-assertion (1976-1995), abuse-of-constituent-power crystallization (2021-2024), and active intervention (2014-2026). 13 of 14 cases either struck the challenged measure or asserted new Court authority over it; 1 declined.
---

# Pattern: Israeli Supreme Court Interventions in Elected-Branch Decisions, 1976-2026

This document is a structured pattern analysis drawn from the documentary core of this project. It surveys the 14 Supreme Court rulings cataloged in `data/rulings/` and identifies recurring features.

This is empirical: every quantitative claim below cites the specific case-IDs in the documentary core. Readers can verify each count by examining the JSON entries directly.

## The documentary core, summarized

The 14 cataloged rulings, in chronological order:

| # | Case | Date | Disposition | Doctrine | Petitioner |
|---|---|---|---|---|---|
| 1 | [Dakka v. Min. Transportation](../../data/rulings/156-75-dakka.json) | 1976 | Declarative (denied; doctrine established) | Reasonableness (foundation) | Individual |
| 2 | [Bank Mizrahi v. Migdal](../../data/rulings/6821-93-bank-mizrahi.json) | 1995-11-09 | Declarative (statute upheld; judicial-review power asserted) | Constitutional supremacy | Individual (commercial) |
| 3 | [Sela v. Yehieli (Kfar Vradim mikveh)](../../data/rulings/662-11-sela-kfar-vradim-mikveh.json) | 2014-09-09 | Struck down | Reasonableness | Individuals |
| 4 | [Yesh Atid v. PM (Litzman)](../../data/rulings/3132-15-yesh-atid-litzman.json) | 2015-08-23 | Struck down | Reasonableness; Basic Law: Government | Party |
| 5 | [ACRI v. Min. Public Security](../../data/rulings/1892-14-acri-prison-space.json) | 2017-06-13 | Struck down (mandatory order) | Reasonableness | NGO |
| 6 | [Shafir v. Knesset](../../data/rulings/5969-20-shafir.json) | 2021-05-23 | Warning of voidness | Abuse of constituent power | Party |
| 7 | [Zilber v. Min. Finance](../../data/rulings/5782-21-zilber.json) | 2022-01-12 | Partially struck | Reasonableness | Individual |
| 8 | [Deri (HCJ 8948/22)](../../data/rulings/8948-22-deri.json) | 2023-01-18 | Struck down | Reasonableness | NGO |
| 9 | [HCJ 5658/23 (reasonableness amendment)](../../data/rulings/5658-23.json) | 2024-01-01 | Struck down | Constituent authority limits; Basic Law: Judiciary | NGO |
| 10 | [HCJ 5119/23 (incapacitation law)](../../data/rulings/5119-23-incapacitation.json) | 2024-01-03 | Partially struck | Abuse of constituent power | NGO |
| 11 | [MQG v. Min. Justice (Levin / Judicial Selection Committee)](../../data/rulings/8987-22-levin-jsc.json) | 2024-09-12 | Mandatory order | Ultra vires; separation of powers | NGO |
| 12 | [Baharav-Miara dismissal](../../data/rulings/18225-06-25-baharav-miara.json) | 2025-12-14 | Struck down | Procedural review; conflict of interest | NGO |
| 13 | [Zini / Shin Bet](../../data/rulings/427-10-25-zini.json) | 2025-12-28 | Dismissed (Court declined to intervene) | Conflict of interest; reasonableness | NGO |
| 14 | [Gofman / Mossad](../../data/rulings/gofman-mossad-2026-05.json) | 2026-05-19 | Remanded | Procedural review; reasonableness | Individual + NGO |

## Pattern 1: Direction of disposition

Grouped by the Court's action, the 14 documented rulings break down as:

| Category | Count | Cases |
|---|---|---|
| **Active intervention** (struck / partially struck / remanded / mandatory order) | 10 | Sela, Litzman, ACRI, Zilber, Deri, HCJ 5658/23, HCJ 5119/23, Levin/JSC, Baharav-Miara, Gofman |
| **Doctrinal power-assertion without immediate strike** (declarative or warning-of-voidness) | 3 | Dakka 1976 (reasonableness established), Bank Mizrahi 1995 (constitutional-supremacy + judicial-review-of-legislation asserted), Shafir 2021 (abuse-of-constituent-power test articulated) |
| **Court declined to intervene** (dismissed) | 1 | Zini |

Out of 14 cataloged rulings, **13 either struck the challenged measure or asserted new Court authority over its class of measures.** The single exception (Zini) was itself contested within the Court — 2-1, with the current President Amit dissenting; the unanimous Gofman remand six months later applied analytically similar logic to a comparable security-service appointment.

**Caveat on this pattern**: The documentary core is a non-random selection of high-profile rulings, not a representative sample. The Court rules on thousands of petitions per year, most of which never produce the kind of intervention documented here. What the 13:1 ratio shows is not the Court's overall intervention rate; it shows **the shape of high-profile cases that reach the documentary surface** — that when the Court engages with an elected-branch decision of consequence, asserting authority over it (whether by striking, compelling, or expanding doctrine) is the default outcome.

## Pattern 2: Three doctrinal layers

The dataset spans 50 years across three identifiable doctrinal layers:

### Layer A — Foundational power-assertion (1976-1995)

| Case | What was asserted |
|---|---|
| Dakka 1976 | Reasonableness as standalone ground of administrative review (later expanded into the "balancing" form that drives most of Layer C) |
| Bank Mizrahi 1995 | Basic Laws as constitutional rank; judicial power to invalidate primary legislation that conflicts with them — both asserted in obiter dicta in a private commercial-banking appeal |

In neither case did the immediate disposition strike anything. The doctrinal architecture asserted in these rulings is what makes Layers B and C possible.

### Layer B — Abuse-of-constituent-power crystallization (2021-2024)

| Case | Step in the doctrinal arc |
|---|---|
| Shafir 2021 | Tripartite test established (abuse of constituent power, generality, compatibility with constitutional fabric); warning of voidness issued |
| HCJ 5658/23 (Jan 2024) | First operative use to strike a Basic Law amendment — the reasonableness amendment, 8-7 en banc |
| HCJ 5119/23 (Jan 2024) | Second operative use, same day; the incapacitation amendment held to apply only from next Knesset (6-5 partial strike via delayed-effect interpretation) |

Layer B is the project's most concentrated doctrinal cluster: a single test articulated in Shafir was used twice on the same day in January 2024 against the most consequential Basic Law amendments the Knesset had passed in that legislative cycle.

### Layer C — Active intervention in elected-branch decisions (2014-2026)

The other 8 cases in the dataset: Sela, Litzman, ACRI, Zilber, Deri, Levin/JSC, Baharav-Miara, Zini, Gofman. These apply doctrines from Layers A and B to specific government decisions and appointments.

## Pattern 3: Doctrinal distribution

Doctrines invoked across the 14 rulings:

| Doctrine | Count | Cases |
|---|---|---|
| Reasonableness | 8 | Dakka (foundation), Sela, Litzman, ACRI, Zilber, Deri, Gofman, Levin/JSC |
| Abuse of constituent power | 3 | Shafir (foundation), HCJ 5658/23, HCJ 5119/23 |
| Constituent authority limits | 4 | Shafir, HCJ 5658/23, HCJ 5119/23, Bank Mizrahi (obliquely) |
| Procedural review | 2 | Baharav-Miara, Gofman |
| Conflict of interest | 2 | Baharav-Miara, Zini |
| Basic Law: Government | 2 | Litzman, Shafir |
| Basic Law: Judiciary | 1 | HCJ 5658/23 |
| Constitutional supremacy | 1 | Bank Mizrahi |
| Ultra vires | 1 | Levin/JSC |
| Separation of powers | 1 | Levin/JSC |
| Judicial independence | 1 | Levin/JSC |

**Reasonableness remains the most-used doctrine** — invoked in 8 of 14 cases, spanning from its 1976 foundation in Dakka through the 2026 Gofman remand. The 2024 reasonableness amendment (struck in HCJ 5658/23) would have eliminated reasonableness review for cabinet/PM/minister decisions. Had it stood, four of the rulings in this documentary core (Litzman, Deri, Zilber, Levin/JSC) might not have proceeded on their current grounds. The Court's decision to strike that amendment — preserving its most-used doctrine — is itself a documented pattern.

**Abuse of constituent power is the second-most-used doctrinal cluster** post-2021 — 3 of 14 cases in 5 years. All three cluster in the Shafir → HCJ 5658/23 → HCJ 5119/23 arc.

## Pattern 4: Petitioner type

Who brings the petitions:

| Petitioner type | Count | Cases |
|---|---|---|
| NGO | 7 | ACRI (#5), Deri (#8, MQG), HCJ 5658/23 (#9, MQG + Bar Assn), HCJ 5119/23 (#10, MQG), Levin/JSC (#11, MQG), Baharav-Miara (#12, MQG + Bar + others), Zini (#13, MQG + 4 ex-Shin Bet chiefs) |
| Individual | 4 | Dakka (#1), Bank Mizrahi (#2, commercial), Sela (#3), Zilber (#7), Gofman (#14, Elmakayes + NGOs) |
| Party | 3 | Litzman (#4, Yesh Atid), Shafir (#6, former MK + NGOs) |

(Note: Gofman appears in both NGO and Individual categories — petition was individual + NGO co-petitioners; counted once as Individual+NGO.)

The **Movement for Quality Government** (התנועה למען איכות השלטון) appears as the lead or major co-petitioner in **6 of 14 cases** (#8, #9, #10, #11, #12, #13) — Deri, HCJ 5658/23, HCJ 5119/23, Levin/JSC, Baharav-Miara, and Zini.

This concentration is structurally significant: a single repeat-player NGO drives the petition flow on the cases that most directly contest the elected branch's appointment and Basic-Law-amendment authority. This is public information — MQG's role is openly stated — but the empirical density of its presence in the post-2022 cluster (5 of 7 post-2022 cases in this dataset, or 71%) is itself a pattern.

## Pattern 5: Time distribution

Rulings by period:

| Period | Count | Cases |
|---|---|---|
| 1976 | 1 | Dakka (reasonableness foundation) |
| 1995 | 1 | Bank Mizrahi (judicial-review foundation) |
| 1996-2013 | 0 | — |
| 2014-2017 | 3 | Sela 2014; Litzman 2015; ACRI 2017 |
| 2018-2020 | 0 | — |
| 2021-2022 | 2 | Shafir 2021; Zilber 2022 |
| 2023-2026 | 7 | Deri 2023; HCJ 5658/23 Jan 2024; HCJ 5119/23 Jan 2024; Levin/JSC Sep 2024; Baharav-Miara Dec 2025; Zini Dec 2025; Gofman May 2026 |

**Half of all 14 documented rulings — 7 of 14 — come from the 2023-2026 window** (3 years and 5 months). This includes two same-day Basic-Law-amendment rulings (5658/23 and 5119/23 on January 1-3, 2024), a mandatory-order against a sitting minister (Levin/JSC), the dismissal of an AG (Baharav-Miara), and three security-service-appointment rulings (Zini, Gofman, plus the appointment-cluster Court declined on).

The blank stretches (1996-2013, 2018-2020) likely reflect the project's selection focus on high-profile rulings and the political composition of those years' coalitions; they are not claims that the Court did not intervene during those periods.

What the time distribution does show: the **post-2022 period is unusually dense with documented interventions**, and the doctrinal arc cataloged here (Layer A → Layer B → Layer C) reaches its operational peak in this period.

## Pattern 6: What the elected branch was attempting

Decision types challenged in these 14 rulings:

| Decision type | Cases | Count |
|---|---|---|
| Ministerial appointment | Litzman, Deri, Zini, Gofman | 4 |
| Basic Law amendment | HCJ 5658/23, HCJ 5119/23, Shafir | 3 |
| Primary legislation (statute) | Bank Mizrahi | 1 |
| AG dismissal | Baharav-Miara | 1 |
| Ministerial inaction (failure to convene Selection Committee) | Levin/JSC | 1 |
| Policy / regulation | Zilber daycare cancellation | 1 |
| Administrative action / inaction | ACRI prison-space | 1 |
| Administrative reasonableness (transportation) | Dakka | 1 |
| Local-authority decision | Sela mikveh | 1 |

**Appointments are the most-challenged decision type** — 4 of 14 cases. Adding the AG-dismissal and the Selection-Committee inaction case, **6 of 14 cases concern judicial-or-AG-related personnel decisions** — the structural mechanisms by which the legal-establishment composition is renewed.

**Basic Law amendments are the second-most-challenged decision type** — 3 of 14, all concentrated in the Layer B cluster (Shafir → 5658/23 → 5119/23). This is novel: prior to Shafir 2021, the Court had never operatively voided or warned-of-voidness a Basic Law amendment. Three such rulings in 32 months.

## What the data shows together

Taking these patterns together, the documentary core supports several observations:

1. **The Court's authority is self-asserted in obiter and operationalized later.** The foundational power-assertions (Dakka 1976, Bank Mizrahi 1995, Shafir 2021) did not strike anything; they articulated tests later used to strike. Each layer was built before it was used.

2. **The active-intervention default is robust.** In 13 of 14 documented cases the Court either struck the challenged measure or asserted new authority over its class. The single dismissal (Zini) was internally contested 2-1.

3. **Reasonableness is the operational core, and the Court protected it.** Reasonableness appears in 8 of 14 cases across all three layers. The 2024 strike of the reasonableness amendment preserved the Court's most-used doctrine.

4. **A small set of repeat NGOs drives the high-profile petitions.** MQG appears in 6 of 14 cases (5 of 7 post-2022); the Israeli Bar Association is a frequent co-petitioner. The pattern is a small number of repeat-player petitioners producing a disproportionate share of the cases that reach this dataset.

5. **Appointments and structural-personnel decisions are the dominant contested category.** Counting ministerial appointments (4) + AG dismissal (1) + Selection-Committee inaction (1) yields 6 of 14 — the cases that contest the renewal mechanism of the legal establishment specifically.

6. **The doctrinal expansion of Basic-Law-amendment review is concentrated in a narrow window.** Three operative rulings in 32 months (Shafir May 2021; HCJ 5658/23 and 5119/23 same-day in January 2024).

## What the data does NOT show

This pattern document is deliberately limited to what the documentary core empirically demonstrates. It does not, and is not intended to, support claims about:

- The motives or political alignment of individual justices
- Whether any specific intervention was substantively correct or incorrect
- Whether the overall pattern of intervention is good or bad for Israeli democracy
- The intentions of any petitioner organization

These questions are legitimate and are debated extensively elsewhere — including in the further-reading sources cited below. But they are not what the structured data can answer. The structured data answers: how often, on what grounds, brought by whom, with what outcome.

## Further reading

- [Moshe Cohen-Eliya, "Israel's Juristocracy"](https://lawliberty.org/israels-juristocracy/) — the framing this project's editorial layer engages
- [Israel Democracy Institute — Doing Away with the Standard of Extreme Unreasonableness](https://en.idi.org.il/articles/50000) — the IDI's empirical analysis
- [Ran Hirschl, *Towards Juristocracy*](https://www.hup.harvard.edu/books/9780674025479) — the comparative-empirical theoretical anchor; Hirschl's framework is critical-empirical rather than reform-prescriptive (and Hirschl himself, who died May 19 2026, did not endorse the 2023-2024 Israeli reform effort)
- [Verfassungsblog — Saving the Constitution from Politics (on Shafir)](https://verfassungsblog.de/saving-the-constitution-from-politics/)
- See also the explainers in `../explainers/` (reasonableness doctrine, constituent authority, judicial selection committee) and the historical essay `../essays/from-bank-mizrahi-to-hcj-5658-23.md`
