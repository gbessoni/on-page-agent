#!/usr/bin/env python3
"""
seo-agi research orchestrator.
Pulls SERP data, keyword data, PAA questions, and competitor content analysis
into a single research.json file that feeds content generation.

Usage:
    python3 research.py "<keyword>" [options]

Options:
    --serp-depth=N       Number of SERP results to analyze (default: 10)
    --include-paa        Include People Also Ask extraction (default: true)
    --location=CODE      DataForSEO location code (default: 2840 = US)
    --language=CODE      Language code (default: en)
    --output=FORMAT      Output: json|compact|brief (default: compact)
    --save-dir=PATH      Save raw data (default: ~/.local/share/seo-agi/research/)
    --content-depth=N    Number of top results to parse for content (default: 5)
    --mock               Use fixture data instead of live API calls
"""

import sys
import os
import json
import re
import argparse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Add parent dir to path for lib imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.env import load_env, load_config, get_credentials, ensure_dirs
from lib.dataforseo import DataForSEOClient
from lib.massive import MassiveClient
from lib.serp_analyze import analyze_serp


# Minimal English stopword list. Kept inline -- avoiding NLTK / spaCy
# dependency. Covers function words, modal verbs, common copulas, and
# pronouns. Not exhaustive; goal is "filter the obvious noise."
_STOPWORDS = frozenset(
    """
    a about above after again against all am an and any are as at be because
    been before being below between both but by can cant cannot could couldnt
    did didnt do does doesnt doing dont down during each few for from further
    had hadnt has hasnt have havent having he hed hell hes her here heres hers
    herself him himself his how hows i id ill im ive if in into is isnt it its
    itself just lets like me more most mustnt my myself no nor not of off on
    once only or other ought our ours ourselves out over own same shant she
    shed shell shes should shouldnt so some such than that thats the their
    theirs them themselves then there theres these they theyd theyll theyre
    theyve this those through to too under until up very was wasnt we wed
    well were werent weve what whats when whens where wheres which while who
    whos whom why whys with wont would wouldnt you youd youll your youre yours
    yourself yourselves
    """.split()
)


def extract_meta_entities(serp_data: dict) -> list[str]:
    """Extract bolded query-matched entities from competitor SERP description
    snippets. These are the exact tokens Google's snippet generator chose as
    most relevant -- a stronger signal than body-content entity extraction.

    DataForSEO surfaces these in two ways:
      1. A `highlighted` list per organic result (preferred; pre-extracted)
      2. Inline <b>/<strong>/**...** tags in the description (some sources)
    We accept both. Output is deduped, lowercase, ordered by frequency.
    """
    organic = serp_data.get("organic", []) or []
    pattern = re.compile(
        r"<b>(.+?)</b>|<strong>(.+?)</strong>|\*\*(.+?)\*\*",
        re.IGNORECASE | re.DOTALL,
    )
    counter: Counter[str] = Counter()

    def _add(term: str) -> None:
        term = re.sub(r"\s+", " ", term).strip().lower()
        term = term.strip(".,;:!?\"'()[]{}<>")
        if 2 <= len(term) <= 80:
            counter[term] += 1

    for r in organic:
        # Source 1: pre-extracted highlighted phrases
        for phrase in r.get("highlighted") or []:
            if isinstance(phrase, str):
                _add(phrase)
        # Source 2: inline tags in description (fallback)
        desc = r.get("description") or ""
        for m in pattern.finditer(desc):
            term = m.group(1) or m.group(2) or m.group(3) or ""
            _add(term)
    # Most frequent first; ties keep insertion order
    return [t for t, _ in counter.most_common(15)]


def _tokenize(text: str) -> list[str]:
    """Lowercase word tokens, no punctuation, no stopwords, length >= 3."""
    text = re.sub(r"[^A-Za-z0-9\s'-]+", " ", text.lower())
    tokens = []
    for raw in text.split():
        # Drop leading/trailing apostrophes-hyphens, drop pure-numeric junk
        tok = raw.strip("'-")
        if len(tok) < 3:
            continue
        if tok in _STOPWORDS:
            continue
        if tok.isdigit():
            continue
        tokens.append(tok)
    return tokens


