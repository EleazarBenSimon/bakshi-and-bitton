# Moderation

This document defines the moderation framework for Bakshi&Bitton: who has authority, what they can do, how decisions are made, how appeals work, and how the project remains accountable to its own standards.

## Why moderation is structural, not optional

This project's integrity rests on whether participants hold to the standards in [MISSION.md](MISSION.md), [METHODOLOGY.md](METHODOLOGY.md), and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Those documents are aspirational on their own; moderation makes them operational.

Without active moderation:
- The methodology degrades, as contributors smuggle in editorial language
- The code of conduct becomes performative, as the worst impulses of the audience are tolerated
- The project's credibility collapses, as it becomes indistinguishable from any other partisan platform

With active moderation, the project remains what it claims to be.

## Moderator roles

### Maintainer

The project's maintainer is currently **@EleazarBenSimon**, and will remain so until the project is adopted by an institutional umbrella willing to honor the mission and methodology described in [MISSION.md](MISSION.md).

The maintainer's authority is final on:
- Methodology changes (subject to the procedure in METHODOLOGY.md §12)
- Code of Conduct changes (subject to a parallel procedure)
- Moderator appointments and removals
- Appeals of moderator decisions

### Moderators

Additional moderators may be appointed as the project grows. Moderator candidates must:

- Demonstrate sustained understanding of the project's methodology
- Have a documented track record of disciplined contribution (essays, documentary additions, methodology improvements)
- Accept the mission, methodology, and code of conduct in full
- Commit to deciding moderation questions on evidence-and-standard grounds, not political alignment

Moderators have authority within their assigned domain (documentary review, content review, code-of-conduct enforcement) — but cannot unilaterally change methodology or code of conduct, and their decisions are subject to maintainer review on appeal.

## What moderators do

### Documentary contributions (new rulings or corrections)

For each pull request adding or modifying a ruling in `data/`:

1. **Schema validation** (automated, CI-enforced) — the entry must pass JSON Schema validation
2. **Scope check** — does it meet the criteria in METHODOLOGY §2?
3. **Source verification** — is `official_url` valid and authoritative?
4. **Summary check** — do `summary_he` and `summary_en` pass the wire-service test in METHODOLOGY §5?
5. **No-characterization check** — does any field characterize a justice's motives, ideology, or bias?

If any check fails, the PR is rejected with a specific reason. The contributor may revise and resubmit.

### Informative content contributions (essays, pattern documents)

For each pull request adding or modifying content in `content/`:

1. **Source-link audit** — is every factual claim linked to a source per METHODOLOGY §6(a)?
2. **No-characterization check** — does the piece make claims about motives or alleged conduct beyond what sources support? (METHODOLOGY §6(b))
3. **Language review** — does the piece use inflammatory language per METHODOLOGY §6(c) or CODE_OF_CONDUCT §3?
4. **Pattern verification** — are quantitative claims empirically supported by cited rulings? (METHODOLOGY §6(d))
5. **Adversarial fairness** — are opposing positions engaged in their strongest form? (METHODOLOGY §6(e))
6. **Contributor identification** — is the piece attributed? (METHODOLOGY §6(f))
7. **Mission alignment** — does the piece serve the project's documented purpose, or does it use the project as a vehicle for some adjacent agenda? (CODE_OF_CONDUCT §7)

A failed check on any of these means the PR is rejected. Some checks (1, 5, 6) are objective and can be fixed by revision. Others (2, 3, 7) may indicate fundamental incompatibility and result in non-acceptance even with revision.

### Conduct enforcement

For reports of conduct violations or for content that visibly breaches the code:

1. **Immediate triage** — is this an active harm (e.g., harassment in progress, doxxing, threat) requiring immediate removal?
2. **Investigation** — gather context, review the content in question, talk to the parties if appropriate
3. **Decision** — remove content / restrict participant / ban participant / no action, with a written reason
4. **Notification** — inform the affected parties of the decision and the reasoning
5. **Documentation** — log the action in a moderation log (private to moderators, available on appeal)

## Standards for moderator decisions

Moderators decide on **evidence and standards**, not on political alignment or factional preference. Specifically:

- A contributor whose politics align with the project's mission is held to **exactly the same standards** as one whose politics oppose it
- A contribution that supports the project's broader argument is held to the same source-linking discipline as one that contradicts it
- A complaint from a sympathetic audience member is treated with the same skepticism and the same seriousness as a complaint from a critical one
- Moderator decisions are documented with their reasoning, so the standard applied is visible and accountable

The most common moderation failure is letting in-group contributions slide on standards. The project's credibility — and ultimately its effectiveness — depends on resisting this.

## Appeals

Any moderator decision can be appealed. The process:

1. Submit appeal to the maintainer via the email contact in [SECURITY.md](SECURITY.md), including:
   - The specific decision being appealed
   - The basis for the appeal (factual error, standard misapplication, etc.)
   - Any supporting evidence or context

2. The maintainer reviews within 14 days

3. Appeal outcome is one of:
   - **Original decision affirmed** — with written reasoning
   - **Original decision overturned** — with written reasoning; the moderator who made the original decision is informed
   - **Decision modified** — partial reversal with written reasoning
   - **Methodology question identified** — the appeal raises a question that requires a methodology change; the appeal is held pending the change procedure

4. The maintainer's decision is **final** on the specific appeal, but does not preclude future appeals on different facts or under updated methodology

## Maintainer accountability

The maintainer is not exempt from the standards described in this project's documents. Specifically:

- The maintainer's own contributions are subject to the same methodology, code of conduct, and moderation review as any other contributor's
- The maintainer may delegate moderation decisions to other moderators and is bound by their decisions when not overturned on appeal
- The maintainer's decisions are documented and may be reviewed by future maintainers or by an institutional umbrella that adopts the project

If the project is adopted by an institutional umbrella (e.g., Masad HaAretz), the institutional structure replaces the individual-maintainer model, with the same standards and the same appeal procedures applied through institutional decision-making.

## What moderators do NOT do

To prevent confusion about scope:

- Moderators do not adjudicate **factual disputes about ruling content** (those go to the source — supreme.court.gov.il — and are resolved by reference to the official text)
- Moderators do not adjudicate **political disagreements** about whether the project's broader argument is correct (those happen in the public sphere; the project's job is to document, not to win arguments)
- Moderators do not act as **legal counsel** (consult [METHODOLOGY.md §10](METHODOLOGY.md) for the legal-defense posture, and seek qualified counsel for actual legal matters)
- Moderators do not act as **journalists** (this is a documentary and educational resource, not a news organization)

## Current state (V0)

As of V0, the project has **one moderator: @EleazarBenSimon, who is also the maintainer**. The mission, methodology, and code of conduct are in place; the moderation framework is documented; but the volume of contributions does not yet require additional moderators.

Additional moderators will be appointed as:
- The project goes public
- Contribution volume exceeds the maintainer's single-handed review capacity
- Trusted contributors emerge from sustained, disciplined participation

The selection criteria and process for future moderator appointments are described in this document and will be applied transparently.

## How to become a moderator

The project does not solicit moderator applications. Moderator appointments are by invitation only, based on:

- Sustained, disciplined contribution history (documentary entries, informative content, or methodology improvements)
- Documented willingness to apply standards independent of political alignment
- Acceptance of the project's mission, methodology, and code of conduct in full

If you believe you would be a strong moderator and have a contribution history that supports it, you may contact the maintainer via [SECURITY.md](SECURITY.md). The maintainer is under no obligation to extend an invitation.
