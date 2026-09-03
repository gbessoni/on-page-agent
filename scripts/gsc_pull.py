#!/usr/bin/env python3
"""
SEO-AGI Google Search Console data puller.
Retrieves query performance data and detects cannibalization.

Usage:
    python3 gsc_pull.py "<site_url>" [options]

Options:
    --keyword=KEYWORD       Filter queries containing this keyword
    --days=N                Lookback period (default: 90)
    --min-impressions=N     Minimum impressions threshold (default: 10)
    --output=FORMAT         Output: json|compact (default: compact)
    --cannibalization       Run cannibalization detection for the keyword
    --ghost-paths           Find URLs Google surfaces that return 404 (v2.4.0)
    --crawl-stats-csv=PATH  Ingest a manual GSC Crawl Stats export and isolate
                            Discovery-purpose 404s (v2.4.0)

NOTE ON CRAWL STATS (v2.4.0):
    The "Crawl Stats > By purpose > Discovery" report is UI-only. Google does
    NOT expose it in the Search Console API (the API covers Search Analytics,
    Sites, Sitemaps, and URL Inspection only). So this script offers two paths:

      --ghost-paths          Automated. Queries Search Analytics for pages
                             earning impressions, then checks which return 404.
                             A URL Google surfaces but that does not resolve is
                             the highest-confidence ghost path available via API.

      --crawl-stats-csv      Manual. Export Crawl Stats from the GSC UI and pass
                             the CSV here to isolate literal Discovery 404s.

    GUARDRAIL: do not generate a page for every result. Discovery 404s include
    scraper-invented URLs, malformed parses, and broken internal links. A ghost
    path qualifies only if it has real demand behind it AND sits inside the
    site's topical circle. Everything else gets a 410, not a page.
"""

import sys
import os
import csv
import json
import argparse
import urllib.error
import urllib.request
from urllib.parse import urljoin, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.env import get_credentials
from lib.gsc_client import GSCClient

# Paths that are almost never worth generating a page for, even when Google
# crawls them. Substring match, lowercased.
_JUNK_PATH_MARKERS = (
    "wp-admin", "wp-login", "wp-content", "xmlrpc", ".env", ".git",
    "phpmyadmin", "/feed", "?replytocom", "/cgi-bin", ".php", "/trackback",
    "adminer", "/vendor/", "/node_modules/", "wp-includes",
)


def _looks_like_junk(path: str) -> bool:
    """True for scraper-invented, exploit-probe, or malformed paths that must
    never be turned into generated pages."""
    p = (path or "").lower()
    if not p:
        return True
    if any(marker in p for marker in _JUNK_PATH_MARKERS):
        return True
    # Absurdly long or deeply nested paths are almost always malformed
    if len(p) > 200 or p.count("/") > 8:
        return True
    return False