def extract_target_ngrams(content_data: list, top_n_competitors: int = 3, top_k: int = 5) -> dict:
    """Scan the body text of the top N ranking competitors and return the
    top K most frequent bigrams (2-word) and trigrams (3-word) phrases.

    Body text comes from each competitor's parsed `headings` (joined) plus,
    where available, the underlying topic primary_content -- which is what
    DataForSEOClient._extract_content already aggregates into word_count.
    Since we don't have raw body text in the parsed output, we use heading
    text as the canonical body proxy: headings carry the topic-load and are
    consistent across competitors. Future versions can extend this by
    plumbing primary_content through.
    """
    body_texts: list[str] = []
    for content in (content_data or [])[:top_n_competitors]:
        if not content:
            continue
        # Heading text (most signal-dense per token)
        headings = content.get("headings") or []
        body_texts.append(" ".join(h.split(": ", 1)[-1] for h in headings))
        # Page title is also high-signal
        title = content.get("title") or ""
        if title:
            body_texts.append(title)

    if not body_texts:
        return {"bigrams": [], "trigrams": []}

    tokens = _tokenize(" ".join(body_texts))
    if len(tokens) < 2:
        return {"bigrams": [], "trigrams": []}

    bigram_counts = Counter(
        " ".join(tokens[i : i + 2]) for i in range(len(tokens) - 1)
    )
    trigram_counts = Counter(
        " ".join(tokens[i : i + 3]) for i in range(len(tokens) - 2)
    )

    return {
        "bigrams": [
            {"phrase": p, "count": c} for p, c in bigram_counts.most_common(top_k)
        ],
        "trigrams": [
            {"phrase": p, "count": c} for p, c in trigram_counts.most_common(top_k)
        ],
    }


# v1.9.1: Generic-navigation anchor text that should NOT count as a
# semantic spoke. Lowercased substring match. Tuned for English-language
# commercial sites; extend if running on non-English SERPs.
_GENERIC_ANCHORS = frozenset(
    [
        "home", "homepage", "back to home", "back to top",
        "contact", "contact us", "contact me", "get in touch",
        "about", "about us", "about me", "our team", "our company",
        "privacy", "privacy policy", "terms", "terms of service",
        "terms and conditions", "tos", "legal", "disclaimer",
        "cookie policy", "cookies", "accessibility", "sitemap",
        "login", "log in", "sign in", "sign up", "register",
        "subscribe", "newsletter", "follow", "share",
        "menu", "search", "more", "read more", "learn more",
        "click here", "see more", "view more", "show more",
        "previous", "next", "back", "skip to content",
        "facebook", "twitter", "instagram", "linkedin", "youtube",
        "tiktok", "pinterest", "social media",
        "faq", "faqs", "help", "support", "customer service",
        "careers", "jobs", "press", "blog", "news",
        "español", "english", "language",
    ]
)


def _normalize_domain(url: str) -> str:
    """Bare-host extractor, scheme + path + www. stripped, lowercased."""
    s = url.strip().lower()
    if "://" in s:
        s = s.split("://", 1)[1]
    s = s.split("/", 1)[0]
    if s.startswith("www."):
        s = s[4:]
    return s


def _is_generic_anchor(text: str) -> bool:
    """True if anchor text is navigational/boilerplate rather than semantic."""
    t = (text or "").strip().lower()
    if not t or len(t) > 80:
        return True
    # Nested-markdown leakage: [![alt](img)](href) sometimes leaves an
    # anchor string starting with `!` or containing stray `[`/`]`.
    # These are broken anchors, not real spokes.
    if t.startswith("!") or "[" in t or "]" in t:
        return True
    if t in _GENERIC_ANCHORS:
        return True
    # Pure punctuation, single emoji, or arrow glyphs
    if not re.search(r"[a-z0-9]", t):
        return True
    # Trailing punctuation often matters; check stripped form too
    t_stripped = t.strip(".,;:!?\"'()[]{}<>->→»")
    if t_stripped in _GENERIC_ANCHORS:
        return True
    return False


def extract_missing_spokes(
    content_data: list,
    organic: list,
    top_n_competitors: int = 3,
    top_k: int = 20,
) -> list[dict]:
    """Mine internal-link anchors from the top N ranking competitors and
    return the most-mentioned semantic anchors as candidate missing spokes.

    For each of the top N competitor pages, walks `content.links`, keeps
    only same-domain (internal) links, drops generic navigation, and
    counts by lowercased anchor. The result is the client's build-order
    priority for filling the topical silo gap (v1.9.1 SKILL.md Section 12).
    """
    counter: Counter[str] = Counter()
    # Original-case representative for display
    display_form: dict[str, str] = {}

    for i, content in enumerate((content_data or [])[:top_n_competitors]):
        if not content:
            continue
        competitor_url = (organic[i] if i < len(organic) else {}).get("url", "")
        host = _normalize_domain(competitor_url) if competitor_url else ""
        if not host:
            continue
        for link in content.get("links", []) or []:
            anchor = (link.get("text") or "").strip()
            url = (link.get("url") or "").strip()
            if not anchor or not url:
                continue
            if _is_generic_anchor(anchor):
                continue
            link_host = _normalize_domain(url)
            # Empty host means relative URL -> internal by definition.
            # Otherwise must match the competitor's bare host.
            if link_host and link_host != host:
                continue
            key = anchor.lower()
            counter[key] += 1
            display_form.setdefault(key, anchor)

    return [
        {"anchor": display_form[k], "competitor_count": v}
        for k, v in counter.most_common(top_k)
    ]


