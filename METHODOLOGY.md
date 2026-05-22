# Methodology

This document is the project's strongest defense. Every contribution must satisfy these rules. Contributions that fail any of them are rejected, even if factually accurate.

## 1. Scope rule

A ruling is in scope **if and only if**:

(a) it is an Israeli Supreme Court ruling (sitting as HCJ or as Court of Civil/Criminal Appeals, but only for the Supreme Court itself — not lower instances);

(b) it is a final judgment, not an interim order, injunction, or procedural ruling;

(c) the petitioner challenged a government decision or appointment (this includes ministerial decisions, cabinet resolutions, security-service appointments, and analogous executive actions);

(d) the ruling text is publicly published on supreme.court.gov.il (or an equivalent authoritative source where the Supreme Court's official portal lacks a record);

(e) the ruling falls within the last 24 months unless explicitly flagged as a historical-context entry.

No exceptions. If a ruling almost-fits but misses one criterion, it doesn't ship.

## 2. No interpretation in metadata

The `doctrine_invoked` field captures doctrines explicitly named in the ruling text — not what we, or commentators, or critics think the doctrine "really" was. If the ruling cites "reasonableness," we record "reasonableness." If the ruling does not name a doctrine, we leave the field empty rather than infer.

## 3. No characterization of justices

Vote records, authorship of opinions, panel composition, and biographical career milestones (year of appointment, prior positions) are facts.

We do not record ideology, lean, "activist vs. restrained," partisan identification, or any qualitative descriptor of any justice. If a future maintainer wants to add such fields, that constitutes a methodology change and requires a deliberate discussion.

## 4. Summaries are factual, not editorial

The `summary_he` and `summary_en` fields are one-to-two-sentence factual descriptions of what the ruling did. They state what the Court decided, not whether the decision was good, bad, controversial, or activist.

Test: if the summary wouldn't pass an editor at a wire service (Reuters, AP), it doesn't ship.

Words that should not appear in summaries:
- "controversial," "activist," "appropriate," "improper," "questionable," "shocking," "moderate," "extreme"
- "rightly," "wrongly," "correctly," "incorrectly"
- "as expected," "predictably," "surprisingly"

Words that may appear:
- "struck down," "upheld," "remanded," "voided," "modified"
- "majority," "minority," "dissented," "concurred"
- Procedural verbs of what the Court did

## 5. Every ruling links to the official source

The `official_url` field must point to either:

(a) The official PDF on supremedecisions.court.gov.il (preferred), or
(b) An equivalent authoritative archive (Versa / Cardozo for English translations, Wikimedia Commons for archived PDFs)

Removing the `official_url` field, replacing it with a paraphrase, or pointing it at commentary rather than the ruling text is grounds for rejecting the contribution.

## 6. Contributor process

A pull request adding a new ruling must:

1. Add one file under `data/rulings/<case-id>.json` matching `schemas/ruling.schema.json`
2. Include a non-summary `notes` section in the PR description identifying the source materials consulted
3. Pass the JSON schema validation (CI gate)

A reviewer (currently project maintainer, eventually any approved reviewer) checks the PR against rules 1-5 before merging. Anyone can submit a PR. Not every PR passes review.

## 7. Disputed facts

When sources conflict on a factual detail (panel composition, vote count, lead-author identity), record the detail that is supported by multiple independent sources and **note the discrepancy in the entry's `notes` field**. Do not record a single-source contested fact as if it were settled.

If no consensus exists, the entry doesn't ship in that field — leave it null.

## 8. What we do not do

Things outside this project's scope, no matter how relevant they seem:

- **Live commentary or breaking news.** This is a structured-data project, not a news outlet. Updates lag formal rulings by days-to-weeks.
- **Analysis of legislative reforms.** That's a separate domain (legislative trackers exist; see Israel Policy Forum).
- **Comparison with foreign courts.** Out of V0 scope. The Bank Mizrahi / India / Brazil comparative work belongs in academic literature.
- **Recommendations.** This project does not advocate for any change in the law, court composition, or political outcomes. Period.

## 9. Methodology change procedure

Changing this methodology requires:

1. A pull request to METHODOLOGY.md with the proposed change
2. At least 7 days of public review window
3. An explicit accept by the project maintainer with a note explaining why the change preserves the project's data-only character

Methodology changes are not made silently or through ordinary commit history. They are the project's foundational covenant with users.
