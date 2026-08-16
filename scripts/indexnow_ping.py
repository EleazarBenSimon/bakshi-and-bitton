#!/usr/bin/env python3
"""Ping IndexNow (Bing/Yandex/etc.) with the site's URLs after a deploy.

Usage: python3 scripts/indexnow_ping.py [url ...]
With no arguments, submits every URL in the live sitemap.
The key file site/<KEY>.txt must be deployed before pinging.
"""
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET

HOST = "eleazarbensimon.github.io"
BASE = f"https://{HOST}/bakshi-and-bitton"
KEY = "5c4b1a7dc3ffae4edc42849517c1e86b"
KEY_LOCATION = f"{BASE}/{KEY}.txt"
SITEMAP = f"{BASE}/sitemap.xml"
ENDPOINT = "https://api.indexnow.org/indexnow"
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def sitemap_urls():
    with urllib.request.urlopen(SITEMAP) as resp:
        root = ET.fromstring(resp.read())
    return [el.text for el in root.iter(f"{SITEMAP_NS}loc")]


def main():
    urls = sys.argv[1:] or sitemap_urls()
    # IndexNow scopes permission to URLs under the key file's directory.
    urls = [u for u in urls if u.startswith(BASE)]
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"IndexNow: HTTP {resp.status} — submitted {len(urls)} URLs")
    except urllib.error.HTTPError as e:
        print(f"IndexNow: HTTP {e.code} {e.reason}")
        print(e.read().decode(errors="replace"))
        sys.exit(1)


if __name__ == "__main__":
    main()