# v2.0.0 -- Structural directives the writing agent must follow when it
# builds the page layout. research.py does not emit page HTML itself; it is
# the data layer, and the writing agent is the "content output builder."
# This block is that builder's formatting configuration: it tells the agent
# to wrap primary snippet answers in flat block containers (never bare <p>),
# cap DOM nesting depth, and pair entities in subheadings. See SKILL.md
# "NEW IN v2.0.0" and Sections 3 + 6.
STRUCTURAL_DIRECTIVES = {
    "snippet_answer_container": (
        "block-level structural wrapper (div.answer / blockquote / dl+dd / "
        "leading table row / RDFa-Microdata span block) -- NEVER a bare <p> tag"
    ),
    "anti_paragraph_rule": True,
    "max_dom_nesting_depth": 3,
    "subheading_entity_synergy": (
        "repeat the core entity + tightest semantic neighbors across H2/H3 "
        "subheadings; ban generic 'Overview' / 'Details' / 'More Info' headings"
    ),
    "two_gate_target": (
        "Gate 1 = retrieval-pool entry (relevance, entity coverage, "
        "crawler-visible flat structure); Gate 2 = selected-citation "
        "extraction (liftable block-level answer units)"
    ),
    "anti_nlp_stuffing": (
        "FORBIDDEN: force-repeating NLP entity/term lists (Surfer, Google "
        "NLP API, Clearscope) in body prose to hit a coverage/density score "
        "-- linked to ~25% de-indexation. Place entities structurally "
        "(headings, table cells, schema), never by repetition target."
    ),
    # v2.3.0 -- AI SEO correlation protocols
    "outbound_citations_min": 5,
    "outbound_citation_rule": (
        "REQUIRED: at least 5 descriptive outbound links to external "
        "authoritative sources (.gov, .edu, operating authority, primary "
        "research, published rate cards). Anchor text names the source or "
        "the fact, never a bare URL. Zero outbound links = severe citation "
        "penalty. Do NOT default to rel=nofollow: it has not preserved "
        "equity since 2009 and forfeits the editorial trust signal. Reserve "
        "nofollow/sponsored for paid, affiliate, or untrusted destinations."
    ),
    "strict_phrase_placement": (
        "Exact-match target keyword appears in EXACTLY two places: the Title "
        "tag and the H1. FORBIDDEN in H2/H3/H4, meta description, alt text, "
        "and as stuffed body repeats. Unconditional -- supersedes the retired "
        "competitor-ratio EMQ logic. Subheadings use entity names and natural "
        "question phrasing."
    ),
    "entity_fact_pairing": (
        "Every entity named in a chunk must be bound to at least one hard "
        "verifiable fact in that same chunk (time, place, cost, capacity, "
        "frequency, distance, date). An unpaired entity is a wasted retrieval "
        "slot. Prefer facts an engine cannot synthesize from the rest of the "
        "corpus. Tag numbers with {{VERIFY}}."
    ),
    "intent_divergence": (
        "If primary_intent is informational/global: STRIP sales CTAs, free-"
        "estimate offers, and award mentions (they demote AI citation rate). "
        "If the page is local service targeting Ask Maps: FEATURE local "
        "project counts, awards, certifications, and brand differentiators."
    ),
    "anti_boilerplate_linking": (
        "Internal links must be uniquely contextual to the chunk they sit in. "
        "FORBIDDEN: site-wide repetitive in-content link blocks -- boilerplate "
        "is stripped before retrieval. The Recommended Spoke Pages block is "
        "exempt only because it is derived per-page from missing_spokes; "
        "identical spoke lists across pages mean it has become boilerplate."
    ),
}

# Container tags that increase DOM nesting depth. HTML void elements never do.
_VOID_TAGS = frozenset(
    [
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    ]
)


