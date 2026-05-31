# Bakshi&Bitton

**Live site:** https://eleazarbensimon.github.io/bakshi-and-bitton/

A documentary preservation project of the ongoing process by which the Israeli Supreme Court has been deformed from a guardian of law into an instrument that constrains the elected institutions of the State of Israel against the will of the public.

**Status**: V0 — pre-launch, building documentary core and informative content layer.

## What this project is

A two-layer resource for Israeli citizens, journalists, advocacy organizations, and public-policy actors:

**Layer 1 — Documentary core.** Every ruling of the Israeli Supreme Court that intervenes in a government decision or appointment is recorded with full procedural metadata: case identifier, panel composition, doctrine invoked, vote breakdown, outcome. Every claim is linked to the official judgment on supreme.court.gov.il. This is the verifiable factual foundation.

**Layer 2 — Informative content.** Context essays, pattern documentation, and explanatory material that connect individual rulings into the larger picture they form together — and help citizens see what the official documents alone cannot show. This layer is moderator-reviewed; every editorial claim must trace back to the documentary layer or to other authoritative sources.

Together these layers serve **public awareness**: enabling citizens to see, understand, and respond to the ongoing distortion of constitutional balance in Israel.

## What this project is NOT

This is not a platform for any of the following, and all such uses will be removed by moderators:

- **Humiliation** of any person — including judges, attorneys, public officials, parties to rulings, or fellow contributors
- **Incitement** to action against any person or group
- **Inappropriate language** — vulgarity, slurs, dehumanizing framings
- **Acts of revenge** or settling of personal scores
- **Spreading of lies** — any claim must be source-linked and verifiable
- **Calls for violence** in any form, against any target
- **Any purpose outside** the honest, disciplined effort to document distortions in the Israeli legal system and correct them through democratic means for the benefit of all citizens

These restrictions are not a polite suggestion — they are the project's defining boundary. The moderators have full authority to remove content and contributors who violate them.

## The foundational values

This project rests on, and exists to advance:

- **Truth** — every documented fact is verifiable; every framing is sourced
- **Justice** — restoration of proper constitutional balance, where elected institutions govern within the boundaries of the law and the law itself is determined by the consent of the governed
- **Morality** — the conduct of the project must reflect the principles it seeks to restore
- **Pursuit of justice for all citizens** — not the narrow interests of any political camp, but a sustainable peace and stability in which the State of Israel can serve all of its people

## How the data is structured

- `data/rulings/<case-id>.json` — one file per ruling, conforming to `schemas/ruling.schema.json`
- `data/justices/<slug>.json` — derived: each justice's record across the documented set
- `content/` — informative content layer (essays, pattern documents, explanatory material); moderator-reviewed
- All facts link to `official_url` on supreme.court.gov.il

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Both documentary additions (new rulings) and informative content additions (essays, pattern documents) are welcome from contributors who can accept the methodology and the moderation framework.

See [MODERATION.md](MODERATION.md) for moderator authority, review process, and standards.

See [METHODOLOGY.md](METHODOLOGY.md) for the project's factual discipline and legal posture.

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for participation standards.

See [MISSION.md](MISSION.md) for the project's full mission statement.

## License

MIT. See [LICENSE](LICENSE). The MIT license applies to code and structure; the documentary and informative content is a public resource for the purposes described above.

## Languages

Hebrew (RTL) is the primary interface language. English is provided in parallel for international citation, academic use, and diaspora access.

## Disclaimer

**This project is not a legal source.** Every entry links to the official Israeli Supreme Court ruling at [supreme.court.gov.il](https://supreme.court.gov.il), which is the authoritative text. The structured data and informative content here are a documentary and educational resource. For any legal use, consult the official ruling text and a qualified Israeli attorney.

## Attribution

If you cite this dataset or its informative content in research, journalism, or commentary, please link to the project URL and cite the specific entry or essay. We ask for traceability so claims can be verified at their source.
