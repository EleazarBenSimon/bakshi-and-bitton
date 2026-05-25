# Methodology: Power-Transfer Index

This document defines the **power-transfer index** that drives the
project's headline visualization (the cumulative curve on the home
page). It is a supplement to `METHODOLOGY.md` — the discipline rules
in that document continue to apply to all coding decisions made
under this framework. Where the two documents conflict, the general
methodology governs.

The index is the project's central interpretive instrument. Because
it is interpretive, its construction is documented in unusual detail:
every choice that could plausibly be challenged is named, justified
against the academic literature where possible, and made auditable
case-by-case in the underlying JSON records.

## 1. What the index measures

**The index counts acquisitions of decision-making competence by the
Supreme Court from elected institutions, weighted by the scope of
the acquisition, over time.**

It is not:

- a count of strike-downs (that would conflate normal review with
  unprecedented assertions of power)
- a measure of disposition severity (the previous draft of the chart
  did this; user feedback correctly identified it as the wrong
  unit)
- a measure of "intensity" or "activism" (subjective and unverifiable)

It is:

- a count of cases in which the Court asserted authority over a
  matter — at a level of generality and on a doctrine — it had not
  previously asserted authority over
- weighted such that a *new* assertion of competence counts more
  than the routine application of an established one
- separated into two sub-indices by **target branch** (executive vs.
  legislature), so the two distinct power transfers do not blur into
  a single number

## 2. Relationship to existing academic literature

A literature survey conducted for this project (see
`content/explainers/power-transfer-literature-review.md` — to be
authored) confirmed that no published framework cleanly measures the
quantity this project tracks. The closest analogues:

- **V-Dem `v2x_jucon`** (Judicial Constraints on the Executive)
  measures *constraint* on the executive, not *acquisition* by
  courts. Plotted as an external sanity-check overlay.
- **Linzer–Staton Latent Judicial Independence (LJI)** measures
  de-facto independence, not domain reach. Used as a second sanity
  check.
- **Brinks & Blass (2018), *The DNA of Constitutional Justice in
  Latin America*** is the closest methodological analogue. They
  code judicial authority on two axes — autonomy of judges and
  scope of authority. Our two-axis framework (target-branch ×
  domain) is directly adapted from theirs.
- **Stone Sweet** counts first-of-kind constitutional review actions
  per regime-year. Our "acquisition" coding category is operationally
  similar.
- **Hirschl, *Towards Juristocracy*** provides the theoretical frame
  (hegemonic preservation) but no measurement protocol.
- **Weinshall (2024)** is the strongest extant empirical counter-
  weight to this project's substantive thesis: she distinguishes
  *intervention* (override) from *involvement* (process-insertion)
  and finds the ISC is "high involvement, low intervention." See §6
  for how we engage her framework.

We do not adopt any of these wholesale. We borrow coding logic from
Brinks-Blass and counting logic from Stone Sweet; we cite Hirschl
and Cohen-Eliya as theoretical context; we validate externally
against V-Dem and LJI; we explicitly address Weinshall.

## 3. The two axes

Every ruling that enters the documentary core is coded on two
axes in addition to the existing schema fields:

### 3.1 `target_branch`

Closed enum:

- `executive` — the petition challenged a decision of the
  government, a minister, the prime minister, a cabinet, the
  Attorney General, or any executive agency or appointee
- `legislature` — the petition challenged primary legislation
  enacted by the Knesset
- `basic_law` — the petition challenged a Basic Law amendment
  itself (a sub-category of legislature, broken out because the
  doctrinal stakes are categorically different — striking a
  Basic Law amendment is the most consequential power transfer
  imaginable)
- `mixed` — the petition substantively challenges decisions of
  more than one branch

Selection criterion: which branch's decision is the *operative*
target of the ruling. If the petition is nominally against a
ministerial decision but the ruling's substance is about the
constitutionality of the underlying statute, code as
`legislature`.

### 3.2 `domain`

Closed enum (versioned; additions require a new methodology
release). The current list, derived from the 21 rulings already
in the documentary core:

- `religion-state` — mikvehs, conscription deferment for yeshiva
  students, public-sphere religious symbols, religious-state
  employment
- `asylum-immigration` — detention of asylum seekers,
  anti-infiltration legislation, residence-permit regimes
- `settlements-and-land` — expropriation, settlement
  regularization, land allocation in disputed territories
- `senior-executive-appointments` — Attorney General, Mossad
  chief, Shin Bet chief, IDF Chief of Staff, senior civil-service
  appointments
