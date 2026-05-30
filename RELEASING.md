# Releasing & archival

## Continuous validation

Every push that touches `data/`, `content/`, `schemas/`, or the build scripts
runs `.github/workflows/validate.yml`:

- **`validate`** (blocking) — `scripts/validate.py` checks schema validity,
  slug/filename consistency, vote/panel consistency, author-slug references,
  and content/data drift (every `data/rulings/<slug>.json` link in the Reading
  layer must resolve). Then `scripts/build.py` runs as an end-to-end smoke test.
- **`link-check`** (non-blocking) — `scripts/check_links.py` pings each ruling's
  `official_url` and `secondary_urls` and reports any that are unreachable, so a
  rotted source link surfaces without failing the deploy.

## Citation

- `CITATION.cff` powers GitHub's "Cite this repository" button.
- The dataset is published as `site/_data/rulings.json` and
  `site/_data/rulings.csv` (a flat export for spreadsheets / pandas / R).

## Minting a DOI via Zenodo (one-time setup, then per-release)

`.zenodo.json` already holds the deposit metadata. To get a citable DOI:

1. Sign in to <https://zenodo.org> with the project's GitHub account
   (**@EleazarBenSimon**), go to **Account → GitHub**, and flip the
   `EleazarBenSimon/bakshi-and-bitton` repository switch **On**.
2. In GitHub, create a release: **Releases → Draft a new release**, tag e.g.
   `v1.0`, title it, publish.
3. Zenodo automatically archives that release and mints a DOI. Each new release
   gets a new version DOI plus a stable "all-versions" concept DOI.
4. Add the concept-DOI badge to `README.md` and the resolved citation to
   `cite.html` once issued.

Until the DOI exists, cite by URL (see `cite.html`).
