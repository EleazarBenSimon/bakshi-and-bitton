---
title: The Reasonableness Doctrine (עילת הסבירות)
contributor: "@EleazarBenSimon"
date: 2026-05-23
summary: What "reasonableness" means as a ground for judicial review of executive decisions, how the doctrine expanded under Aharon Barak, and why it became the central battleground of the 2023 reform.
---

# The Reasonableness Doctrine (עילת הסבירות)

## What it is

"Reasonableness" is a ground for judicial review of administrative and executive decisions. A court applying the reasonableness doctrine asks: did the decision-maker — a minister, a cabinet, an agency head — choose an option that any reasonable decision-maker could have chosen, given the facts and the law?

If the court answers "no," the decision can be struck down.

In its original, narrow form, the doctrine was the common-law **Wednesbury unreasonableness** standard, formulated in the 1948 English ruling [*Associated Provincial Picture Houses v. Wednesbury Corporation*](https://en.wikipedia.org/wiki/Associated_Provincial_Picture_Houses_Ltd_v_Wednesbury_Corp). Under that standard, a court intervenes only when an administrative decision is "so outrageous in its defiance of logic or accepted moral standards that no sensible person who had applied his mind to the question to be decided could have arrived at it." This is a high threshold; intervention is rare.

## How the doctrine expanded in Israel

Israeli administrative law adopted Wednesbury reasonableness from British common law in the early years of the state. Through the 1970s the standard was applied narrowly, in line with its British origin.

This changed substantially under the tenure of Justice Aharon Barak. Per Prof. Moshe Cohen-Eliya's account in [*Israel's Juristocracy*](https://lawliberty.org/israels-juristocracy/) (Law & Liberty, March 2024):

> "Barak essentially abandoned this test in the 1980s and instead crafted the 'balancing' version of reasonableness, in which judges exercise discretionary executive powers if they conclude that the government did not correctly weigh or 'balance' different factors or considerations."

The shift moved the doctrine from "is the decision crazy?" to "did the decision-maker properly balance the relevant considerations?" This is a fundamentally different question — and a substantially lower threshold for judicial intervention.

The expanded "balancing" doctrine became the most frequently used ground for striking down executive decisions in Israel.

## Empirical scope (the "16 cases" claim)

Cohen-Eliya, in the same essay, notes the empirical scope of how often the doctrine was actually used at the level of ministerial and cabinet decisions:

> "in the past decade the Supreme Court had intervened in only 16 ministerial or cabinet decisions due to their unreasonableness"

This figure is roughly corroborated by the [Israel Democracy Institute](https://en.idi.org.il/articles/52235), which writes that the Court has "struck down a mere 1.6 decisions a year based on this standard."

The smaller-than-expected number is a key part of the debate: critics of the doctrine argue it has had outsized cultural and structural effects (administrative officials self-censor, knowing review is possible) even where actual strikedowns are rare. Defenders argue the small number shows the Court applies the doctrine with restraint.

Examples of decade-window reasonableness rulings against ministerial or cabinet decisions are documented in this project's `data/rulings/` directory — see `8948-22-deri.json`, `5782-21-zilber.json`, `1892-14-acri-prison-space.json`, `3132-15-yesh-atid-litzman.json`.

## The 2023 amendment and the January 2024 strike-down

In July 2023, the Knesset enacted Amendment No. 3 to *Basic Law: The Judiciary*, adding §15(d1): courts shall not review the reasonableness of decisions of the government, the prime minister, or any other minister.

The amendment did not abolish the reasonableness doctrine for administrative bodies generally — it removed it specifically for the most powerful tier of executive actors (cabinet, PM, ministers).

In January 2024, the Supreme Court, sitting *en banc* as a 15-justice panel, struck down the amendment in [HCJ 5658/23](https://supremedecisions.court.gov.il/Home/Download?path=HebrewVerdicts%2F23%2F580%2F056%2Fv31&fileName=23056580.V31&type=2) by an 8-7 majority. The Court additionally held, by a separate 12-3 ruling, that it has authority in principle to review Basic Laws that exceed the Knesset's constituent authority. See `data/rulings/5658-23.json` for the full structured record.

## Why this is the central battleground

The reasonableness doctrine sits at the intersection of two fundamental questions about how Israeli democracy works:

1. **Who decides what executive officials can do?** The legislature (which writes the laws and confirms ministers) or the judiciary (which reviews the resulting decisions)?

2. **What is the threshold for judicial intervention?** A clearly-defined legal violation (high threshold, narrow scope) or the judge's view of whether the decision was properly balanced (lower threshold, much broader scope)?

The doctrinal expansion under Barak shifted the answers to both questions: judges decide what ministers can do; the threshold is a judicial assessment of balance rather than a clear legal violation.

The 2023 reform sought to reverse this, at least at the cabinet/PM/minister level. The 2024 Supreme Court ruling reversed the reversal.

## A note on adversarial fairness

Defenders of the expanded reasonableness doctrine make two main arguments. First, that Israel lacks the institutional checks present in other democracies — no second legislative chamber, no federalism, no entrenched written constitution — and so the Court's review role is structurally necessary as the "only real check" (a phrase used in the HCJ 5658/23 majority opinion). Second, that reasonableness fills gaps that other doctrines (proportionality, ultra vires) do not cover, particularly around appointments and discretionary administrative actions.

The counter-position — articulated by Cohen-Eliya, Bakshi, Koppel, and others — is that the expansion has no parallel in any other Western democracy; that it amounts to judicial substitution of judgment for the elected executive's; and that the doctrine's "balancing" form is so elastic that it cannot be defined or constrained in advance.

This explainer documents the doctrine and the debate; it does not adjudicate which position is correct.

## Further reading

- [Moshe Cohen-Eliya, "Israel's Juristocracy," *Law & Liberty* (March 2024)](https://lawliberty.org/israels-juristocracy/)
- [Israel Democracy Institute, "The Supreme Court Ruling on Canceling the Reasonableness Clause — Implications"](https://en.idi.org.il/articles/52235)
- [Israel Democracy Institute, "Doing Away with the Standard of Extreme Unreasonableness"](https://en.idi.org.il/articles/50000)
- [INSS, "The Supreme Court on the Reasonableness Standard"](https://www.inss.org.il/publication/reasonableness/)
- [Cohen-Eliya & Porat, "Red Lines for Israel's Constitutional Reforms" (ICONnect)](https://www.iconnectblog.com/red-lines-for-israels-constitutional-reforms/)
