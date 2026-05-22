# Contributing

We welcome contributions of new ruling entries, corrections to existing entries, and improvements to the project's tooling and templates.

## Submitting a new ruling

1. **Verify scope** against [METHODOLOGY.md §1](METHODOLOGY.md). Most rulings don't qualify. That's intentional.
2. **Read at least one existing entry** under `data/rulings/` to see the field conventions in use.
3. **Create a new file** at `data/rulings/<case-id>.json` where `<case-id>` is a slug derived from the case number (e.g., `5658-23` for HCJ 5658/23).
4. **Populate every required field** per [schemas/ruling.schema.json](schemas/ruling.schema.json).
5. **Open a pull request** with:
   - The new file
   - A PR description listing source materials consulted (court PDF URL, news coverage URLs, academic commentary)
   - Confirmation that the entry satisfies METHODOLOGY §1-5

## Submitting a correction

**Issues are currently disabled on this repository.** To report a factual correction, either:

1. Open a pull request with the corrected field value and a source link in the PR description, OR
2. Email the maintainer per [SECURITY.md](SECURITY.md) describing the disputed field, the source supporting your proposed change, and the source the current entry relies on. If sources conflict, see METHODOLOGY §7.

## Style for the `summary_he` and `summary_en` fields

Read METHODOLOGY §4 carefully. The most common reason a PR gets rejected is editorial language in the summary. Examples:

❌ "In a controversial decision, the Court struck down the government's appointment of X to Y..."
✅ "The Court struck down the government's appointment of X to Y on grounds of [doctrine cited in the ruling]."

❌ "The Court properly recognized that..."
✅ "The Court held that..."

❌ "The Court's expansive interpretation of reasonableness..."
✅ "The Court applied the reasonableness doctrine to..."

When in doubt: write the summary the way a wire-service reporter would write the lede. No qualifiers, no adverbs about the ruling's character.

## Disputed and contested entries

If you believe an existing entry contains a disputed fact, please email the maintainer per [SECURITY.md](SECURITY.md) (Issues are currently disabled). In your email:

1. Describe the dispute and the field involved
2. Cite the conflicting sources
3. Suggest one of: (a) update the field with notes about the dispute, (b) remove the disputed fact and leave the field null, (c) keep the field as is

The maintainer will respond. Disputes about METHODOLOGY itself follow the procedure in METHODOLOGY §9.

## Code contributions

Site templates, the JSON schema, scripts, and tooling improvements are welcome via standard pull requests. Use TypeScript for new scripts. Prefer minimal dependencies; the project is intentionally low-stack.

## Code of conduct

Be precise. Be brief. Cite sources. Don't editorialize. Don't make claims you can't back up. Treat methodology violations as ordinary methodology violations, not as political acts.

The project's value depends entirely on its discipline. Contributors who can't maintain that discipline will see their PRs rejected. This is not personal; it's load-bearing.