def measure_dom_depth(html: str) -> int:
    """Maximum nesting depth of container tags in an HTML fragment.

    Pure, dependency-free, stack-based. Void elements (<br>, <img>, ...)
    and self-closing tags do not increase depth. Used to flag deeply
    nested competitor layouts during the v2.0.0 DOM-flattening audit.
    """
    if not html:
        return 0
    depth = 0
    max_depth = 0
    tag_re = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)\b[^>]*?(/?)>")
    for m in tag_re.finditer(html):
        closing, tag, selfclose = m.group(1), m.group(2).lower(), m.group(3)
        if closing:
            depth = max(0, depth - 1)
        elif selfclose or tag in _VOID_TAGS:
            continue
        else:
            depth += 1
            max_depth = max(max_depth, depth)
    return max_depth


def flag_deep_nesting(
    content_data: list,
    organic: list,
    top_n: int = 3,
    max_depth: int = 3,
) -> dict:
    """Flag top-N competitors whose rendered DOM exceeds the v2.0.0
    flattening target.

    Operates on raw HTML when a parser provides it (`content["raw_html"]`).
    DataForSEO content_parsing returns a topic tree and Massive returns
    markdown -- neither exposes raw HTML today -- so this reports
    `not_assessed` rather than fabricating a depth number. The analyzer is
    forward-compatible: the moment a parser supplies raw HTML, the flag
    activates with no further changes.
    """
    flagged = []
    assessed = 0
    for i, content in enumerate((content_data or [])[:top_n]):
        if not content:
            continue
        html = content.get("raw_html")
        if not html:
            continue
        assessed += 1
        depth = measure_dom_depth(html)
        if depth > max_depth:
            url = (organic[i] if i < len(organic) else {}).get("url", "")
            flagged.append({"url": url, "max_depth": depth})
    return {
        "target_max_depth": max_depth,
        "assessed_count": assessed,
        "flagged": flagged,
        "status": (
            "assessed"
            if assessed
            else "not_assessed (no raw HTML from current parsers)"
        ),
    }


def detect_secondary_intent(keyword: str, primary_intent: str, serp_data: dict) -> str:
    """Map secondary intent per the Orcas 1 dual-intent model. The primary
    intent answers 'what did the user type'. The secondary intent answers
    'what do they want to do next'. A page targeting 'best CRM 2026'
    (primary: commercial) usually has a transactional secondary (start
    free trial, book demo). A 'how to park at JFK' page (primary:
    informational) usually has a transactional secondary (reserve a spot).

    Heuristic: invert primary along the funnel.
        informational -> commercial    (compare options after learning)
        commercial    -> transactional (act after comparing)
        transactional -> navigational  (find the seller / brand)
        navigational  -> transactional (act once on the brand)
    Override based on SERP-feature signals when stronger evidence exists.
    """
    funnel_map = {
        "informational": "commercial",
        "commercial": "transactional",
        "transactional": "navigational",
        "navigational": "transactional",
    }
    secondary = funnel_map.get(primary_intent, "transactional")

    organic = serp_data.get("organic", []) or []
    titles_text = " ".join(
        (r.get("title") or "").lower() for r in organic[:5]
    )

    # Strong transactional override
    if any(s in titles_text for s in ["book", "reserve", "buy", "order", "shop", "checkout"]):
        secondary = "transactional"
    # Strong navigational override (lots of brand-domain hits in top 5)
    domains = [r.get("domain", "") for r in organic[:5]]
    if domains and len(set(domains)) <= 2:
        secondary = "navigational"

    return secondary


def parse_args():
    parser = argparse.ArgumentParser(description="SEO-AGI Research")
    parser.add_argument("keyword", help="Target keyword or topic")
    parser.add_argument(
        "--serp-depth", type=int, default=10, help="SERP depth"
    )
    parser.add_argument(
        "--content-depth",
        type=int,
        default=5,
        help="Number of competitors to parse content from",
    )
    parser.add_argument(
        "--location", type=int, default=None, help="Location code"
    )
    parser.add_argument(
        "--language", default=None, help="Language code"
    )
    parser.add_argument(
        "--output",
        choices=["json", "compact", "brief"],
        default="compact",
        help="Output format",
    )
    parser.add_argument(
        "--save-dir", default=None, help="Directory to save research data"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use fixture data (no API calls)",
    )
    parser.add_argument(
        "--differentiators",
        default=None,
        help=(
            "Comma-separated brand differentiators / USPs to enforce in the "
            "brief output (e.g. --differentiators='women-owned, 24/7 service, "
            "no hidden fees'). Pages built without explicit differentiators "
            "fail the v1.9.1 Brand Identity check."
        ),
    )
    parser.add_argument(
        "--affiliate-link",
        default=None,
        help=(
            "Affiliate destination URL. When set, flags the page as affiliate "
            "monetization and emits a COMPLIANT affiliate directive (disclosed "
            "rel='sponsored nofollow' CTAs + FTC disclosure). Never a JS "
            "redirect or cloak. (v2.2.0)"
        ),
    )
    return parser.parse_args()


