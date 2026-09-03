# Changelog

All notable changes to seo-agi are documented here.

## [2.3.0] - 2026-09-03

### Added
- **Outbound Citation Requirement**: pages targeting AI Overviews must carry at least 5 descriptive outbound links to external authoritative sources. Zero outbound links carries a severe citation penalty.
- **Strict Phrase Placement (Title + H1 only)**: exact-match keyword restricted to exactly two locations. H2/H3/H4 exact-match is now unconditionally forbidden.
- **Entity-Fact Pairing** (Section 3, applies to every 500-token chunk): every entity named in a chunk must be bound to a hard verifiable fact in that same chunk.
- **Informational vs. Local Divergence**: informational pages strip sales CTAs, free-estimate offers, and award mentions; local Ask Maps pages feature local project counts, awards, and differentiators. Selected by `research.primary_intent`.
- **Anti-Boilerplate Internal Linking**: site-wide repetitive in-content link blocks banned. Internal links must be contextual and unique to their chunk.
- **63-point quality checklist** with #59-#63. Passing threshold raised to 54/63.
- Five new `STRUCTURAL_DIRECTIVES` entries in `scripts/research.py` (`outbound_citations_min`, `outbound_citation_rule`, `strict_phrase_placement`, `entity_fact_pairing`, `intent_divergence`, `anti_boilerplate_linking`), surfaced in compact/brief/JSON output.

### Changed / Retired
- **The Forensic EMQ Check is retired.** The former rule made H1 exact-match conditional on whether 2 of the top 3 competitors used it (`EMQ_REQUIRED` flag). That conditional is gone: H1 placement is now unconditional and H2/H3/H4 is unconditionally forbidden. Copying an over-optimized competitor's heading pattern imports their demotion risk, not their ranking. Competitor EMQ ratio is still recorded, but as niche-over-optimization context only. Execution Protocol step 1, step 3, and checklist item #37 updated accordingly.
- **`rel="nofollow"` on citations is documented as optional and not recommended by default.** The requested rationale ("preserve equity") has been false since 2009: Google changed PageRank sculpting so a nofollowed link still consumes its share of equity, which then evaporates rather than passing. You lose the equity either way and additionally forfeit the editorial trust signal. Nofollow/sponsored remains correct for paid, affiliate, and untrusted links.
- **Anti-Boilerplate reconciled with the v1.9.1 Spoke Pages rule.** The required `Recommended Spoke Pages` block is exempt because it is derived per-page from `missing_spokes`. Identical spoke lists across pages mean it has become boilerplate and must be regenerated.

## [2.2.0] - 2026-06-03

### Added
- **Strict Local Service Isolation** (SKILL.md Section 10 + highlights). Local pages must target a single service+place; multi-service catch-all stacking is now a hard rule violation because AI parsers truncate stacked pages. N services in a city = N pages.
- **GBP Canonical Link Directive** (Section 10 + Execution Protocol step 8c). Local pages emit a directive telling the user to point their Google Business Profile website field at the specific inner page, not the homepage.
- **Compliant affiliate monetization** (`scripts/research.py --affiliate-link`, `build_affiliate_block()`, Execution Protocol step 8b). Emits a compliant affiliate directive: disclosed `rel="sponsored nofollow"` CTAs + FTC disclosure (16 CFR 255), crawler and human read the same page. Surfaced in compact/brief/JSON output.
- **58-point quality checklist** -- adds #57 Local Isolation and #58 GBP Inner-Link Directive (both N/A pass on non-local pages). Passing threshold raised to 49/58.
- 4 new tests in `tests/test_research_v220.py` covering the affiliate block (none/compliant modes, cloaking-forbidden guardrail, whitespace).

### Changed / Rejected
- The originally-requested "JavaScript Affiliate Bypass" (serve informational HTML to LLM crawlers while JS-redirecting humans to an affiliate page) was **rejected as cloaking / a sneaky redirect** -- a Google spam-policy violation and de-indexation trigger that directly contradicts the v2.1.0 Anti-NLP Protocol. Replaced with the compliant disclosed-CTA pattern above. SKILL.md and research.py explicitly forbid JS redirects, meta-refresh, and crawler/user content divergence for affiliate pages.

## [2.1.0] - 2026-06-03

