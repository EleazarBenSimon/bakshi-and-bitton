# Repository Mirrors

This document describes the redundant-hosting setup for Bakshi&Bitton. Set up because political-content repositories can face coordinated reporting / takedown campaigns that suspend the primary host, even when nothing about the content violates policy.

**Status as of last update**: GitHub primary is active. Codeberg mirror is **not yet configured** — pending the maintainer's manual account creation.

## Primary host

- **GitHub** — `github.com/EleazarBenSimon/bakshi-and-bitton`
- **Visibility**: Private
- **Branch protection**: not enabled (free-plan blocked on private repos; will unlock if the repo is ever made public)
- **Issues**: disabled
- **Wiki**: disabled
- **Discussions**: disabled
- **Pages**: not configured (no public deployment yet)

## Secondary mirror — Codeberg (planned, not yet active)

**Codeberg** ([codeberg.org](https://codeberg.org)) is a Berlin-based nonprofit Git host running Forgejo. It is the recommended takedown-insurance mirror for politically-charged civic-tech projects because:

- EU-jurisdiction (Berlin), GDPR-native, anti-AI-training by default policy
- No corporate ownership; community-governed nonprofit (Codeberg e.V.)
- Free for private repos with no KYC, no payment method required
- Forgejo features parity-with-Gitea, including private repos, CI (Woodpecker), and Pages

### Steps the maintainer needs to do once (manually, in the alias Chrome profile)

1. **Visit** [codeberg.org](https://codeberg.org) in the alias Chrome profile (the one logged in as `eleazarbensimon@gmail.com`)
2. **Click "Register"** — use:
   - Username: `EleazarBenSimon` (or whatever Codeberg allows; aim for visual parity with the GitHub alias)
   - Email: `eleazarbensimon@gmail.com`
   - Password: something only stored in your password manager
3. **Verify the email** Codeberg sends
4. **Read and accept the** [Terms of Use](https://codeberg.org/Codeberg/org/src/branch/main/TermsOfUse.md). Codeberg's terms are stricter than GitHub's in some areas (anti-spam, no commercial paid services), looser in others (more privacy-respecting, no advertising)
5. **Create a new repository**:
   - Owner: your new Codeberg account
   - Name: `bakshi-and-bitton`
   - **Visibility: Private** (CRITICAL — must NOT be public; same rules as the GitHub repo)
   - Do NOT initialize with README / .gitignore / license (the existing repo content will be pushed)
6. **Generate an access token** at `codeberg.org/-/user/settings/applications`:
   - Token name: `bakshi-and-bitton-push`
   - Scopes: `write:repository` (minimum needed)
   - Copy the token value once — Codeberg shows it only on creation
7. **Store the token securely** (1Password, system keychain, or a `.env` file outside this repo). Do NOT commit it.

### After the account exists — wire up the second remote

Once the account and empty private repo exist on Codeberg, from your local clone of bakshi-and-bitton:

```bash
cd ~/court-observatory   # (or wherever the working dir is)

# Add Codeberg as a second remote
git remote add codeberg https://codeberg.org/EleazarBenSimon/bakshi-and-bitton.git

# First push (using token for auth):
# Codeberg expects username + token via HTTPS basic auth
git push codeberg main
# When prompted: username = EleazarBenSimon, password = the access token

# Verify both remotes:
git remote -v
# Should show:
#   origin   https://github.com/EleazarBenSimon/bakshi-and-bitton.git
#   codeberg https://codeberg.org/EleazarBenSimon/bakshi-and-bitton.git
```

### Routine pushing to both remotes

Two approaches — choose whichever feels cleaner:

**Approach A — explicit per push** (recommended; you see what you're doing):
```bash
git push origin main
git push codeberg main
```

**Approach B — single command via a push group**:
```bash
# One-time setup: configure origin to push to BOTH on `git push`
git remote set-url --add --push origin https://github.com/EleazarBenSimon/bakshi-and-bitton.git
git remote set-url --add --push origin https://codeberg.org/EleazarBenSimon/bakshi-and-bitton.git

# After this, `git push origin main` pushes to both.
# git remote -v will show the multi-push URLs.
```

Approach A is safer if you want different commits to land on different hosts; Approach B is faster for routine work.

## What stays IDENTICAL on both hosts

- All source files (this is the whole point of the mirror — Codeberg is exact-copy insurance)
- The MIT license
- The methodology and contributor docs
- All ruling JSON data
- All site assets

## What stays DIFFERENT (intentional)

- **Issues disabled on both** (currently — re-enable later when moderation bandwidth exists; same policy both sides)
- **Wiki disabled on both**
- **Pages**: GitHub Pages can be enabled later as primary public deployment; Codeberg Pages is the backup but should NOT be enabled until/unless GitHub Pages fails

## Privacy and identity-firewall reminders

- **The repo must remain PRIVATE on Codeberg** just as it is on GitHub. Codeberg's UI defaults to public when creating a repo via web form — pay attention to the visibility toggle
- **Only the alias identity (`Eleazar Ben Simon` / `eleazarbensimon@gmail.com`) ever commits to either host**
- **No KYC, no payment method, no Sponsors-equivalent** features should be enabled on Codeberg
- **Do not link the Codeberg account to any other identity** (e.g., social-login with Google would tie it to the alias Google account, which is fine; do NOT use a primary-identity Google account)
- **Codeberg has no equivalent of GitHub Sponsors**, but it does have a "Liberapay" link option — do not enable; do not accept tipping

## Verifying everything still works after Codeberg is added

After the mirror is set up, run a sanity check:

```bash
cd ~/court-observatory   # local working dir

# Make a trivial test change (or just check status)
git status

# Confirm both remotes exist
git remote -v

# Check Codeberg repo URL is reachable
curl -s -o /dev/null -w "%{http_code}\n" https://codeberg.org/EleazarBenSimon/bakshi-and-bitton
# Should return 200 (or 404 if Codeberg requires auth for private repo discovery — try with the token)
```

## When to use the mirror in practice

Three scenarios:

1. **Routine**: every commit goes to both. The mirror is silent insurance — you don't notice it's there.
2. **GitHub suspension or coordinated mass-reporting attack**: switch the project's outward branding to the Codeberg URL (update README badges, social posts, site footer). The site itself stays up if hosted on GitHub Pages temporarily, or pivot deployment to Codeberg Pages (15-min task).
3. **Long-term move off GitHub**: not currently planned, but if GitHub policy changes in ways that materially affect this project, Codeberg is the migration target.

## What NOT to do

- **Don't** make either repo public until both the legal-tech consultant agent and the github-policy-expert agent have done a fresh pre-publication review
- **Don't** enable GitHub Sponsors or Codeberg Liberapay
- **Don't** add cloud-platform integrations (Cloudflare, Netlify, Vercel, Fleek, Pinata) without re-running the firewall analysis — these require account creation and can introduce KYC surfaces
- **Don't** mirror to a third host before evaluating whether two mirrors is overkill (it usually is)

## Sources

- [Codeberg — official site](https://codeberg.org)
- [Codeberg Terms of Use](https://codeberg.org/Codeberg/org/src/branch/main/TermsOfUse.md)
- [Codeberg Pages documentation](https://docs.codeberg.org/codeberg-pages/)
- [Forgejo project (the software Codeberg runs on)](https://forgejo.org/)
- [Git remote multi-push documentation](https://git-scm.com/docs/git-remote)
