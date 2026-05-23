# Methodology

This document defines the discipline that makes Bakshi&Bitton credible, defensible, and useful. Every contributor must satisfy these rules. Contributions that fail any of them are rejected by the moderators — regardless of how compelling the underlying claim sounds or how much the contributor agrees with the project's broader mission.

## 1. Two-layer structure

The project has two distinct layers, each with its own discipline:

### Layer 1 — Documentary core (`data/`)

The structured factual record. Every ruling has: case identifier, date, panel composition, doctrine invoked, vote breakdown, outcome, official-source link. **This layer contains no interpretation, no characterization of motives, no qualitative assessment.** Only documented procedural facts.

The documentary core is the project's foundation. Everything above it depends on its integrity.

### Layer 2 — Informative content (`content/`)

The editorial layer: context essays, pattern documents, explainers, timelines that connect individual rulings into the larger picture they form. This layer is **moderator-reviewed** and **source-linked** — every claim above the factual layer must trace back either to the documentary core or to other authoritative sources.

The informative content layer is what enables awareness-raising — but it is the more exposed surface, both legally and credibility-wise. The methodology for this layer is therefore stricter than naive editorial writing.

## 2. Scope rule (Documentary core)

A ruling is in scope **if and only if**:

(a) it is an Israeli Supreme Court ruling (sitting as HCJ or as Court of Civil/Criminal Appeals, but only for the Supreme Court itself — not lower instances);

(b) it is a final judgment, not an interim order, injunction, or procedural ruling;

(c) the petitioner challenged a government decision or appointment (this includes ministerial decisions, cabinet resolutions, security-service appointments, and analogous executive actions);