### Added
- **The Anti-NLP Stuffing Protocol** (SKILL.md "The NLP SEO Lie", Section 9 Never Do). Practitioner testing links force-repeating NLP-tool entity lists (Surfer SEO, Google Natural Language API, Clearscope) in body prose to ~25% de-indexation. The agent is strictly forbidden from NLP entity stuffing; entities earn weight through structural placement, not repetition targets.
- **Structural Entity Placement** -- Section 4 (SEAT Signals) rewritten. Removed the "Google's KG uses different NLP than transformers" framing; replaced with placement rules: entities belong in headings, table cells, definition terms, and schema fields, not stuffed into paragraph text. Placement once beats prose repetition ten times.
- **`anti_nlp_stuffing` directive** added to `STRUCTURAL_DIRECTIVES` in `scripts/research.py`, surfaced in compact + brief + JSON output.
- **56-point quality checklist** -- adds #56 Anti-NLP Stuffing check. Passing threshold raised to 47/56.

### Note
The other v2.1.0 highlight items (Two-Gate paradigm, Anti-Paragraph Snippet, DOM Flattening, Goldilocks Entity Synergy) shipped in v2.0.0 and are recapped in the v2.1.0 version-highlights block for completeness; they are unchanged. The single net-new checklist item is #56, which is why the count moved 55 -> 56.

## [2.0.0] - 2026-06-03

Major release. Reframes the optimization target around the Two-Gate AEO model.

### Added
- **The Two-Gate AEO Framework** (SKILL.md, new "NEW IN v2.0.0" section before Section 0). Optimization now targets Gate 1 (Retrieval Pool Entry) and Gate 2 (Selected Citation Extraction) explicitly. Meta-tag tuning is demoted -- it does not drive AI Overview success.
- **Anti-Paragraph Snippet Answer Rule** (Section 3). Primary 2-3 sentence answers beneath an H2 must NOT use bare `<p>` tags -- they are skipped for first-position citations. Must use block-level structural containers (`div.answer`, `blockquote`, `dl`/`dd`, leading table row, RDFa/Microdata span block).
- **DOM Nesting Depth Flattening** (Section 6). Shallow-DOM enforcement, target max ~3 nesting levels. Visual-builder wrapper bloat (Elementor/Divi) is penalized at runtime. Competitors exceeding the target are flagged `DOM_FLATTENING_OPPORTUNITY`.
- **Goldilocks Entity Synergy** (Section 6). Subheadings repeat core associated entity pairings to build citation-extraction synergy; generic subheadings are banned.
- **`scripts/research.py` additions**:
  - `STRUCTURAL_DIRECTIVES` block now in every research payload (live, mock, no-creds, brief) -- the formatting configuration the writing agent reads (flat block snippet containers, anti-`<p>`, max depth, entity synergy, two-gate target).
  - `measure_dom_depth(html)` -- pure stack-based max-nesting-depth analyzer (void/self-closing tags excluded).
  - `flag_deep_nesting()` -- competitor DOM-flattening audit. Activates on raw HTML when a parser supplies it; reports `not_assessed` (never a fabricated number) otherwise, since DataForSEO content_parsing and Massive markdown do not expose raw HTML today. Forward-compatible.
- **55-point quality checklist** with #52 Anti-Paragraph Snippet, #53 DOM Flattening Depth, #54 Goldilocks Entity Synergy, #55 Two-Gate Extraction Pass. Passing threshold raised to 46/55.
- 11 new tests in `tests/test_research_v200.py` (DOM-depth measurement edge cases, deep-nesting flag with/without raw HTML, top-N limiting, structural-directives shape).

### Note on scope
`research.py` is the data layer, not a page-HTML generator -- it has no `<p>`-emitting code to swap. The v2.0.0 layout rules (flat blocks, anti-`<p>`, Goldilocks) are enforced at the agent layer via SKILL.md + the `structural_directives` payload the agent consumes. The competitor DOM-nesting audit ships ready and unit-tested; it reports `not_assessed` until a parser provides raw HTML.

## [1.9.1] - 2026-05-21