- `cabinet-composition` — ministerial qualifications,
  conflict-of-interest, coalition agreements, government
  formation
- `civil-tort-and-state-liability` — state immunity, civil-wrongs
  exemptions, compensation for civilian damage
- `privatization-of-sovereign-functions` — private prisons,
  outsourcing of coercive authority
- `conscription-and-equality` — Tal Law and successor statutes,
  draft deferments
- `economic-regulation` — gas frameworks, regulatory commitments,
  industry-stability clauses
- `intelligence-and-security-appointments` — sub-category of
  senior-executive-appointments when the appointment is in the
  intelligence community
- `prison-conditions` — detention conditions, physical capacity
- `criminal-procedure` — protections during criminal proceedings
- `judicial-appointments` — Judicial Selection Committee
  composition, justice tenure
- `basic-law-amendment` — amendments to Basic Laws challenged in
  themselves (distinct from `target_branch=basic_law` which marks
  the petition's target; this `domain` value marks the *subject
  matter*)
- `administrative-review-general` — older or unclassified
  administrative-review cases that crystallized doctrine but
  weren't tied to a specific policy domain
- `local-government` — municipal and local-authority decisions

This list is closed. Adding a value requires a methodology version
increment, a moderator vote, and documentation of why no existing
value fits.

## 4. `competence_class`

Each ruling is coded into exactly one of four categories. This
field carries the index weight:

| value | meaning | weight |
|---|---|---|
| `acquisition` | First time the Court substantively reviewed/intervened in **this** (target_branch × domain) combination. The Court is reaching into territory previously outside its operative review surface. | **+3** |
| `extension` | Application of existing review power to a meaningfully different sub-domain or doctrinal frontier within an already-claimed (target_branch × domain) combination. Incremental growth. | **+1** |
| `application` | Routine application of settled doctrine to a familiar case type. The Court is operating within its already-established reach. | **0** |
| `ratification` | The petition was dismissed without expanding doctrine. The Court's existing reach is reaffirmed but not extended. Cataloged for transparency; does not contribute to the index. | **0** |

The weights are deliberately coarse. They are intended to convey
"there is a meaningful difference between a *first* reach and a
*hundredth* reach," not to encode fine-grained intensity
distinctions that the data does not support.

### 4.1 Coding criteria for `acquisition`

A coding of `acquisition` requires **three independent secondary
sources** documenting that no prior Israeli Supreme Court ruling
substantively reviewed the same (target_branch × domain)
combination. The sources must be cited in the ruling's `notes`
field.

If any contributor disputes an `acquisition` coding, the ruling is
demoted to `extension` pending moderator review.

### 4.2 Coding criteria for `extension`

Sub-domain novelty must be specific and named. "Same domain but
different doctrine invoked" alone is not sufficient — the doctrine
either materially extends the Court's reach within the domain, or
the case is `application`.

### 4.3 Coding criteria for `application` and `ratification`

These categories are the default. When in doubt, code as
`application`. The bar to claim `acquisition` or `extension` is
higher than the bar to claim `application`.

## 5. The cumulative index

The headline visualization is computed as:

```
index(t) = Σ weight(r) for all rulings r with ruling_date ≤ t
```

Plotted as two sub-curves — one for `target_branch=executive` and
one for `target_branch=legislature` (with `basic_law` and `mixed`
contributing to whichever component they primarily belong to,
documented per-ruling).

A *total* curve summing both sub-curves is offered as the headline,
but the sub-curves remain accessible (interactive toggle on the
chart).

## 6. Engagement with Weinshall (2024)

Weinshall's intervention-vs-involvement framework deserves direct
response because it is the strongest published rebuttal to this
project's substantive thesis. Three points:

1. **Definitional convenience.** Weinshall categorizes Court
   process-insertion as not-really-power-transfer. We disagree on
   principled grounds: when the Court inserts itself into a
   policy process, the standard a political actor must satisfy
   changes from "what serves my mandate" to "what survives
   judicial scrutiny." That is a competence transfer regardless of
   the formal disposition. The index reflects this by counting an
   acquisition whenever the Court reaches into a (branch × domain)
   combination, *regardless* of whether the disposition was a
   strike-down or a procedural intervention.

2. **Sample period.** Weinshall's dataset is 2010–2018. Our
   documentary core spans 1976–2026 and includes the 2006–2009
   first wave of statute strikes and the 2021–2026 Basic Law
   override era. Both eras are outside her window and both are
   load-bearing for the substantive thesis. We do not claim her
   finding within her window is wrong; we claim her window is too
   narrow to support inference about the larger phenomenon.