def build_affiliate_block(affiliate_link: Optional[str]) -> dict:
    """Build the v2.2.0 affiliate monetization directive.

    Compliant-only: discloses the affiliate relationship and links with
    rel="sponsored nofollow". Explicitly forbids cloaking / sneaky
    redirects (serving the crawler informational HTML while JS-redirecting
    humans to an affiliate page) -- that violates Google spam policy and
    LLM crawler terms and triggers de-indexation. The human and the crawler
    read the same page.
    """
    link = (affiliate_link or "").strip()
    if not link:
        return {"mode": "none"}
    return {
        "mode": "affiliate",
        "affiliate_link": link,
        "cta_rel": "sponsored nofollow",
        "disclosure_required": True,
        "directive": (
            "Add visible, disclosed affiliate CTAs linking to the affiliate "
            "URL with rel=\"sponsored nofollow\". Place an FTC-style "
            "affiliate-disclosure line (16 CFR Part 255) above the fold. "
            "The crawler and the human read the SAME page."
        ),
        "forbidden": (
            "No <script>window.location.href=...</script>, no meta-refresh, "
            "no cloaking or crawler/user content divergence."
        ),
    }


def _parse_differentiators(raw: Optional[str]) -> list[str]:
    """Split comma-separated USPs, strip whitespace, drop empties.
    Returns an empty list when input is None or only whitespace."""
    if not raw:
        return []
    return [d.strip() for d in raw.split(",") if d.strip()]


def load_mock_data(keyword: str) -> dict:
    """Load fixture data for testing without API calls."""
    fixtures_dir = (
        Path(__file__).parent.parent / "fixtures"
    )

    serp_fixture = fixtures_dir / "serp_sample.json"
    keywords_fixture = fixtures_dir / "keywords_sample.json"

    serp_data = {"organic": [], "paa": [], "featured_snippet": None}
    related_kw = []

    if serp_fixture.exists():
        with open(serp_fixture) as f:
            serp_data = json.load(f)

    if keywords_fixture.exists():
        with open(keywords_fixture) as f:
            related_kw = json.load(f)

    return {
        "keyword": keyword,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "mock",
        "primary_intent": "commercial",
        "secondary_intent": "transactional",
        "meta_entities": [],
        "target_ngrams": {"bigrams": [], "trigrams": []},
        "differentiators": [],
        "missing_spokes": [],
        "structural_directives": STRUCTURAL_DIRECTIVES,
        "dom_nesting": {
            "target_max_depth": 3,
            "assessed_count": 0,
            "flagged": [],
            "status": "not_assessed (mock data)",
        },
        "affiliate": build_affiliate_block(getattr(args, "affiliate_link", None)),
        "serp": serp_data,
        "related_keywords": related_kw,
        "analysis": {
            "intent": "commercial",
            "word_count_stats": {
                "min": 800,
                "max": 3200,
                "median": 1800,
                "recommended_min": 1440,
                "recommended_max": 2340,
            },
            "paa_questions": serp_data.get("paa", []),
            "topic_frequency": [],
            "heading_patterns": {
                "avg_h2_count": 6,
                "avg_h3_count": 8,
                "median_h2_count": 5,
                "median_h3_count": 7,
            },
        },
    }