### Added
- **`--differentiators` CLI flag** on `scripts/research.py`. Comma-separated brand USPs (e.g. `--differentiators="women-owned, 24/7 service, no hidden fees"`) flow through to the research JSON + brief output as `research.differentiators` for the writing agent to enforce verbatim.
- **Missing Spoke Detection** in `scripts/research.py` (`extract_missing_spokes()`). Walks the top 3 ranking competitors' internal-link anchors, filters out generic navigation (Home, Contact, Privacy, FAQ, etc.) and nested-image-link leakage, returns a ranked `missing_spokes` list in the output payload.
- **Link extraction in both content parsers**: `MassiveClient._parse_markdown` now returns a `links` list (`[{text, url}]`) from standard markdown link syntax; `DataForSEOClient._extract_links` walks `primary_content[].urls[]` across `main_topic` and `secondary_topic`.
- **SKILL.md Section 12 (Hub & Spoke)** now requires every generated page to append a `## Recommended Spoke Pages` block built from `missing_spokes`.
- **SKILL.md Execution Protocol** now stops and asks the user for Brand Differentiators / USPs if not provided up front. Pages built without explicit differentiators are flagged as Reddit-Test failure risk.
- **51-point quality checklist** with #49 Decision Fit, #50 Brand Identity, #51 Topical Silo. Passing threshold raised to 42/51.
- 15 new tests in `tests/test_research_v191.py` covering differentiator parsing, domain normalization, generic-anchor filtering (including nested-image-link leakage), missing-spokes extraction, and link extraction in both content parsers.

### Changed
- `references/quality-checklist.md` appended with a v1.9.1 section detailing the three new checks and threshold.

## [1.9.0] - 2026-05-20

### Added
- **Massive Web Render integration** (`scripts/lib/massive.py`). When `MASSIVE_API_TOKEN` is configured, the `/browser` endpoint becomes the primary competitor content parser. Returns clean rendered markdown including JS-loaded content -- the gap DataForSEO's `content_parsing/live` has always had.
- **Per-URL graceful fallback**: if Massive errors or returns empty for any single URL, that URL falls back to DataForSEO. Partial Massive outage cannot break a run.
- **`content_parsers` field** in research output records which parser handled each URL (e.g. `{"massive": 4, "dataforseo-fallback": 1}`). Visible in saved JSON and printed in compact output's per-URL log lines (`via massive` / `via dataforseo`).
- **`MASSIVE_API_TOKEN`** added to `.env.example` and `env.py` credential loader. New `creds["has_massive"]` flag.
- 8 new unit tests in `tests/test_massive.py` covering the markdown parser, output-shape contract with DataForSEOClient, and client construction.

### Changed
- `scripts/research.py` content-parsing step now branches on Massive availability per URL.
- SKILL.md Data Cascade table reorganized to surface Massive as Priority 1 for content parsing, with DataForSEO as the SERP + keyword data backbone and per-URL fallback.

### Not Changed
- **SERP organic results, PAA, and keyword data still come from DataForSEO.** Massive's `/search` endpoint as of v1.9.0 only returns "also-searched" suggestions, not organic results. SERP path is unchanged.
- All existing tests pass. Heading extraction, n-gram analysis, meta-entity isolation, intent detection, and the 48-point checklist behave identically whichever content parser is used.

## [1.8.0] - 2026-05-08

### Added
- **DOM Vectoring & Shard Extraction Compliance** (SKILL.md Section 6): documents the constraint that Google's AI Overviews are now built by Gemini 3.5 Flash via a RAG pipeline that extracts structural "shards" from the raw HTML DOM. Critical data must live in front-facing `<table>` markup or inline RDFa spans -- JSON-LD in `<head>` is no longer sufficient on its own.
- **Trust Pilot as Tier 1 Tributary** (Section 11A): added to the Tributary Trust Protocol table as a first-class Tier 1 asset. Cited as a highly weighted trust/relevance signal for LLMs that shifts brand description vectoring in Gemini and ChatGPT within 48 hours.
- **Off-Page Schema Injection** (Section 11A): new Tier 1 tactic. Embedding `Organization` and `Person` JSON-LD schema in Cloud Pages and PRs with explicit GBP CID backlinks blocks Google NavBoost from rank-shuffling the money page during A/B exposure tests.
- **48-point quality checklist**: adds #46 (Trust Pilot entity profiling with target bigrams), #47 (off-page Organization/Person schema mapping), #48 (DOM-visible critical data points). Passing threshold raised to 39/48.

### Changed
- Tributary network spread requirement updated from "4 of the 5 Tier 1 assets" to "5 of the 7 Tier 1 assets" to account for the two new asset types.
- SKILL.md frontmatter description now mentions Gemini 3.5 Flash RAG optimization.

## [1.7.1] - 2026-05-07

