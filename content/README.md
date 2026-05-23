# Content Layer

This directory holds the project's **informative content layer** — the editorial material that connects individual rulings (in `../data/`) into the larger picture they form, and helps citizens understand what the documentary record cannot convey on its own.

This is Layer 2 in the project's two-layer structure. See [../METHODOLOGY.md](../METHODOLOGY.md) §1 for the structural relationship between layers, and §6 for the discipline that governs everything in this directory.

## Subdirectories

### `essays/`

**Long-form context essays.** Each essay focuses on a specific theme or period — e.g., the doctrinal evolution of "reasonableness" from 1980 to 2024, the post-Oct-7 acceleration of judicial-establishment interventions in security appointments, the historical arc from Bank Mizrahi (1995) to HCJ 5658/23 (2024).

Format: markdown, sourced inline, contributor-attributed, moderator-approved.

Target length: 1,500-4,000 words. Longer treatments should be split into a series of essays.

### `patterns/`

**Pattern documentation across multiple rulings.** A pattern document identifies a recurring structural feature of the documented dataset — e.g., "rulings where the Court strikes appointments on reasonableness grounds tend to share the following characteristics," or "the AG-court relationship in 2025-2026 follows this discernible cycle."

Format: markdown with quantitative claims linked to specific case-IDs in `../data/rulings/`. Every assertion must be empirically verifiable from the cited records.

Target length: 800-2,500 words. Patterns documents are denser than essays — more table-and-list, less narrative.

### `explainers/`

**Short explanatory pieces for specific terms, doctrines, or institutional structures.** What is the reasonableness doctrine? What does the Judicial Selection Committee do? What is the difference between a Basic Law and an ordinary law? What does "constituent authority" mean? These are reference pieces for citizens who encounter unfamiliar terminology while engaging with the documentary core.

Format: short markdown, 200-600 words, glossary-style, with links to authoritative sources for further reading.

Explainers are the gateway for new readers. They should be accurate, clear, and accessible without requiring prior legal training.

## Discipline rules (binding on all content in this directory)

Per [../METHODOLOGY.md](../METHODOLOGY.md) §6, every piece in this directory must satisfy:

1. **Inline source-linking** for every factual claim — to the documentary core (`../data/rulings/<case-id>.json` and `../data/justices/<slug>.json`) or to authoritative external sources
2. **No characterization of justices' motives, ideology, alleged bias, or alleged corruption** — pattern observations about voting records and authorship are legitimate; psychoanalysis is not
3. **No inflammatory language** — see CODE_OF_CONDUCT.md §3
4. **Empirical verifiability of quantitative claims** — "N rulings on doctrine X in years Y-Z" requires the N rulings to be cited
5. **Adversarial good faith** — opposing positions are engaged in their strongest form, accurately attributed
6. **Contributor attribution** — each piece is signed (with a contributor identifier and date); anonymous contributions are not accepted in this directory

## Adding content

See [../CONTRIBUTING.md](../CONTRIBUTING.md) for the pull request workflow.

Briefly:
1. Place your file under the appropriate subdirectory (`essays/`, `patterns/`, or `explainers/`)
2. Name files in `kebab-case-with-date.md` (e.g., `reasonableness-doctrine-evolution-2024-01.md`)
3. Add a header block with:
   - Title
   - Contributor identifier
   - Date written
   - One-line summary
   - Cross-references to relevant `data/rulings/<case-id>.json` entries
4. Open a pull request; a moderator will review against the discipline rules
5. Moderator approval is required before merge — see [../MODERATION.md](../MODERATION.md)

## What this directory is NOT for

- **Opinion pieces** that are not source-linked
- **Personal commentary** on specific judges, attorneys, or officials
- **Polemical writing** that uses inflammatory language
- **Political-campaign material** for any party, faction, or candidate
- **News-style coverage** of breaking events (the project is documentary; it does not cover active proceedings)
- **Speculation** about motives, intentions, or alleged misconduct that is not source-supportable

Contributions that fall into any of these categories will be rejected by moderators regardless of factual accuracy or political appeal.

## Current state

As of V0, this directory is **empty of essays, patterns, and explainers** — the project is preparing to launch and the content layer will be populated after the documentary core is stable and the moderation framework is operational.

The first content additions are expected to be a few short **explainers** (covering reasonableness, the Judicial Selection Committee, constituent authority, and the role of the Attorney General). Essays and pattern documents come later.

If you want to contribute, follow [CONTRIBUTING.md](../CONTRIBUTING.md). Read [METHODOLOGY.md](../METHODOLOGY.md) §6 carefully first.