def run_research(args) -> dict:
    """Execute the full research pipeline."""
    creds = get_credentials()
    config = load_config()

    location = args.location or config["default_location"]
    language = args.language or config["default_language"]

    if args.mock:
        return load_mock_data(args.keyword)

    if not creds["has_dataforseo"]:
        print(
            "NO_DATAFORSEO_CREDS: DataForSEO credentials not found.",
            file=sys.stderr,
        )
        print(
            "Falling back to mock data. For live research, add credentials to "
            "~/.config/seo-agi/.env",
            file=sys.stderr,
        )
        print(
            "Or use Ahrefs/SEMRush MCP tools in Claude Code as alternative data sources.",
            file=sys.stderr,
        )
        # Return a skeleton that the agent can fill in via MCP tools or WebSearch
        return {
            "keyword": args.keyword,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "no-creds-fallback",
            "location": location,
            "language": language,
            "primary_intent": "unknown",
            "secondary_intent": "unknown",
            "meta_entities": [],
            "target_ngrams": {"bigrams": [], "trigrams": []},
            "differentiators": _parse_differentiators(getattr(args, "differentiators", None)),
            "missing_spokes": [],
            "structural_directives": STRUCTURAL_DIRECTIVES,
            "dom_nesting": {
                "target_max_depth": 3,
                "assessed_count": 0,
                "flagged": [],
                "status": "not_assessed (no-creds fallback)",
            },
            "affiliate": build_affiliate_block(getattr(args, "affiliate_link", None)),
            "serp": {"organic": [], "paa": [], "featured_snippet": None},
            "related_keywords": [],
            "analysis": {
                "keyword": args.keyword,
                "intent": "unknown",
                "word_count_stats": {},
                "paa_questions": [],
                "topic_frequency": [],
                "heading_patterns": {},
                "competitors_analyzed": 0,
                "total_organic_results": 0,
                "featured_snippet": None,
            },
            "_fallback_note": (
                "No DataForSEO credentials. Use Ahrefs MCP, SEMRush MCP, "
                "or WebSearch to gather competitive data manually."
            ),
        }

    client = DataForSEOClient(
        creds["dataforseo_login"], creds["dataforseo_password"]
    )

    # v1.9.0: Massive Web Render is the primary content parser when a
    # token is configured. It returns clean rendered markdown including
    # JS-loaded content, which DataForSEO's content_parsing/live misses.
    # Falls back to DataForSEO on a per-URL basis if Massive errors out
    # or returns empty, so a partial Massive outage doesn't break the run.
    # SERP results and keyword data still come from DataForSEO -- Massive's
    # /search endpoint only returns 'also-searched' suggestions, not
    # organic results.
    massive: Optional[MassiveClient] = (
        MassiveClient(creds["massive_api_token"])
        if creds.get("has_massive")
        else None
    )
    parsers_used: list[str] = []

    # Step 1: SERP results
    print(f"Fetching SERP for: {args.keyword}", file=sys.stderr)
    serp_data = client.serp_live(
        args.keyword, location, language, args.serp_depth
    )

    # Step 2: Related keywords
    print("Fetching related keywords...", file=sys.stderr)
    related_kw = client.related_keywords(args.keyword, location, language)

    # Step 3: Parse competitor content (top N). Massive first if available,
    # DataForSEO as per-URL fallback.
    content_data = []
    organic = serp_data.get("organic", [])
    parse_count = min(args.content_depth, len(organic))

    for i in range(parse_count):
        url = organic[i].get("url", "")
        if not url:
            content_data.append(None)
            continue

        primary = "massive" if massive else "dataforseo"
        print(
            f"Parsing content ({i+1}/{parse_count}, via {primary}): "
            f"{url[:70]}...",
            file=sys.stderr,
        )

        content: Optional[dict] = None
        if massive:
            content = massive.content_parse(url)
            if content and content.get("word_count", 0) > 0:
                parsers_used.append("massive")
            else:
                # Massive returned nothing usable; fall back per-URL.
                print(
                    f"  Massive empty/failed for {url[:60]}; "
                    f"falling back to DataForSEO",
                    file=sys.stderr,
                )
                content = client.content_parse(url)
                if content:
                    parsers_used.append("dataforseo-fallback")
        else:
            content = client.content_parse(url)
            if content:
                parsers_used.append("dataforseo")

        content_data.append(content)

        # Merge content data back into organic result
        if content:
            organic[i]["word_count"] = content.get("word_count", 0)
            organic[i]["headings"] = content.get("headings", [])

    # Step 4: Analyze
    print("Analyzing competitive landscape...", file=sys.stderr)
    analysis = analyze_serp(serp_data, content_data, args.keyword)

    # Step 5: v1.7.1 -- LLM Retrieval signals
    primary_intent = analysis.get("intent", "unknown")
    secondary_intent = detect_secondary_intent(args.keyword, primary_intent, serp_data)
    meta_entities = extract_meta_entities(serp_data)
    target_ngrams = extract_target_ngrams(content_data, top_n_competitors=3, top_k=5)

    # Step 6: v1.9.1 -- Brand & spoke signals
    differentiators = _parse_differentiators(getattr(args, "differentiators", None))
    missing_spokes = extract_missing_spokes(
        content_data, organic, top_n_competitors=3, top_k=20
    )

    # Step 7: v2.0.0 -- DOM flattening competitor audit
    dom_nesting = flag_deep_nesting(content_data, organic, top_n=3, max_depth=3)

    # Step 8: v2.2.0 -- compliant affiliate monetization directive
    affiliate = build_affiliate_block(getattr(args, "affiliate_link", None))

    # Assemble research output. Surface the new signals at top level for
    # easy brief consumption -- do not bury them inside `analysis`.
    content_parser_summary = (
        Counter(parsers_used) if parsers_used else Counter()
    )
    research = {
        "keyword": args.keyword,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "location": location,
        "language": language,
        "source": "dataforseo",
        "content_parsers": dict(content_parser_summary),
        "primary_intent": primary_intent,
        "secondary_intent": secondary_intent,
        "meta_entities": meta_entities,
        "target_ngrams": target_ngrams,
        "differentiators": differentiators,
        "missing_spokes": missing_spokes,
        "structural_directives": STRUCTURAL_DIRECTIVES,
        "dom_nesting": dom_nesting,
        "affiliate": affiliate,
        "serp": serp_data,
        "related_keywords": related_kw[:20],
        "analysis": analysis,
    }

    return research