3. **Publication timing.** Weinshall's 2024 reframing appeared
   immediately after the Court actually overrode Knesset Basic
   Law amendments. The reframing has the effect of recategorizing
   most ISC behavior as not-really-overriding at the precise
   moment when an actual override occurred. We do not impute
   motive; we observe that the framework's features happen to be
   the features that would obtain if it were institutionally
   protective. Readers can judge.

The project's curve will be plotted alongside Weinshall's
intervention-count when her data is published in machine-readable
form, so readers can directly compare.

## 7. External validation

The power-transfer curve will be plotted alongside two external
sanity-check series:

- **V-Dem `v2x_jucon` for Israel**, 1948-present
  ([dataset](https://www.v-dem.net/data/the-v-dem-dataset/))
- **Linzer-Staton LJI for Israel**, 1948-2015 ([Harvard
  Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/L716E8))

Neither series measures what our index measures, but if our curve
diverges *wildly* from both, we have a credibility problem and
must explain why. If our curve tracks both reasonably plus shows
additional detail on the dimensions they don't capture
(acquisition, breadth, target-branch split), the contribution is
defensible.

## 8. Adversarial review

This methodology is open to public critique before any of its
codings become the visual face of the project. Specifically:

- The closed `domain` vocabulary and the `competence_class`
  thresholds will be posted as a draft to GitHub Issues for at
  least 14 days before the first index is published as the
  homepage chart.
- Each ruling's `competence_class` coding includes a
  three-source citation requirement (for `acquisition`) in the
  `notes` field.
- A separate `adversarial_view` field is added to the ruling
  schema, permitting (and where contested, requiring) a
  citation-supported counter-classification by another
  contributor.

The project's `MODERATION.md` workflow governs disputes about
codings.

## 9. What this methodology does and does not claim

### 9.1 What it does not claim

- It does **not** claim that every act of judicial review is
  illegitimate. The Court has core review functions that are
  uncontroversial. The index registers expansions of those
  functions, not their existence.
- It does **not** claim that the Court's expansions are corrupt or
  done in bad faith. The index is structural, not motivational.
- It does **not** claim to be the only or the best measure of
  judicial power. It claims to be a *defensible* measure of one
  specific dimension — competence acquisition across (branch ×
  domain) cells over time.
- It does **not** claim that the underlying dispositions are
  illegitimate. A struck statute can be the right outcome on the
  merits *and* still represent a competence acquisition by the
  Court — these are independent questions.
- It does **not** claim that Israel is necessarily an outlier on
  the *volume* of judicial review compared to other democracies.
  Some democracies do have similarly active courts.

### 9.2 What it does claim — and the role of volume here

The index measures **competence acquired by the Court from
elected institutions over time**. Volume alone is institutional
design; democratic-authorization basis is legitimacy. **The
project's substantive concern is the conjunction of the two:**
substantial competence acquired *without* a corresponding act of
democratic authorization.

The Knesset is, in Israel's constitutional architecture, the
highest authority — and it derives that authority from the
electorate. Competence transferred from the Knesset (and from
Knesset-accountable executive actors) to the Court is therefore
competence transferred *away* from the chain of electoral
accountability. When such a transfer happens through Court-internal
interpretive moves rather than through a deliberate constitutional
founding moment, an explicit legislative grant, or a referendum,
that's the conjunction the project documents.

A country with high judicial-review volume whose review power was
explicitly granted by a constitutional convention or a referendum
is not making the same move. A country with moderate judicial-
review volume whose review power was self-asserted by the court is
making a smaller version of the same move. The relevant axis is
the *combination* — volume × (1 − authorization).

If a comparative panel is ever added to this project, it must
present both dimensions together. A panel that compared only the
volume axis would invite the misreading that the project is
upset about *amount* of judicial review rather than its
*authorization basis*. The current methodology version does not
publish such a panel for that reason.

## 10. Version

This is **methodology version 1.0** of the power-transfer index.
Future revisions will be tagged in the repository and any past
visualizations that depended on this version will be preserved as
historical artifacts so the index's evolution is itself auditable.

---

*See also:*
- `METHODOLOGY.md` — general project discipline (binding on all
  contributions)
- `MISSION.md` — project purpose
- `MODERATION.md` — dispute-resolution workflow
- `schemas/ruling.schema.json` — formal data shape
