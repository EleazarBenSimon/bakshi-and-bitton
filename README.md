# Court Observatory (מצפה המשפט)

A public, data-driven monitor of recent Israeli Supreme Court (HCJ) rulings that intervene in government decisions and appointments.

**Status**: V0 — pre-launch, building seed dataset.

## What this project is

A structured, source-linked dataset of Israeli Supreme Court rulings on government decisions and appointments. For each ruling we record: case identifier, date, panel composition, petitioner, government decision being challenged, legal doctrine invoked, outcome, vote split, and a link to the official ruling on supreme.court.gov.il.

## What this project is NOT

- **It is not advocacy.** We publish data. We do not editorialize, characterize, or take positions.
- **It does not assess justices' motives or character.** Vote records and authorship are facts. No "ideology" or "bias" field.
- **It does not paraphrase or replace official sources.** Every claim links to the official ruling text.

The political conversation about these rulings happens elsewhere. This project provides the data layer underneath that conversation.

## Scope (V0)

- Israeli Supreme Court rulings only (not lower courts, not administrative appeals unless heard by the Supreme Court)
- Final judgments only (not interim orders)
- Cases where petitioners challenged a government decision or appointment
- Last 24 months by default; selected earlier rulings included for historical context

V0 ships with ~9 hand-curated, news-grade rulings. V1 (post-adoption) expands the dataset.

## How to read the data

- `data/rulings/<case-id>.json` — one file per ruling, conforming to `schemas/ruling.schema.json`
- `data/justices/<slug>.json` — derived: each justice's record across the ruling set
- All facts in the dataset link to `official_url` at supreme.court.gov.il (or to authoritative secondary sources where the Court's own site lacks an English page)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Pull requests adding new rulings are reviewed against the methodology in [METHODOLOGY.md](METHODOLOGY.md). Anyone can contribute. Not every contribution will be accepted — the methodology gate is strict.

## License

MIT. See [LICENSE](LICENSE).

## Disclaimer

**This project is not a legal source.** Every entry links to the official Israeli Supreme Court ruling at [supreme.court.gov.il](https://supreme.court.gov.il), which is the authoritative text. The structured data here is a research and journalism aid; for any legal use, consult the official ruling text and a qualified Israeli attorney.

## Languages

Hebrew (RTL) is the primary interface language. English is provided in parallel for international citation and academic use.

## Attribution

If you cite this dataset in research, journalism, or commentary, please link to the project URL and cite the specific ruling's `case_id` field. The dataset is a public good; we ask only for traceability.