### Added
- **Meta-Specific Entity Isolation**: `extract_meta_entities()` mines bolded query-matched phrases from the `highlighted` field of competitor SERP results (with inline `<b>`/`<strong>`/`**` fallback parsing). These are the entities Google's snippet generator already validated as relevant -- a stronger signal than body-content extraction.
- **Bigram/Trigram AI Alignment**: `extract_target_ngrams()` tokenizes the top 3 ranking competitors' headings + titles, filters via an inlined English stopword list, and returns the top 5 bigrams and top 5 trigrams. Output seeds the AI Summary Nugget for LLM-retrieval token overlap.
- **Primary + Secondary Intent (Orcas 1)**: `detect_secondary_intent()` maps the funnel-next intent (informational → commercial → transactional → navigational), with overrides for transactional title signals (book/reserve/buy) and brand-domain dominance in the top 5.
- **45-point quality checklist**: adds Meta Entity Isolation, N-Gram Alignment, Dual-Intent, and Status Code Governance checks. Passing threshold raised to 36/45.
- **Technical Codebase Execution Rules** (SKILL.md): when the skill runs inside a project repo, it detects the framework (Next.js, Astro, Gatsby, Hugo, etc.), injects semantic HTML into source files, and emits `.htaccess` / Nginx / `next.config.js` redirect snippets for 301/410 recommendations.
- **The 410 Prune Protocol** in the rewrite workflow: every legacy URL gets an explicit 301 (preserve equity) or 410 (prune) recommendation. Silent leave-as-is is no longer acceptable.

### Changed
- `dataforseo.py`: `_extract_serp` now passes through the `highlighted` field on every organic result (was being dropped). Required for Meta Entity Isolation.
- `research.py`: research output now surfaces `primary_intent`, `secondary_intent`, `meta_entities`, and `target_ngrams` at top level (not buried in `analysis`) for direct brief consumption.
- README.md "What It Actually Does" block expanded from 13 to 14 steps reflecting dual-intent mapping (step 5), n-gram seeding (step 8), and 301/410 governance (step 12).
- HARD RULES rewritten in SKILL.md: replaced the negative "never use codename X" rule with positive naming guidance ("framework is seo-agi / seobuild-onpage; no prior internal codenames in any output").

### Tests
- Added `tests/test_research_v171.py` with 13 new tests covering meta-entity extraction (highlighted field + inline-tag fallback + dedup), n-gram extraction (stopword filtering, top-N limiting, empty-input safety), tokenizer behavior, and secondary-intent funnel + override logic.

## [1.7.0] - 2026-04-30

### Added
- **Tributary Trust Protocol** (Section 11A): off-page architecture for AEO entity validation. Defines Tier 1 owned assets (Google Sites, Medium, Subreddits, Google Sheets, LinkedIn) as tributaries that feed entity signal to the money page. Includes companion-content rules, network topology, derivation matrix, and sequencing requirements.
- **Core Belief #7**: AEO Entity Validation via Owned Tier 1 Assets. Knowledge Graph inclusion and AI Overview impression share are now primary success signals, gated by off-page corroboration.
- **`scripts/tributary_gen.py`**: CLI tool that reads a money page, extracts its 500-token chunks + entities + `{{VERIFY}}` tags, and outputs derived companion briefs to `~/Documents/SEO-AGI/tributaries/<slug>/` with a manifest mapping each draft to its host platform.
- **Execution Protocol step 11**: tributary deployment is now mandatory for commercial-intent and local pages. All quality gates (Reddit Test, Information Gain, Prove-It, `{{VERIFY}}` resolution, Section 9 banned patterns, Entity Consensus) apply equally to off-page content -- thin tributaries net-harm the money page's entity signal.

### Changed
- CLAUDE.md directory structure now lists `scripts/tributary_gen.py`
- CLAUDE.md framework features updated with Tributary Trust capability

## [1.6.1] - 2026-04-28

### Fixed
- **Heading extraction returned empty for every competitor page.** DataForSEO's `on_page/content_parsing/live` endpoint returns headings inside `main_topic[]` and `secondary_topic[]` arrays (each with `h_title` and `level`), not as flat `h1`/`h2`/`h3` arrays. The old `_extract_headings` looked for keys that don't exist, so `Avg H2s: 0, Avg H3s: 0` for every research run regardless of competitor depth. Now correctly walks the topic tree.
- **Word count returned 0 for every competitor.** `plain_text_word_count` is not a field DataForSEO returns. Now computes from `page_as_markdown` (preferred) with a fallback walking `primary_content[].text`.
- **Title extraction returned empty.** `header.title` doesn't exist; replaced with markdown H1 detection plus a `main_topic[0].h_title` fallback.
- Added regression tests covering the real API response shape so this can't silently break again.

