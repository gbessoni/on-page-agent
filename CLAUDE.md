# CLAUDE.md

This is **seo-agi** -- a Claude Code skill for Generative Engine Optimization. It writes pages that rank on Google AND get cited by LLMs.

This is not a generic SEO prompt. It enforces 500-token chunk architecture, Reddit Test quality gates, verification tags, "Not For You" blocks, ICP-driven content targeting, and real competitive data from DataForSEO/Ahrefs/SEMRush/GSC.

## Structure

```
SKILL.md              -- The framework (GEO engine + data layer integration)
SPEC.md               -- Technical architecture for the data layer
scripts/
  research.py         -- CLI: SERP research via DataForSEO. v1.7.1 adds
                         meta_entities (bolded snippet phrases),
                         target_ngrams (top 3 competitor bigrams/trigrams),
                         primary_intent + secondary_intent dual mapping.
  gsc_pull.py         -- CLI: Google Search Console data. v2.4.0 adds
                         --ghost-paths (impression-earning URLs that 404)
                         and --crawl-stats-csv (manual Discovery export).
                         Crawl Stats is UI-only, not in the GSC API.
  tributary_gen.py    -- CLI: Generates Tier 1/Tier 2 companion content
                         (Google Sites, Medium, Subreddit, Google Sheets,
                         LinkedIn) topically derived from the money page's
                         500-token chunk architecture. See SKILL.md
                         "Tributary Trust Protocol" for the strategy.
  setup.py            -- Interactive first-run config
  lib/
    env.py            -- Config loader
    dataforseo.py     -- DataForSEO REST API client
    massive.py        -- Massive Web Render client (v1.9.0). Primary
                         competitor content parser when MASSIVE_API_TOKEN
                         is set. Returns clean markdown including
                         JS-loaded content. Per-URL fallback to
                         DataForSEO on failure.
    serp_analyze.py   -- Content gap analysis engine
    gsc_client.py     -- Google Search Console client
references/
  page-templates.md   -- Structural templates by page type
  schema-patterns.md  -- JSON-LD schema patterns
fixtures/             -- Mock data for testing without API calls
tests/                -- Unit tests
```

## The Framework (SKILL.md)

