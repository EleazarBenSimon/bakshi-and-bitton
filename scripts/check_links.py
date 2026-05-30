#!/usr/bin/env python3
"""
check_links.py — verify that each ruling's official_url and secondary_urls are
reachable. Source-link integrity is the project's core credibility claim ("we
link the primary source"), so a rotted link should be surfaced.

Non-blocking by design (run as continue-on-error in CI): transient network
failures and aggressive bot-blocking on government sites should warn, not fail.
Stdlib only.

Exit code: 0 always (informational). Prints a summary of unreachable URLs.
"""

import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RULINGS_DIR = REPO_ROOT / "data" / "rulings"
TIMEOUT = 20
UA = "Mozilla/5.0 (compatible; BakshiBitton-linkcheck/1.0; +https://eleazarbensimon.github.io/bakshi-and-bitton/)"


def reachable(url: str) -> tuple[bool, str]:
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                if 200 <= resp.status < 400:
                    return True, str(resp.status)
        except urllib.error.HTTPError as e:
            # Some servers reject HEAD (405) or bots (403) but the link is valid.
            if e.code in (403, 405, 429):
                if method == "GET":
                    return True, f"{e.code} (accepted — bot/method block)"
                continue
            return False, f"HTTP {e.code}"
        except Exception as e:  # noqa: BLE001 — informational tool
            if method == "GET":
                return False, type(e).__name__
            continue
    return False, "unreachable"


def main() -> int:
    files = sorted(RULINGS_DIR.glob("*.json"))
    checked = 0
    dead = []
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        urls = []
        if d.get("official_url"):
            urls.append(("official_url", d["official_url"]))
        for u in d.get("secondary_urls", []) or []:
            urls.append(("secondary", u))
        for kind, url in urls:
            checked += 1
            ok, detail = reachable(url)
            status = "✓" if ok else "✗"
            print(f"  {status} [{f.stem}] {kind}: {detail} — {url}")
            if not ok:
                dead.append((f.stem, kind, url, detail))

    print(f"\n{checked} URL(s) checked across {len(files)} rulings; "
          f"{len(dead)} unreachable.")
    if dead:
        print("\nUnreachable (review — source links are the project's credibility anchor):")
        for slug, kind, url, detail in dead:
            print(f"  - {slug} [{kind}] {detail}: {url}")
    return 0  # informational only


if __name__ == "__main__":
    sys.exit(main())