## [1.6.0] - 2026-04-15

### Added
- **Ideal Customer Persona (ICP)**: Page brief template now requires a defined ICP with demographics, psychographics, and specific pain points. Content maps to the actual reader, not a generic audience.
- **Deep Entity History & Identity Tags**: Founding dates, generational ownership, and identity attributes (women-owned, veteran-owned) are now explicit entity signals in Section 4 SEAT Signals.
- **The Self-Placement Rule**: Listicle guidance now explicitly allows ranking the client #1, provided the entry is objective with a specific use-case and honest tradeoffs.
- **Keyword Cannibalization Governance**: Section 9 "Never Do" list now prohibits creating pages that compete with existing URLs for the same intent. Sales-focused duplicates get tagged with `noindex` recommendation.

### Changed
- Quality checklist expanded from 38 to 41 items (ICP alignment, entity history, cannibalization)
- Minimum passing score raised to 33/41
- Both brief templates (Page Brief Template + Execution Protocol) updated with ICP field

## [1.3.0] - 2026-03-25

### Added
- **AI Summary Nugget**: Mandatory 200-character fact-dense block at top of every page, designed for LLM scrapers (Perplexity, Gemini, ChatGPT) to cite as a consensus source
- **Original Research Block**: Every page must include a data experiment or first-hand observation section to satisfy Google's Experience (E-E-A-T) signal
- **Map Traffic Shifting**: Local SEO instruction to link from high-traffic informational pages to map embeds, shifting user interaction signals toward local intent
- **Spam Resilience Logic**: Quality checklist now prioritizes technical relevance density over "human tone" -- factually perfect content is not downgraded for sounding clinical
- **Recursive Fact-Checking**: New execution step validates every claim against 2+ high-ranking sources for Entity Consensus before delivery

### Changed
- Quality checklist expanded from 24 to 28 items
- Minimum passing score raised to 22/28
- Execution protocol now has 11 steps (was 10)

## [1.2.0] - 2026-03-25

### Added
- Anti-spam ranking signals: single H1 rule, no EMQ in meta descriptions, no keyword-stuffed alt text, no duplicate content, internal linking requirements
- EMQ allowed in title and URL, banned in H2/H3/H4 subheadings
- Interactive elements section (cost calculators, widgets) to defend against AI Overview traffic loss
- Broken backlink monitoring guidance
- "Boat anchor" page culling (410 status for unindexable cruft)

### Changed
- Quality checklist expanded from 20 to 24 items (added H1, meta desc, heading, alt text checks)

## [1.1.0] - 2026-03-24

### Added
- Hard rule: framework is named seo-agi only; prior internal codenames must not appear in output
- Mandatory printed scorecard at end of every page output (no exceptions)
- FAQ/PAA section required (3+ questions, FAQPage schema)
- JSON-LD schema block required per page type
- Hub/spoke internal links required in every output
- RAG Targeting section (write for AI retrieval, not keyword volume)
- Topical Circle Audit (stay inside core service topic, noindex strays)
- Off-Page Sequencing (establish external brand footprint before on-page)
- Reddit Subdomain Indexing (subdomains over standard posts for AI retrieval)
- Ask Maps / Conversational GBP Optimization

### Changed
- Quality checklist expanded from base to 20 items
- Scorecard enforcement language strengthened ("INCOMPLETE without this table")

## [1.0.0] - 2026-03-23

### Added
- Initial release: GEO framework skill for Claude Code, OpenClaw, and Codex
- 500-token chunk architecture for Google AI retrieval
- SEAT signals (Semantic + E-E-A-T + Entity/Knowledge Graph)
- Google AI Search 7 ranking signals (Gecko, Jetstream, BM25, PCTR, Freshness, Boost/Bury)
- Reddit Test, Prove-It Details, Not For You, Information Gain quality gates
- Verification tagging system (VERIFY, RESEARCH NEEDED, SOURCE NEEDED)
- DataForSEO integration with graceful no-creds fallback
- MCP tool integration (Ahrefs, SEMRush)
- Google Search Console pull scripts
- Skill root discovery loop (works across Claude Code, OpenClaw, Codex, Gemini)
- Reference files: page templates, schema patterns, quality checklist
- Mock mode for testing without API keys