def _status_for(url: str, timeout: int = 12) -> int:
    """Return the HTTP status for a URL. 0 on connection failure."""
    req = urllib.request.Request(
        url, method="HEAD", headers={"User-Agent": "seo-agi/2.4.0 ghost-path-check"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def find_ghost_paths(client, site_url: str, days: int, limit: int = 200) -> list[dict]:
    """Find URLs that earn impressions in Search Analytics but return 404.

    This is the API-accessible proxy for the UI-only Crawl Stats Discovery
    report: a URL Google is actively surfacing that does not resolve is a
    demand signal with a broken destination.
    """
    rows = client.query_performance(
        site_url=site_url, keyword=None, days=days, min_impressions=1
    )

    seen: dict[str, dict] = {}
    for r in rows:
        page = r.get("page") or ""
        if not page:
            continue
        agg = seen.setdefault(page, {"page": page, "impressions": 0, "clicks": 0})
        agg["impressions"] += r.get("impressions", 0) or 0
        agg["clicks"] += r.get("clicks", 0) or 0

    candidates = sorted(seen.values(), key=lambda x: x["impressions"], reverse=True)[:limit]

    ghosts = []
    for c in candidates:
        path = urlparse(c["page"]).path
        if _looks_like_junk(path):
            continue
        status = _status_for(c["page"])
        if status in (404, 410):
            ghosts.append(
                {
                    "url": c["page"],
                    "path": path,
                    "status": status,
                    "impressions": c["impressions"],
                    "clicks": c["clicks"],
                    "recommendation": (
                        "GENERATE" if c["impressions"] >= 10 else "REVIEW"
                    ),
                }
            )
    return sorted(ghosts, key=lambda x: x["impressions"], reverse=True)


def parse_crawl_stats_csv(csv_path: str, site_url: str) -> list[dict]:
    """Ingest a manual GSC Crawl Stats export and isolate Discovery-purpose
    404s. Column names vary by export and locale, so match defensively."""
    out = []
    with open(os.path.expanduser(csv_path), newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            low = { (k or "").strip().lower(): (v or "").strip() for k, v in row.items() }
            purpose = low.get("purpose", "") or low.get("crawl purpose", "")
            response = low.get("response", "") or low.get("status", "")
            url = low.get("url", "") or low.get("page", "")
            if not url:
                continue
            if "discovery" not in purpose.lower():
                continue
            if "404" not in response and "not found" not in response.lower():
                continue
            full = url if url.startswith("http") else urljoin(site_url, url)
            path = urlparse(full).path
            if _looks_like_junk(path):
                continue
            out.append(
                {
                    "url": full,
                    "path": path,
                    "status": 404,
                    "source": "crawl-stats-csv",
                    "purpose": "Discovery",
                    "recommendation": "REVIEW",
                }
            )
    return out


def parse_args():
    parser = argparse.ArgumentParser(description="SEO-AGI GSC Pull")
    parser.add_argument("site_url", help="GSC site URL (e.g., https://example.com)")
    parser.add_argument("--keyword", default=None, help="Keyword filter")
    parser.add_argument("--days", type=int, default=90, help="Lookback days")
    parser.add_argument("--min-impressions", type=int, default=10, help="Min impressions")
    parser.add_argument("--output", choices=["json", "compact"], default="compact")
    parser.add_argument("--cannibalization", action="store_true", help="Detect cannibalization")
    parser.add_argument(
        "--ghost-paths",
        action="store_true",
        help="Find URLs earning impressions that return 404 (v2.4.0)",
    )
    parser.add_argument(
        "--crawl-stats-csv",
        default=None,
        help="Path to a manual GSC Crawl Stats export; isolates Discovery 404s (v2.4.0)",
    )
    return parser.parse_args()


def format_ghosts(ghosts: list[dict]) -> str:
    lines = ["# Ghost Paths (URLs Google expects that return 404)"]
    if not ghosts:
        lines.append("  none found")
        return "\n".join(lines)

    lines.append(
        f"{'Path':<52} {'Impr':>7} {'Clicks':>7} {'Status':>7}  Action"
    )
    lines.append("-" * 96)
    for g in ghosts[:50]:
        lines.append(
            f"{g['path'][:51]:<52} {g.get('impressions', 0):>7} "
            f"{g.get('clicks', 0):>7} {g.get('status', '?'):>7}  {g.get('recommendation', '')}"
        )
    lines.append("")
    lines.append("GENERATE = 10+ impressions, real demand, inside the topical circle.")
    lines.append("REVIEW   = confirm demand and topical fit before writing anything.")
    lines.append("Anything not qualifying gets a 410 per the Prune Protocol, not a page.")
    return "\n".join(lines)


def format_compact(data: list[dict], mode: str = "performance") -> str:
    lines = []

    if mode == "cannibalization":
        lines.append("# Cannibalization Report")
        for item in data:
            lines.append(f"\nQuery: {item['query']} ({item['page_count']} pages, {item['total_impressions']} impressions)")
            for page in item["pages"]:
                lines.append(f"  pos {page['position']}: {page['page']} ({page['clicks']} clicks, {page['ctr']}% CTR)")
    else:
        lines.append("# Query Performance")
        lines.append(f"{'Query':<40} {'Clicks':>7} {'Impr':>7} {'CTR':>7} {'Pos':>5} Page")
        lines.append("-" * 110)
        for row in data[:50]:
            lines.append(
                f"{row['query'][:39]:<40} {row['clicks']:>7} {row['impressions']:>7} "
                f"{row['ctr']:>6.1f}% {row['position']:>5.1f} {row['page'][:50]}"
            )

    return "\n".join(lines)


def main():
    args = parse_args()
    creds = get_credentials()

    if not creds["has_gsc"]:
        print("ERROR: Google Search Console credentials not found.", file=sys.stderr)
        print("Add GSC_SERVICE_ACCOUNT_PATH to ~/.config/seo-agi/.env", file=sys.stderr)
        sys.exit(1)

    client = GSCClient(credentials_path=creds["gsc_service_account_path"])

    if args.crawl_stats_csv:
        data = parse_crawl_stats_csv(args.crawl_stats_csv, args.site_url)
        print(json.dumps(data, indent=2) if args.output == "json" else format_ghosts(data))
        return

    if args.ghost_paths:
        data = find_ghost_paths(client, args.site_url, args.days)
        print(json.dumps(data, indent=2) if args.output == "json" else format_ghosts(data))
        return

    if args.cannibalization and args.keyword:
        data = client.detect_cannibalization(
            site_url=args.site_url,
            keyword=args.keyword,
            days=args.days,
        )
        if args.output == "json":
            print(json.dumps(data, indent=2))
        else:
            print(format_compact(data, mode="cannibalization"))
    else:
        data = client.query_performance(
            site_url=args.site_url,
            keyword=args.keyword,
            days=args.days,
            min_impressions=args.min_impressions,
        )
        if args.output == "json":
            print(json.dumps(data, indent=2))
        else:
            print(format_compact(data))


if __name__ == "__main__":
    main()