(d) the ruling text is publicly published on supreme.court.gov.il (or an equivalent authoritative source where the Supreme Court's official portal lacks a record);

(e) the ruling falls within the last 24 months unless explicitly flagged as a historical-context entry.

No exceptions. If a ruling almost-fits but misses one criterion, it doesn't ship in the documentary core. It may still be referenced in the informative content layer with appropriate caveats.

## 3. No interpretation in documentary metadata

The `doctrine_invoked` field captures doctrines explicitly named in the ruling text — not what we, or commentators, or critics think the doctrine "really" was. If the ruling cites "reasonableness," we record "reasonableness." If the ruling does not name a doctrine, we leave the field empty rather than infer.

## 4. No characterization of justices anywhere in the project

Vote records, authorship of opinions, panel composition, and biographical career milestones (year of appointment, prior positions, public-record statements made in public roles) are facts. They appear in the documentary layer and may be cited in the informative content layer.

We do **not** record or write about: ideology, lean, "activist vs. restrained," partisan identification, alleged motives, alleged corruption, alleged bias, or any qualitative descriptor of any justice. This applies to both layers.

This is not because such characterizations are necessarily wrong. It is because:

1. They cannot be reliably verified against source material — they depend on access to information no contributor has
2. They convert a documentary project into a polemic, which collapses its credibility with the broader audience the mission requires
3. They expose the project to defamation liability without corresponding benefit
4. They invite contributors and readers to substitute opinion for evidence, which is the discipline this project exists to demonstrate the opposite of

The discipline is harder than it sounds. The reward is a project that survives scrutiny from skeptical readers — including readers who disagree with the project's broader framing.

## 5. Summaries are factual, not editorial (Documentary core)

The `summary_he` and `summary_en` fields are one-to-two-sentence factual descriptions of what the ruling did. They state what the Court decided, not whether the decision was good, bad, controversial, or activist.

Test: if the summary wouldn't pass an editor at a wire service (Reuters, AP), it doesn't ship.

Words that should not appear in documentary summaries:
- "controversial," "activist," "appropriate," "improper," "questionable," "shocking," "moderate," "extreme"
- "rightly," "wrongly," "correctly," "incorrectly"
- "as expected," "predictably," "surprisingly"

Words that may appear:
- "struck down," "upheld," "remanded," "voided," "modified"
- "majority," "minority," "dissented," "concurred"
- Procedural verbs of what the Court did

## 6. Informative content discipline (Layer 2)

Editorial content in `content/` operates under stricter, not looser, discipline than ordinary opinion writing. Specifically:

(a) **Every factual claim is source-linked.** Inline citations to the documentary core or to authoritative external sources. Not aggregate citations at the end — inline, at the point of each claim.

(b) **No claims about motives, character, or alleged corruption** of any individual — judge, attorney, official, petitioner, defendant. The content layer can describe what was done; it does not impute why it was done, except where the source material itself imputes a reason and is so cited.

(c) **No inflammatory language**, including but not limited to: dehumanizing descriptors, slurs, mockery, sarcastic framing, name-calling, or rhetorical devices that substitute heat for evidence.

(d) **Pattern observations must be empirically verifiable**: if an essay claims "X has happened N times in the past M years," the N rulings underlying that claim must be cited explicitly. If the count is approximate, the essay must say "approximately N" and explain how it was derived.

(e) **Adversarial sources are engaged in good faith**: if a piece quotes or paraphrases a position from a perspective the project disagrees with, it does so accurately, identifies the source, and engages the strongest form of the position rather than a strawman.

(f) **Each informative-content piece carries the contributor's identifier**, the moderator who approved it, and the date of last review. Anonymous contributions are not accepted for the content layer.

## 7. Every ruling links to the official source

The `official_url` field must point to either:

(a) The official PDF on supremedecisions.court.gov.il (preferred), or
(b) An equivalent authoritative archive (Versa / Cardozo for English translations, Wikimedia Commons for archived PDFs)

Removing the `official_url` field, replacing it with a paraphrase, or pointing it at commentary rather than the ruling text is grounds for rejecting the contribution.

## 8. Contributor process

Contributions follow two tracks depending on layer:

### Documentary contributions (a new ruling)

A pull request adding a new ruling must:

1. Add one file under `data/rulings/<case-id>.json` matching `schemas/ruling.schema.json`
2. Include a non-summary `notes` section in the PR description identifying the source materials consulted
3. Pass the JSON schema validation (CI gate)

A reviewer (moderator) checks the PR against rules 1-5 and 7 before merging.

### Informative content contributions (an essay or pattern document)

A pull request adding informative content must:

1. Place the file under `content/` in the appropriate subdirectory
2. Include the contributor's identifier in the file
3. Include inline source citations for every factual claim
4. Pass moderator review against rules 4 and 6 before merging

Documentary contributions are merge-eligible on factual correctness alone. Informative contributions require both factual correctness **and** moderator approval of the framing under §6. See [MODERATION.md](MODERATION.md) for the review process.

## 9. Disputed facts

When sources conflict on a factual detail (panel composition, vote count, lead-author identity), record the detail that is supported by multiple independent sources and **note the discrepancy in the entry's `notes` field**. Do not record a single-source contested fact as if it were settled.

If no consensus exists, the entry doesn't ship in that field — leave it null.

## 10. Legal posture

The project's discipline is also its primary legal defense. Under Israeli law, this project's published material rests on two well-established defenses to defamation claims:

- **Defamation Law, 1965, §15(2)** — publication of judicial proceedings and other public-record material. Every entry in the documentary core cites the official ruling text on supreme.court.gov.il. Where a fact about a ruling is included, the source is the ruling itself, not the project's characterization.

- **Defamation Law, 1965, §15(4)** — good-faith reporting on a matter of public concern, with reasonable care. The methodology rules in §1-9 of this document operationalize "reasonable care": scope discipline, no interpretation in documentary metadata, no characterization of justices, wire-service-grade summaries, source-linking discipline in the informative layer, and a moderator-review process that gates every entry.

This posture is not legal advice and does not replace consultation with a qualified Israeli attorney when one is needed. It is, however, the operational standard against which contributions are evaluated. Contributions that depart from this posture — by introducing characterization, opinion, or unverified claims — undermine the project's defense and will be rejected on those grounds alone.

Additional legal foundations:

- **Copyright Law, 2007, §6** — state-produced works including court rulings are not subject to copyright. Linking to and excerpting from rulings is unrestricted under Israeli copyright law.
- **Privacy Protection Law, 1981 (amended 2024, Amendment 13 effective 14 August 2025)** — the journalism, research, and public-information exceptions apply to the project's coverage of public officials acting in their public roles. Data-subject requests for correction can be submitted via the contact in [SECURITY.md](SECURITY.md) and via the channels described in [CONTRIBUTING.md](CONTRIBUTING.md).

## 11. What this methodology is FOR

This is not bureaucratic ritual. The methodology exists because:

- Without source-linking, the project becomes another voice shouting; with source-linking, it becomes evidence
- Without scope discipline, the project gets pulled into every adjacent controversy; with scope discipline, it remains a focused tool
- Without no-characterization, the project becomes a personal-attack platform; with no-characterization, it becomes a structural-pattern resource
- Without contributor review, the project's worst contributors define it; with contributor review, the maintainers and moderators do
- Without legal defense, the project gets shut down by its first lawsuit; with legal defense, it survives

Every methodology rule traces back to one of these structural needs. None of them is a polite preference.

## 12. Methodology change procedure

Changing this methodology requires:

1. A pull request to METHODOLOGY.md with the proposed change
2. At least 14 days of moderator and contributor review
3. Explicit accept by the project maintainer with a note explaining why the change preserves the documentary discipline AND serves the mission

Methodology changes are not made silently or through ordinary commit history. They are the project's foundational covenant with its users.

## 13. Anti-misuse provisions

This methodology document is paired with [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), which articulates the prohibited uses of this project — humiliation, incitement, inappropriate language, revenge, lies, calls for violence, or any purpose outside the honest documentary effort. Those provisions apply to all contributors and to all content. Moderators have full authority to remove contributions and contributors who breach them. See [MODERATION.md](MODERATION.md) for the moderator-authority framework.