def save_research(research: dict, save_dir: str = None):
    """Save research data to disk."""
    ensure_dirs()
    config = load_config()

    if save_dir:
        out_dir = Path(save_dir).expanduser()
    else:
        out_dir = Path.home() / ".local" / "share" / "seo-agi" / "research"

    out_dir.mkdir(parents=True, exist_ok=True)

    # Filename from keyword + date
    slug = (
        research["keyword"]
        .lower()
        .replace(" ", "-")
        .replace("/", "-")[:50]
    )
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{slug}-{date_str}.json"

    filepath = out_dir / filename
    with open(filepath, "w") as f:
        json.dump(research, f, indent=2)

    print(f"Research saved: {filepath}", file=sys.stderr)
    return str(filepath)


def format_compact(research: dict) -> str:
    """Format research as compact human-readable output."""
    lines = []
    kw = research["keyword"]
    analysis = research.get("analysis", {})
    serp = research.get("serp", {})
    organic = serp.get("organic", [])

    lines.append(f"# Research: {kw}")
    lines.append(
        f"Intent: primary={research.get('primary_intent', 'unknown')}, "
        f"secondary={research.get('secondary_intent', 'unknown')}"
    )

    # Word count
    wc = analysis.get("word_count_stats", {})
    if wc:
        lines.append(
            f"Competitor word count: {wc.get('min', '?')}-{wc.get('max', '?')} "
            f"(median: {wc.get('median', '?')})"
        )
        lines.append(
            f"Recommended range: {wc.get('recommended_min', '?')}-"
            f"{wc.get('recommended_max', '?')} words"
        )

    # Top results
    lines.append(f"\n## Top {len(organic)} Results")
    for r in organic[:10]:
        wc_str = (
            f" ({r.get('word_count', '?')} words)"
            if r.get("word_count")
            else ""
        )
        lines.append(f"  {r['position']}. {r['title']}{wc_str}")
        lines.append(f"     {r['url']}")

    # PAA
    paa = analysis.get("paa_questions", serp.get("paa", []))
    if paa:
        lines.append(f"\n## People Also Ask ({len(paa)})")
        for q in paa:
            lines.append(f"  - {q}")

    # Related keywords
    related = research.get("related_keywords", [])
    if related:
        lines.append(f"\n## Related Keywords (top 10)")
        for kw_data in related[:10]:
            lines.append(
                f"  - {kw_data['keyword']} "
                f"(vol: {kw_data['volume']}, "
                f"diff: {kw_data.get('difficulty', '?')})"
            )

    # Topics
    topics = analysis.get("topic_frequency", [])
    if topics:
        lines.append(f"\n## Common Topics Across Competitors")
        for t in topics[:15]:
            lines.append(
                f"  - {t['topic']} (in {t['competitor_count']} pages)"
            )

    # Heading patterns
    hp = analysis.get("heading_patterns", {})
    if hp:
        lines.append(f"\n## Heading Structure")
        lines.append(
            f"  Avg H2s: {hp.get('avg_h2_count', '?')}, "
            f"Avg H3s: {hp.get('avg_h3_count', '?')}"
        )

    # Meta entities (bolded SERP-snippet terms -- v1.7.1)
    meta_ents = research.get("meta_entities", [])
    if meta_ents:
        lines.append(f"\n## Meta Entities (bolded in competitor SERP snippets)")
        for ent in meta_ents[:10]:
            lines.append(f"  - {ent}")

    # Target n-grams (top 3 competitor body text -- v1.7.1)
    ngrams = research.get("target_ngrams", {}) or {}
    bigrams = ngrams.get("bigrams", [])
    trigrams = ngrams.get("trigrams", [])
    if bigrams or trigrams:
        lines.append(
            f"\n## Target N-grams (seed 2+ into AI Summary Nugget)"
        )
        if bigrams:
            lines.append("  Bigrams:")
            for b in bigrams:
                lines.append(f"    - {b['phrase']} ({b['count']}x)")
        if trigrams:
            lines.append("  Trigrams:")
            for t in trigrams:
                lines.append(f"    - {t['phrase']} ({t['count']}x)")

    # Brand differentiators (v1.9.1)
    diffs = research.get("differentiators", [])
    if diffs:
        lines.append("\n## Brand Differentiators (mandatory in body + AI Summary Nugget)")
        for d in diffs:
            lines.append(f"  - {d}")

    # Missing spokes (v1.9.1)
    spokes = research.get("missing_spokes", [])
    if spokes:
        lines.append(
            "\n## Missing Spokes (from top 3 competitor internal anchors)"
        )
        for s in spokes[:15]:
            lines.append(f"  - {s['anchor']} ({s['competitor_count']}x)")

    # Structural directives (v2.0.0)
    sd = research.get("structural_directives", {})
    if sd:
        lines.append("\n## Structural Directives (v2.0.0 -- agent must obey)")
        lines.append(f"  - Snippet answer container: {sd.get('snippet_answer_container', '?')}")
        lines.append(f"  - Max DOM nesting depth: {sd.get('max_dom_nesting_depth', '?')}")
        lines.append(f"  - Subheading entity synergy: {sd.get('subheading_entity_synergy', '?')}")
        lines.append(f"  - Two-gate target: {sd.get('two_gate_target', '?')}")
        lines.append(f"  - Anti-NLP stuffing: {sd.get('anti_nlp_stuffing', '?')}")
        lines.append(f"  - Outbound citations (min {sd.get('outbound_citations_min', '?')}): {sd.get('outbound_citation_rule', '?')}")
        lines.append(f"  - Strict phrase placement: {sd.get('strict_phrase_placement', '?')}")
        lines.append(f"  - Entity-fact pairing: {sd.get('entity_fact_pairing', '?')}")
        lines.append(f"  - Intent divergence: {sd.get('intent_divergence', '?')}")
        lines.append(f"  - Anti-boilerplate linking: {sd.get('anti_boilerplate_linking', '?')}")

    # DOM nesting audit (v2.0.0)
    dn = research.get("dom_nesting", {})
    if dn:
        lines.append("\n## DOM Flattening Audit (v2.0.0)")
        lines.append(f"  Status: {dn.get('status', '?')}")
        flagged = dn.get("flagged", [])
        if flagged:
            lines.append(f"  Flagged (depth > {dn.get('target_max_depth', 3)}):")
            for f in flagged:
                lines.append(f"    - {f.get('url', '?')} (depth {f.get('max_depth', '?')})")

    # Affiliate monetization directive (v2.2.0) -- only when in affiliate mode
    aff = research.get("affiliate", {})
    if aff and aff.get("mode") == "affiliate":
        lines.append("\n## Affiliate Monetization (v2.2.0 -- COMPLIANT, no cloaking)")
        lines.append(f"  Link: {aff.get('affiliate_link', '?')}")
        lines.append(f"  CTA rel: {aff.get('cta_rel', '?')}")
        lines.append(f"  Directive: {aff.get('directive', '?')}")
        lines.append(f"  Forbidden: {aff.get('forbidden', '?')}")

    return "\n".join(lines)


