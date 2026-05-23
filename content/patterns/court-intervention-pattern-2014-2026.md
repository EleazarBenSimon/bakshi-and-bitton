---
title: "Pattern: Israeli Supreme Court interventions in elected-branch decisions, 2014-2026"
contributor: "@EleazarBenSimon"
date: 2026-05-23
summary: An empirical pattern analysis drawn directly from the 9 rulings in this project's documentary core. The data shows the Court intervening against the elected branch in 8 of 9 documented cases, across a range of doctrines, with NGO petitioners driving the majority of cases.
---

# Pattern: Israeli Supreme Court Interventions in Elected-Branch Decisions, 2014-2026

This document is a structured pattern analysis drawn from the documentary core of this project. It surveys the 9 Supreme Court rulings cataloged in `data/rulings/` and identifies recurring features.

This is empirical: every quantitative claim below cites the specific case-IDs in the documentary core. Readers can verify each count by examining the JSON entries directly.

## The documentary core, summarized

The 9 cataloged rulings, in chronological order:

| # | Case | Date | Court action | Doctrine | Petitioner |
|---|---|---|---|---|---|
| 1 | [Sela v. Yehieli (Kfar Vradim mikveh)](../../data/rulings/662-11-sela-kfar-vradim-mikveh.json) | 2014-09-09 | Struck down | Reasonableness | Individuals |
| 2 | [Yesh Atid v. PM (Litzman)](../../data/rulings/3132-15-yesh-atid-litzman.json) | 2015-08-23 | Struck down | Reasonableness; Basic Law: Government | Party |
| 3 | [ACRI v. Min. Public Security](../../data/rulings/1892-14-acri-prison-space.json) | 2017-06-13 | Struck down (mandatory order) | Reasonableness | NGO |
| 4 | [Zilber v. Min. Finance](../../data/rulings/5782-21-zilber.json) | 2022-01-12 | Partially struck | Reasonableness | Individual |
| 5 | [Deri (HCJ 8948/22)](../../data/rulings/8948-22-deri.json) | 2023-01-18 | Struck down | Reasonableness | NGO |
| 6 | [HCJ 5658/23 (reasonableness amendment)](../../data/rulings/5658-23.json) | 2024-01-01 | Struck down | Constituent authority limits; Basic Law: The Judiciary | NGO |
| 7 | [Baharav-Miara dismissal](../../data/rulings/18225-06-25-baharav-miara.json) | 2025-12-14 | Struck down | Procedural review; conflict of interest | NGO |
| 8 | [Zini / Shin Bet](../../data/rulings/427-10-25-zini.json) | 2025-12-28 | Dismissed (Court declined to intervene) | Conflict of interest; reasonableness | NGO |
| 9 | [Gofman / Mossad](../../data/rulings/gofman-mossad-2026-05.json) | 2026-05-19 | Remanded | Procedural review; reasonableness | Individual + NGO |

## Pattern 1: Direction of intervention

Of the 9 documented rulings, **8 are interventions against the elected branch** (struck down, partially struck, remanded, or mandatory order issued). **1** (Zini) is a case where the Court declined to intervene.

