"""Tests for v2.4.0 GSC ghost-path detection:
junk-path filtering, Crawl Stats CSV ingestion, output formatting.
"""

import csv
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from gsc_pull import _looks_like_junk, parse_crawl_stats_csv, format_ghosts


# --- junk filtering -----------------------------------------------------------

def test_junk_filter_blocks_exploit_probes():
    """Scraper and exploit-probe paths must never become generated pages."""
    for p in [
        "/wp-admin/install.php",
        "/wp-login.php",
        "/.env",
        "/.git/config",
        "/phpmyadmin/index.php",
        "/vendor/phpunit/phpunit/eval-stdin.php",
        "/cgi-bin/test.cgi",
        "/feed",
    ]:
        assert _looks_like_junk(p), f"should be junk: {p}"


def test_junk_filter_blocks_malformed():
    assert _looks_like_junk("")
    assert _looks_like_junk(None)
    assert _looks_like_junk("/a" * 150)              # absurdly long
    assert _looks_like_junk("/a/b/c/d/e/f/g/h/i/j")  # too deeply nested


def test_junk_filter_allows_real_content_paths():
    for p in [
        "/airports/jfk",
        "/services/water-heater-repair-anaheim",
        "/guides/long-term-parking",
        "/locations/dallas/emergency-plumber",
    ]:
        assert not _looks_like_junk(p), f"should be allowed: {p}"


# --- Crawl Stats CSV ingestion ------------------------------------------------

def _write_csv(rows, header):
    f = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="", encoding="utf-8")
    w = csv.DictWriter(f, fieldnames=header)
    w.writeheader()
    for r in rows:
        w.writerow(r)
    f.close()
    return f.name


def test_csv_isolates_discovery_404s_only():
    path = _write_csv(
        [
            {"URL": "/ghost-page", "Purpose": "Discovery", "Response": "404"},
            {"URL": "/live-page", "Purpose": "Discovery", "Response": "200"},
            {"URL": "/refreshed", "Purpose": "Refresh", "Response": "404"},
            {"URL": "/wp-admin/x.php", "Purpose": "Discovery", "Response": "404"},
        ],
        ["URL", "Purpose", "Response"],
    )
    out = parse_crawl_stats_csv(path, "https://example.com")
    paths = [o["path"] for o in out]

    assert "/ghost-page" in paths           # Discovery + 404 -> kept
    assert "/live-page" not in paths        # 200 -> dropped
    assert "/refreshed" not in paths        # Refresh purpose -> dropped
    assert "/wp-admin/x.php" not in paths   # junk -> dropped
    assert out[0]["purpose"] == "Discovery"
    assert out[0]["source"] == "crawl-stats-csv"


def test_csv_handles_absolute_urls_and_alt_headers():
    path = _write_csv(
        [{"Page": "https://example.com/ghost", "Crawl purpose": "Discovery", "Status": "404 Not Found"}],
        ["Page", "Crawl purpose", "Status"],
    )
    out = parse_crawl_stats_csv(path, "https://example.com")
    assert len(out) == 1
    assert out[0]["url"] == "https://example.com/ghost"
    assert out[0]["path"] == "/ghost"


def test_csv_empty_returns_empty():
    path = _write_csv([], ["URL", "Purpose", "Response"])
    assert parse_crawl_stats_csv(path, "https://example.com") == []


# --- output formatting --------------------------------------------------------

def test_format_ghosts_empty():
    assert "none found" in format_ghosts([])


def test_format_ghosts_shows_action_and_guardrail():
    out = format_ghosts([
        {"path": "/ghost", "impressions": 42, "clicks": 0, "status": 404, "recommendation": "GENERATE"}
    ])
    assert "/ghost" in out
    assert "GENERATE" in out
    # The guardrail against mass-generating pages must always be printed
    assert "410" in out
    assert "Prune Protocol" in out


if __name__ == "__main__":
    test_junk_filter_blocks_exploit_probes()
    test_junk_filter_blocks_malformed()
    test_junk_filter_allows_real_content_paths()
    test_csv_isolates_discovery_404s_only()
    test_csv_handles_absolute_urls_and_alt_headers()
    test_csv_empty_returns_empty()
    test_format_ghosts_empty()
    test_format_ghosts_shows_action_and_guardrail()
    print("All tests passed.")