def main():
    args = parse_args()
    research = run_research(args)

    # Save
    filepath = save_research(research, args.save_dir)

    # Output
    if args.output == "json":
        print(json.dumps(research, indent=2))
    elif args.output == "brief":
        # Minimal output for piping into content generation
        analysis = research.get("analysis", {})
        brief_data = {
            "keyword": research["keyword"],
            "primary_intent": research.get("primary_intent"),
            "secondary_intent": research.get("secondary_intent"),
            "meta_entities": research.get("meta_entities", []),
            "target_ngrams": research.get("target_ngrams", {}),
            "differentiators": research.get("differentiators", []),
            "missing_spokes": research.get("missing_spokes", []),
            "structural_directives": research.get("structural_directives", {}),
            "dom_nesting": research.get("dom_nesting", {}),
            "affiliate": research.get("affiliate", {}),
            "word_count_stats": analysis.get("word_count_stats"),
            "paa_questions": analysis.get(
                "paa_questions",
                research.get("serp", {}).get("paa", []),
            ),
            "topic_frequency": analysis.get("topic_frequency", [])[:10],
            "heading_patterns": analysis.get("heading_patterns"),
            "research_file": filepath,
        }
        print(json.dumps(brief_data, indent=2))
    else:
        print(format_compact(research))


if __name__ == "__main__":
    main()