The SKILL.md is the living document. It contains:
- Core belief system (anti-generic, LLM retrieval, entity consensus)
- Google AI Search 7 ranking signals
- 500-token chunk architecture
- SEAT signals (Semantic + E-E-A-T + Entity/Knowledge Graph)
- Quality gates: Reddit Test, Prove-It Details, Not For You, Information Gain Test
- ICP (Ideal Customer Persona) requirement in every page brief
- Deep Entity History & Identity Tags for local trust signals
- Self-Placement Rule for listicles (objective #1 ranking with tradeoffs)
- Keyword Cannibalization governance (noindex for overlapping intents)
- **Tributary Trust Protocol**: AEO entity validation via owned Tier 1 assets
  (Google Sites, Medium, Subreddits, Google Sheets, LinkedIn). Quality gates
  apply equally to off-page content -- thin tributaries net-harm the money
  page's entity signal. Generated via `scripts/tributary_gen.py`.
- **MASTER RULE: Anti-Hallucination Meta-Directive** (v2.4.0): at the
  top of SKILL.md. The agent must not apply pre-trained SEO knowledge
  (LSI, keyword density, blog hubs, arbitrary word counts) and executes
  only the rules in the document. Table of instincts to suppress.
- **Discovery Routes & Off-Page Embeds** (v2.4.0): `gsc_pull.py
  --ghost-paths` finds impression-earning URLs that 404;
  `--crawl-stats-csv` ingests the manual export (Crawl Stats is UI-only,
  not in the GSC API). Junk-path filter prevents mass-generating pages
  for exploit probes. Tier 1 drafts get plain-text brand/URL mentions
  and a conditional Maps embed. CSR SPAs banned; internal links must be
  in the raw HTML DOM. 66-point checklist, threshold 57/66.
- **AI SEO Correlation Protocols** (v2.3.0): 5+ descriptive outbound
  citations required (zero = severe citation penalty; nofollow NOT
  default, it has not preserved equity since 2009). Strict Phrase
  Placement retires the conditional Forensic EMQ Check -- exact match
  in Title and H1 only, never H2/H3/H4. Entity-Fact Pairing in every
  chunk. Intent Divergence (informational strips CTAs/awards, local
  features them). Anti-Boilerplate internal linking, with the
  per-page-derived Spoke Pages block exempted. 63-point checklist,
  threshold 54/63.
- **Local Isolation + Compliant Affiliate** (v2.2.0): local pages must
  target one service+place (no multi-service stacking -- AI parsers
  truncate); local pages emit a GBP directive (point GBP at the inner
  page, not homepage). Affiliate monetization via
  `research.py --affiliate-link` is COMPLIANT-only: disclosed
  rel="sponsored nofollow" + FTC disclosure, same page for crawler and
  human. Cloaking/JS-redirect affiliate bypass was rejected as a
  spam-policy/de-indexation risk. 58-point checklist, threshold 49/58.
- **Anti-NLP Stuffing Protocol** (v2.1.0): force-repeating NLP-tool
  entity lists (Surfer, Google NLP API, Clearscope) in body prose is
  forbidden (~25% de-indexation). Section 4 rewritten to Structural
  Entity Placement -- entities go in headings/table cells/schema, not
  paragraph text. research.py STRUCTURAL_DIRECTIVES gains an
  anti_nlp_stuffing directive. 56-point checklist, threshold 47/56.
- **Two-Gate AEO & DOM Flattening** (v2.0.0): optimization targets
  Gate 1 (retrieval-pool entry) + Gate 2 (citation extraction).
  Anti-Paragraph rule (primary H2 answers in block containers, never
  bare `<p>`), DOM nesting depth flattening (max ~3 levels), Goldilocks
  entity synergy in subheadings. research.py emits `structural_directives`
  to the agent and a `flag_deep_nesting()` competitor audit
  (`measure_dom_depth()` pure analyzer; reports not_assessed without raw
  HTML). 55-point checklist, threshold 46/55.
- **Decision Fit + Brand Voice + Missing Spokes** (v1.9.1):
  `--differentiators` CLI flag flows brand USPs into the brief output.
  `extract_missing_spokes()` mines top 3 competitors' internal anchors
  (generic nav + image-link leakage filtered) for the page's required
  `Recommended Spoke Pages` section. Execution Protocol now asks for
  differentiators if not provided. 51-point checklist with Decision
  Fit, Brand Identity, and Topical Silo checks.
- **Massive Web Render integration** (v1.9.0): competitor content
  parsing now flows through Massive when `MASSIVE_API_TOKEN` is set,
  with graceful per-URL fallback to DataForSEO. SERP and keyword data
  still come from DataForSEO -- Massive's search endpoint doesn't
  return organic results.
- **Gemini 3.5 Flash RAG Optimization** (v1.8.0): DOM Vectoring &
  Shard Extraction Compliance (critical data must live in front-facing
  `<table>` / RDFa, not just JSON-LD), Trust Pilot as Tier 1 tributary,
  Off-Page Schema Injection (Organization/Person schema on Cloud Pages
  and PRs linking to GBP CID to block NavBoost rank-shuffling),
  48-point checklist with new DOM-visible-data check.
- **LLM Retrieval & Substantive Content Protocols** (v1.7.1): Meta Entity
  Isolation (snippet-level entities), Bigram/Trigram AI Alignment (top
  3 competitor n-grams in AI Summary Nugget), Dual-Intent Mapping
  (Primary + Secondary action funnel), 410 Prune Protocol (explicit
  301/410 recommendations on rewrites), Technical Codebase Execution
  (semantic HTML injection + redirect config snippets when in-repo).
- Verification tagging system ({{VERIFY}}, {{RESEARCH NEEDED}}, {{SOURCE NEEDED}})
- Vertical-specific instructions (airport/parking, local service, listicle, comparison)
- LLM/AEO citation strategy
- Hub & spoke internal linking
- Execution protocol with data layer integration

## Running Tests

```bash
python3 tests/test_env.py
python3 tests/test_serp_analyze.py
python3 tests/test_dataforseo.py

# Mock mode research:
python3 scripts/research.py "test keyword" --mock
```

## Style

- No em dashes in any output
- No "nestled", no "in today's fast-paced world", no "whether you're a...or a..."
- Numbers and specifics over adjectives
- Every claim tagged with {{VERIFY}} or {{SOURCE NEEDED}}
- Tables are mandatory for comparisons -- never simulate with bullet points