| Outcome | Count |
|---|---|
| Struck down or partially struck | 5 (#1, 2, 4, 5, 6, 7) — Sela, Litzman, Zilber, Deri, HCJ 5658/23, Baharav-Miara dismissal |
| Mandatory order (functionally a strike-down against administrative non-implementation) | 1 (#3 — ACRI prison-space) |
| Remanded | 1 (#9 — Gofman) |
| Dismissed (Court declined to intervene) | 1 (#8 — Zini) |

The 8:1 ratio is striking. It is consistent with what Cohen-Eliya in [*Israel's Juristocracy*](https://lawliberty.org/israels-juristocracy/) identifies as the operational signature of the post-Barak Court: an institution that intervenes routinely in the elected branch's decisions on appointments, regulations, and structural matters.

**Important caveat on this pattern**: This documentary core is a small, non-random selection of high-profile rulings, not a representative sample of all Supreme Court rulings. The Court rules on thousands of petitions per year, most of which never reach the level of intervention documented here. The 8:1 ratio reflects the **shape of high-profile cases**, not the Court's overall intervention rate.

What the ratio does show: when the elected branch's most consequential decisions (Basic Law amendments, ministerial appointments, AG dismissal, security-service chiefs) are brought before the Court, **intervention is the default outcome.**

## Pattern 2: Doctrinal distribution

Doctrines invoked across the 9 rulings:

| Doctrine | Count | Cases |
|---|---|---|
| Reasonableness | 6 | Sela, Litzman, ACRI, Zilber, Deri, Gofman |
| Procedural review | 2 | Baharav-Miara dismissal, Gofman |
| Conflict of interest | 2 | Baharav-Miara dismissal, Zini |
| Constituent authority limits | 1 | HCJ 5658/23 |
| Basic Law: The Judiciary | 1 | HCJ 5658/23 |
| Basic Law: Government | 1 | Litzman |

**Reasonableness is the most-used doctrine** — 6 of 9 documented cases. This is consistent with Cohen-Eliya's empirical observation that reasonableness has been the most-used ground for review of executive decisions since the 1980s.

The 2024 reasonableness amendment (struck in HCJ 5658/23) would have eliminated reasonableness review for cabinet/PM/minister decisions. Had the amendment stood, three of the rulings in this documentary core (Litzman, Deri, Zilber) might not have been possible under their current grounds. The court's decision to strike that amendment — preserving its own most-used doctrine — is itself a documented pattern.

## Pattern 3: Petitioner type

Who brings the petitions that result in these rulings:

| Petitioner type | Count | Cases |
|---|---|---|
| NGO | 5 | ACRI (#3), Deri (#5, MQG), HCJ 5658/23 (#6, MQG + Israeli Bar Assn), Baharav-Miara (#7, MQG + Bar + others), Zini (#8, MQG + 4 ex-Shin Bet chiefs) |
| Individual | 3 | Sela (#1), Zilber (#4), Gofman (#9, Elmakayes + NGOs) |
| Party | 1 | Yesh Atid (#2, Litzman) |

The **Movement for Quality Government** (התנועה למען איכות השלטון) appears as the lead or major co-petitioner in **4 of 9 cases** (#5, #6, #7, #8) — Deri, HCJ 5658/23, Baharav-Miara dismissal, and Zini.

This concentration matters: a small number of NGOs drive a disproportionate share of the petitions that result in elected-branch intervention. This is not a hidden fact — MQG's role is public — but it is structurally significant. The Court is intervening on what is, in effect, a recurring small set of repeat-player petitioners.

## Pattern 4: Time distribution

Rulings by year:

| Period | Count |
|---|---|
| 2014-2017 | 3 (#1 Sela 2014; #2 Litzman 2015; #3 ACRI 2017) |
| 2018-2021 | 0 |
| 2022-2026 | 6 (#4 Zilber 2022; #5 Deri 2023; #6 HCJ 5658/23 2024; #7 Baharav-Miara 2025; #8 Zini 2025; #9 Gofman 2026) |

**Two-thirds of the documented rulings come from 2022-2026** — the period of the current Netanyahu coalition government, the 2023 reform package, the post-October-7 crisis, and the post-Jan-2024 acceleration of intervention. The four-year gap (2018-2021) likely reflects the project's selection focus on high-profile interventions and the political quiet of those years' coalition compositions; it is not a claim that the Court did not intervene during that period.

What the time distribution does show: the **post-2022 period is dense with documented interventions**. This is consistent with Cohen-Eliya's framing that the post-Hayut Court accelerated its interventionist posture in response to the reform effort — striking down the reasonableness amendment, blocking high-profile appointments (Zini partially; Gofman), and asserting new authorities (review of Basic Law amendments).

## Pattern 5: What the elected branch was attempting to do

The decisions challenged in these 9 rulings, by type:

| Decision type | Cases | Count |
|---|---|---|
| Ministerial appointment | Litzman (#2); Deri (#5); Zini (#8) — Court declined; Gofman (#9) | 4 |
| AG dismissal | Baharav-Miara (#7) | 1 |
| Basic Law amendment | HCJ 5658/23 (#6) | 1 |
| Policy / regulation | Zilber daycare cancellation (#4) | 1 |
| Administrative action / inaction | ACRI prison-space (#3) | 1 |
| Local-authority decision | Sela mikveh (#1) | 1 |

**Appointments are the most-challenged decision type** — 4 of 9 cases. This is consistent with the "Selection Committee battles" pattern that has dominated 2025-2026 politics: the elected branch attempts a high-profile appointment (Deri to Interior; Zini to Shin Bet; Gofman to Mossad; or dismissal of Baharav-Miara) and the Court intervenes (or in Zini's case, declines to).

The pattern across the appointment cases is itself worth noting:
- **Deri (2023)**: Court struck (10-1) based on plea-bargain representations and prior conviction
- **Zini (Dec 2025)**: Court declined (2-1), with the current Court President Amit in dissent
- **Gofman (May 2026)**: Court remanded (3-0, unanimous) on procedural grounds

The doctrinal grounds shift across these cases (reasonableness → conflict of interest → procedural review of the appointments committee), but the underlying conflict — the elected branch's preferred appointee versus the Court's view of what is allowable — remains constant.

## What the data shows together

Taking these patterns together, the documentary core supports several observations:

1. **Intervention is the default outcome** when the Court accepts a case challenging an elected-branch decision: 8 of 9 documented cases. The exception (Zini) is itself contested within the Court (Amit's dissent foreshadowed the unanimous Gofman ruling six months later, using similar logic).

2. **Reasonableness remains the operational core** of the Court's doctrinal toolkit, despite the 2023 attempt to amend it out of existence for cabinet-level decisions. The Court's 2024 striking of the amendment preserved its most-used doctrine.

3. **A small set of repeat petitioners** drives a disproportionate share of high-profile interventions. The Movement for Quality Government is the lead repeat-player; the Israeli Bar Association is a frequent co-petitioner.

4. **Appointments and structural decisions** are the most-contested category. The post-2022 period has produced an unusually dense cluster of Court interventions in appointment decisions specifically.

5. **The doctrinal mix expanded after January 2024**. Pre-2024 cases use reasonableness predominantly. Post-2024 cases see the introduction of "constituent authority limits" (HCJ 5658/23), procedural review (Gofman), and conflict-of-interest doctrines (Zini, Baharav-Miara) as new pillars of intervention.

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
- [Ran Hirschl, *Towards Juristocracy*](https://www.hup.harvard.edu/books/9780674025479) — the theoretical anchor, acknowledged in adversarial fairness; Hirschl's framework is critical-empirical rather than reform-prescriptive
- [Yehonatan Givati & Aharon Garber — empirical work on public confidence in the Supreme Court](https://en.idi.org.il/) (cited by Cohen-Eliya; primary paper to be located)
- See also the explainers in `../explainers/`
