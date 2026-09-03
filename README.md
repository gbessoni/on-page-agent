# seobuild-onpage v2.4.0

### One command. Competitive data in. Ranking pages out.

```bash
git clone https://github.com/gbessoni/seobuild-onpage.git ~/.claude/skills/seobuild-onpage
```

Most SEO tools tell you what's wrong with your site. This one writes the pages.

`/seoagi "airport parking JFK"` pulls the current SERP, analyzes what's ranking, finds the gaps in their content, and writes you a complete page -- with the heading structure, depth, FAQ section, and schema markup that actually competes. Not thin content. Not keyword-stuffed filler. Pages backed by live data from the tools the pros use.

**New in v2.4.0 -- Discovery Routes & Off-Page Embeds:**
- **The Anti-Hallucination Meta-Directive** -- a new MASTER RULE at the top of SKILL.md. LLMs are trained on fifteen years of largely obsolete SEO writing, so the agent is now explicitly forbidden from applying pre-trained SEO instincts (LSI keywords, keyword density, blog hubs, "write 2,000 words") and must execute only the rules in the document. Includes a table of the specific instincts to suppress and why each is wrong.
- **GSC Discovery Route Fill** -- find URLs Google already expects to exist and fill them. `gsc_pull.py --ghost-paths` finds pages earning impressions that return 404, which is the highest-confidence signal available through the API. `--crawl-stats-csv` ingests a manual Crawl Stats export for the literal Discovery list, because that report is UI-only and not in the Search Console API.
- **Unlinked Brand Citations** -- Tier 1 off-page drafts now carry plain-text brand and URL mentions alongside HTML links. RAG pipelines read plain text, so this adds retrieval coverage anchor-only linking misses.
- **Off-Page Embeds** -- Tier 1 drafts embed a live artifact pointing at the money entity where the platform allows it, defaulting to the officially supported Google Maps embed. Conditional by design, since most Tier 1 platforms block arbitrary iframes.
- **Strict SSR/SSG Requirement** -- client-side-rendered SPAs are banned as an output target. Every internal link must exist in the raw HTML DOM of the initial server response, because JS-injected link graphs are routinely missed or crawled late.
- **66-point quality checklist** -- adds Off-Page Embed, Unlinked Citation, and SSR/SSG Validation. Passing threshold raised to 57/66.

**New in v2.3.0 -- AI SEO Correlation Protocols:**
- **Outbound Citation Requirement** -- pages targeting AI Overviews must link out to at least 5 external authoritative sources with descriptive anchor text. Zero outbound links carries a severe citation penalty: an engine checking whether the page synthesizes real sources finds nothing to verify against.
- **Strict Phrase Placement (Title + H1 only)** -- the exact-match keyword appears in exactly two places and nowhere else. H2/H3/H4 exact-match is now unconditionally forbidden. This retires the old competitor-ratio Forensic EMQ Check, which made H1 placement conditional.
- **Entity-Fact Pairing** -- naming an entity is not a signal; binding it to a hard fact is. Every entity in a chunk must carry a time, place, cost, capacity, frequency, distance, or date. Crucial non-obvious information is the highest-weighted retrieval signal.
- **Informational vs. Local Divergence** -- informational pages strip sales CTAs, free-estimate offers, and award mentions (they demote citation rate). Local Ask Maps pages feature local project counts, awards, and differentiators heavily. Same elements, opposite treatment, selected by detected intent.
- **Anti-Boilerplate Internal Linking** -- site-wide repetitive in-content link blocks are banned; internal links must be contextual and unique to their chunk. The Recommended Spoke Pages block stays, because it is derived per-page from competitor anchor data rather than templated.
- **63-point quality checklist** -- adds Outbound Citation, Strict Phrase Placement, Entity-Fact Pairing, Intent Divergence, and Anti-Boilerplate checks. Passing threshold raised to 54/63.

**New in v2.2.0 -- Compliant Affiliate Monetization & Local Isolation:**
- **Strict Local Service Isolation** -- local pages must target a single service+place ("Water Heater Repair Anaheim"), never a multi-service catch-all. AI parsers truncate stacked pages because they can't form a clean service-to-place association. N services in a city = N pages.
- **GBP Canonical Link Directive** -- local pages now emit a directive telling the user to point their Google Business Profile website field at the specific inner page, not the homepage. Strongest local-relevance signal, usually wasted on the homepage.
- **Compliant Affiliate Monetization** -- `research.py --affiliate-link` emits a compliant affiliate directive: disclosed `rel="sponsored nofollow"` CTAs + FTC disclosure, crawler and human read the same page. (An earlier draft of this feature proposed a JS redirect that served informational HTML to LLMs while bouncing humans to an affiliate page -- that is cloaking / a sneaky redirect, a Google spam-policy violation and de-indexation trigger, so it was replaced with the compliant pattern.)
- **58-point quality checklist** -- adds Local Isolation (#57) and GBP Inner-Link Directive (#58) checks (N/A pass on non-local pages). Passing threshold raised to 49/58.

**New in v2.1.0 -- The Anti-NLP Protocol & Two-Gate AEO:**
- **The NLP SEO Lie** -- practitioner testing shows that artificially stuffing traditional NLP entities (Surfer SEO, Google's Natural Language API, Clearscope term lists) into body copy to hit a coverage score results in ~25% de-indexation. The agent is strictly forbidden from NLP entity stuffing. Entities earn weight through structural placement, never repetition targets.
- **Structural Entity Placement** (Section 4 rewrite) -- entities belong in headings, table cells, definition terms, and schema fields, not stuffed into paragraph text. Placement once beats prose repetition ten times.
- Two-Gate AEO, Anti-Paragraph Snippet, DOM Flattening, and Goldilocks Entity Synergy (all shipped in v2.0.0) remain in full force.
- **56-point quality checklist** -- adds the Anti-NLP Stuffing check (#56). Passing threshold raised to 47/56.

**New in v2.0.0 -- The Two-Gate AEO & DOM Flattening Protocols:**
- **The Two-Gate Paradigm Shift** -- traditional metrics like meta descriptions and title tags no longer dictate AI Overview success. The agent now optimizes primarily for Gate 1 (Retrieval Pool Entry) and Gate 2 (Selected Citation Extraction). Entering the candidate pool and getting your passage selected for citation are two different jobs; v2.0.0 optimizes both explicitly.
- **Anti-Paragraph Snippet Answer Rule** -- strict ban on bare `<p>` tags for the primary 2-3 sentence answer beneath an H2. Bare paragraphs are routinely skipped for first-position citations. Primary answers must use block-level structural containers (`div.answer`, `blockquote`, `dl`/`dd`, leading table row, or RDFa/Microdata span block).
- **DOM Nesting Depth Flattening** -- shallow-DOM enforcement. Deeply nested visual-builder output (Elementor, Divi, etc.) is penalized at runtime for node-processing cost and Main Content dilution. Generated layout targets a max ~3 nesting levels; competitor pages exceeding it are flagged as `DOM_FLATTENING_OPPORTUNITY`.
- **Goldilocks Entity Synergy** -- subheadings maintain a precise entity density, strategically repeating core associated entities across H2/H3s to build extraction synergy for citation algorithms. Not too sparse, not stuffed.
- **55-point quality checklist** -- adds Anti-Paragraph Snippet, DOM Flattening Depth, Goldilocks Entity Synergy, and Two-Gate Extraction Pass checks. Passing threshold raised to 46/55.

**New in v1.9.1 -- Decision Fit Mapping + Brand Voice + Missing Spoke Detection:**
- **Brand differentiator injection** via `--differentiators` on `research.py` (e.g. `--differentiators="women-owned, 24/7 service, no hidden fees"`). Passes through to the brief output so the writing agent has strict brand constraints. Differentiators must be woven verbatim into the 500-token chunks and surfaced in the AI Summary Nugget -- paraphrased fluff fails the new Brand Identity check.
- **Missing Spoke Detection** -- the research pipeline now extracts internal-link anchor text from the top 3 competitors, filters out navigational generics (Home, Contact Us, Privacy, FAQ, etc.) and image-link leakage, and outputs a ranked `missing_spokes` list. SKILL.md Section 12 now requires every generated page to append a `## Recommended Spoke Pages` section built from this data.
- **Decision Fit Mapping** -- new checklist enforcement: heading structure must map to the user's psychological buying stage (Research / Compare / Buy) instead of copy-pasting competitor H2s.
- **Execution Protocol now prompts for differentiators** if the user didn't supply them up front -- the agent stops and asks before writing rather than producing generic AI homogenization.
- **51-point quality checklist** -- adds Decision Fit (#49), Brand Identity (#50), Topical Silo (#51) checks. Passing threshold raised to 42/51.

**New in v1.9.0 -- Massive Web Render as primary content parser:**
- **Massive Web Render** (render.joinmassive.com) is now the primary competitor content parser when `MASSIVE_API_TOKEN` is configured. Returns clean rendered markdown including JS-loaded content that DataForSEO's `content_parsing/live` endpoint misses.
- **Graceful per-URL fallback to DataForSEO** -- if Massive errors or returns empty for any single URL, that URL falls back to DataForSEO. A partial Massive outage cannot break a research run.
- **SERP organic results and keyword data continue to come from DataForSEO** -- Massive's `/search` endpoint only returns "also-searched" query suggestions, not organic results, so the SERP path is unchanged.
- **`content_parsers` field added** to research output so you can see exactly which parser handled each URL (e.g. `{"massive": 4, "dataforseo-fallback": 1}`).
- Setup: add `MASSIVE_API_TOKEN=...` to `~/.config/seo-agi/.env`. No token = skill runs in pure DataForSEO mode exactly as before.

**New in v1.8.0 -- Gemini 3.5 Flash RAG Optimization + Off-Page Trust Expansion:**
- **DOM Vectoring & Shard Extraction Compliance** (Section 6) -- Google's AI Overviews are built by Gemini 3.5 Flash running a RAG pipeline that extracts structural "shards" from the raw HTML DOM. JSON-LD in `<head>` is no longer sufficient by itself: critical data points must live in front-facing `<table>` markup or inline RDFa spans where a clean-session crawler can see them without JavaScript execution.
- **Trust Pilot as Tier 1 Tributary** -- added to the Tributary Trust Protocol as a first-class Tier 1 asset. Trustpilot is now a highly weighted trust/relevance signal for LLMs and demonstrably shifts brand description vectoring in Gemini and ChatGPT within 48 hours of publication.
- **Off-Page Schema Injection** -- new Tier 1 tactic. Embedding `Organization` and `Person` JSON-LD schema in third-party properties (Cloud Pages, press releases) with explicit links back to the brand's Google Business Profile CID blocks Google's NavBoost from rank-shuffling the money page during A/B exposure tests.
- **Tributary network spread updated** from 4/5 Tier 1 assets to 5/7 to account for the two new asset types.
- **48-point quality checklist** -- adds Trust Pilot profiling, off-page schema mapping, and DOM-visible data point checks. Passing threshold raised to 39/48.

**New in v1.7.1 -- LLM Retrieval & Substantive Content Protocols:**
- **Meta-Specific Entity Isolation** -- competitor SERP descriptions are mined for the bolded query-matched terms (the snippet entities Google itself surfaces), not generic body entities. These become the primary entity set the brief must cover, because they are the exact tokens already validated as relevant by Google's snippet generator.
- **Bigram / Trigram AI Alignment** -- top 3 ranking competitors' body text is tokenized to extract the top 5 bigrams and top 5 trigrams. The AI Summary Nugget (top of page, position zero for LLM retrieval) must include 2 or more of these n-grams verbatim. AI retrieval scoring rewards token-window overlap with consensus phrasing -- this is how you align with what the LLM has already learned the topic "looks like."
- **Primary + Secondary Intent Mapping (Orcas 1)** -- single-intent pages underperform. Every page now maps Primary intent (the question the user typed) into the first 500 tokens AND Secondary intent (the action funnel: compare, book, contact, calculate) into the next two chunks. Pages without a secondary action path fail the dual-intent check.
- **The 410 Prune Protocol** -- on rewrites, every legacy URL gets an explicit status-code recommendation. 301 preserves equity when the topic survives. 410 prunes thin, cannibalizing, or out-of-topical-circle pages so they stop dragging the domain. Silent leave-as-is is no longer an acceptable output for a legacy URL audit.
- **Local Codebase Contextual Linking** -- when the skill is run inside a project repo, it scans the local file structure (`.tsx`, `.md`, `.html`, etc.), detects the framework, injects semantic HTML directly into source files where appropriate, and emits `.htaccess` / Nginx / `next.config.js` redirect snippets for the 410 recommendations. The skill writes ranking pages, not just content briefs.
- **45-point quality checklist** -- adds Meta Entity Isolation, N-Gram Alignment, Dual-Intent, and Status Code Governance checks.

**New in v1.6.0 -- ICP-Driven Content + Local Trust Signals:**
- **Ideal Customer Persona (ICP) Integration** -- page briefs now require a defined ICP with demographics, psychographics, and specific pain points. Content maps to who it's actually for, not a generic audience.
- **Deep Entity History & Identity Tags** -- founding dates, generational ownership, and identity attributes (women-owned, veteran-owned, family-owned) are now explicit entity signals. Maps directly to GBP tags and conversational AI filtering.
- **The Self-Placement Rule** -- ranking the client #1 in a listicle is now an approved tactic, provided the entry is strictly objective with a defined use-case and honest tradeoffs.
- **Keyword Cannibalization Governance** -- strict rule against creating pages that compete with existing URLs for the same intent. Sales-focused duplicates of informational pages get tagged with `noindex` recommendation.
- **41-point quality checklist** adding ICP alignment, entity history, and cannibalization checks.

**New in v1.5.0 -- Forensic SEO + Structural Signals:**
- **Semantic HTML Containers** -- generated HTML now uses `<article>`, `<section>`, `<aside>`, `<main>` instead of generic `<div>`. Google's crawler uses these elements to identify the Main Content zone for passage extraction and AI retrieval.
- **Proof-Term Proximity** -- supporting evidence (numbers, entity names, operational details) must live in the same 500-token chunk as the H2 it supports. BERT evaluates within the passage window, not page-wide. Orphaned proof terms don't help.
- **QDD Vulnerability Check** -- UGC (Instagram, Pinterest, Reddit) ranking for a commercial keyword is a structural gap, not a signal to avoid. Flag as HIGH_CONFIDENCE_TAKEOVER.
- **Site Over Page Rule** -- generalist competitors ranking with one page are vulnerable to specialist site architecture. Niche Site Pivot trigger fires when 2/3 top results are generalist pages.
- **Query Fan-Out (QFO) Facet Coverage** -- each 500-token chunk now targets a specific AI sub-query. 40% of future traffic arrives via AI fan-out from a single user prompt.
- **Forensic EMQ Check** -- EMQ in H1 is conditionally required when 2/3 top competitors use it. Competitive context overrides the default entity-based heading rule.
- **Orcas One CVR Modeling** -- keywords now ranked by estimated conversion value, not raw volume. Position 1 at 4.5% CVR vs position 7 at 2%.
- **38-point quality checklist** with QDD, Site vs. Page, EMQ ratio, and QFO facet checks.

**New in v1.4.0 -- March 2026 Update Protocols:**
- **NavBoost Geographic Click Relevance** -- pages now reranked by geographic click patterns. Local pages require neighborhood-level specificity, not just city names. Observed across SEO X community testing.
- **Click Satisfaction as Primary Signal** -- Google watches if users are satisfied after clicking. Content must deliver value in the first 3 chunks or rankings drop regardless of quality. Confirmed via practitioner NavBoost analysis.
- **AI Overview Link Optimization** -- earning a link inside AI Overviews drives 70-80% CTR. Pages structured for snippet extraction with clean tables and FAQ markup.
- **AI Overview Theft Defense** -- rising impressions + falling clicks = your content cited without credit. Interactive elements (calculators, widgets) defend against extraction.
- **QDD (Query Deserves Diversity)** -- Google pulls diverse results into overviews. Information Gain Test now critical for QDD survival.
- **FHASS Replaces YMYL** -- Financial, Health, And Safety, and Security. Expanded scrutiny for risk-adjacent content. Discussed in Google Cloud documentation updates.
- **Banned 2026 Content Patterns** -- generic AI FAQs, 300-word thin pages, blog rolls outside topical circle all confirmed penalized.
- **34-point quality checklist** with geographic specificity, click satisfaction, FHASS compliance, and minimum 1,500-word depth checks.

**New in v1.3.0 -- 2026 SEO Protocols:**
- **AI Summary Nuggets** -- every page opens with a 200-character fact-dense block designed for Perplexity/Gemini/ChatGPT to cite as a consensus source. Position zero for LLM retrieval.
- **Original Research Block** -- mandatory data experiment or first-hand observation section. Google's highest-priority E-E-A-T signal: Experience. Pages without original research cap at 20/28.
- **Map Traffic Shifting** -- internal links from high-traffic informational pages to map embeds, shifting engagement signals toward local intent.
- **Spam Resilience** -- quality scoring now prioritizes technical relevance density over "human tone." Factually perfect content is not downgraded for sounding clinical.
- **Recursive Fact-Checking** -- every claim validated against 2+ high-ranking sources for Entity Consensus before delivery.
- **28-point quality checklist** with mandatory printed scorecard at the end of every output.

**New in v1.2.0 -- Anti-Spam Ranking Signals:**
- Single H1 rule, no exact-match keyword in meta descriptions or subheadings
- No keyword-stuffed alt text, no duplicate content
- Internal linking requirements, broken backlink awareness
- Interactive elements (calculators, widgets) to defend against AI Overview traffic loss

**New in v1.1.0 -- GEO Framework Additions:**
- RAG Targeting: zero-volume long-tail queries that "train" AI to cite your domain
- Topical Circle Audit: stay inside your core service topic or dilute AI authority
- Off-Page Sequencing: establish third-party brand footprint before on-page SEO
- Reddit Subdomain Indexing: seed entity consensus across indexed Reddit layers
- Ask Maps / Conversational GBP Optimization
- FAQ/PAA section and JSON-LD schema now mandatory in every output

**I built this because I got tired of the gap between "SEO audit" and "published page."** I've been doing SEO for 20+ years in ground transportation (1M+ bookings, 2M+ rides across my companies). The workflow was always the same: pull SERP data, analyze competitors, find gaps, write brief, write page, add schema, publish. Over and over. So I turned that entire workflow into a single skill that any AI agent can execute.

The result? I used this to research a competitor's best-performing pages, built equivalent content with `/seoagi`, bought the exact-match domains, and every single page is ranking on page 1. That's not theory. That's the workflow.

---

## What It Actually Does

```
You: /seoagi "best project management tools 2026"

SEO-AGI:
  1.  Pulls SERP top 10 via DataForSEO
  2.  Parses competitor content (word count, headings, topics covered)
  3.  Extracts People Also Ask questions
  4.  Pulls related keywords with search volumes
  5.  Maps Primary intent (top of page) and Secondary intent (action funnel
      below the fold) per the Orcas 1 dual-intent model
  6.  Generates a data-driven content brief
  7.  Writes the complete page (Markdown + YAML frontmatter)
  8.  Extracts top bigrams/trigrams from top 3 competitors and seeds 2+ of
      them into the 200-char AI Summary Nugget for LLM-retrieval alignment
  9.  Adds FAQ section from real PAA data
  10. Generates JSON-LD schema markup + inline RDFa entities
  11. Validates every claim against 2+ sources (Entity Consensus)
  12. For rewrites: evaluates each legacy URL and recommends 301 (when topic
      survives and equity should consolidate) or 410 (when the URL is thin,
      cannibalizing, or out-of-circle and should be pruned)
  13. Validates against 66-point quality checklist
  14. Prints scorecard so you see exactly what passed
```

For rewrites, point it at any URL. It compares your page against the current top 3 ranking competitors, identifies exactly what you're missing, and rewrites with a change summary explaining every edit.

---

## The SEO Knowledge Inside

This isn't a wrapper around "write me an SEO article." The skill encodes strategies from the best in the game:

**Traditional SEO**
- Intent-first content architecture (match what searchers actually want, not what you think the keyword means)
- Competitive word count targeting (page length based on what's ranking, not arbitrary "write 2000 words")
- Heading hierarchy derived from SERP analysis (not templates, not guesswork)
- People Also Ask coverage as FAQ sections (answer the questions Google already knows people are asking)
- Schema markup patterns by page type (FAQPage, LocalBusiness, HowTo, Product, BreadcrumbList)
- Internal linking suggestions based on actual site data from GSC

**GEO / LLM SEO (Generative Engine Optimization)**
- 200-char AI Summary Nugget at top of every page, designed for Perplexity/Gemini/ChatGPT to cite as a consensus source
- 500-token chunk architecture matching Google AI's retrieval window
- Content structured for AI citation (Perplexity, ChatGPT, Google AI Overviews)
- Entity-rich writing that LLMs can extract and reference
- Depth-over-length philosophy (comprehensive coverage that becomes the authoritative source)
- FAQ patterns that match how AI systems parse and surface answers
- Data-backed claims that AI systems prefer to cite over vague assertions
- RAG targeting: zero-volume long-tail queries that "train" AI to cite your domain
- Off-page sequencing: establish third-party brand footprint before on-page SEO
- Reddit subdomain indexing: seed entity consensus across indexed Reddit layers
- Topical circle enforcement: stay inside your core service topic to avoid diluting AI authority signals
- Recursive fact-checking: every claim validated against 2+ high-ranking sources for Entity Consensus
- Spam resilience: technical relevance density prioritized over "human tone" in quality scoring

**Structural & DOM Signals**
- Semantic HTML containers: `<article>`, `<section>`, `<aside>`, `<main>` in generated HTML for Main Content zone identification
- Proof-term proximity: supporting evidence must live in the same 500-token chunk as its H2 (BERT evaluates within passage window, not page-wide)
- Query Fan-Out facet coverage: each chunk answers a distinct AI sub-query for multiplicative retrieval
- Forensic EMQ check: conditionally require exact-match keyword in H1 based on competitor optimization ratio
- QDD vulnerability detection: UGC in top 10 = HIGH_CONFIDENCE_TAKEOVER opportunity flag
- Site-level entity dominance: niche site architecture beats generalist single-page competitors

**Local / GBP Optimization**
- Ask Maps & conversational GBP optimization (structured data that answers "who has X available?")
- Holiday/exception hours, discrete service items, pre-populated Q&A
- GBP fields treated as AEO markup, not optional admin work
- Map traffic shifting: internal links from high-traffic informational pages to map embeds to boost local engagement signals

**Content Quality Signals (2026 protocols)**
- Mandatory Original Research / Data Experiment block in every page (Google's top E-E-A-T signal: Experience)
- Verification tagging system: every claim tagged with `{{VERIFY}}`, `{{RESEARCH NEEDED}}`, or `{{SOURCE NEEDED}}`
- "Not For You" block: honest section telling readers when this option is a bad fit (trust signal competitors skip)
- Information Gain Test: every page must contain content not found in the top 10 Google results

**The 66-point quality checklist every page runs through (selected highlights):**
- Information gain over top 10 Google results? Check.
- Reddit Test: would a practitioner upvote this? Check.
- Core answer in first 150 words? Check.
- Fast-scan summary within first 200 words? Check.
- 2+ hard operational Prove-It facts? Check.
- Real HTML tables (not bullet lists)? Check.
- Every section doing a unique job (no repetition)? Check.
- All specific numbers tagged with `{{VERIFY}}`? Check.
- All citations specific and traceable? Check.
- "Not For You" block present? Check.
- 500-token chunk architecture? Check.
- No banned phrases or patterns? Check.
- Word count within competitive range? Check.
- JSON-LD schema block matching page type? Check.
- FAQ section with 3+ PAA questions? Check.
- Hub/spoke internal links? Check.
- Title tag <60 chars with target keyword? Check.
- Meta description <155 chars with value prop? Check.
- Content inside site's core topical circle? Check.
- `reddit_test` and `information_gain` in frontmatter? Check.
- Single H1 tag only? Check.
- No exact-match keyword in meta description? Check.
- No keyword stuffing in H2/H3/H4 tags? Check.
- Image alt text descriptive, not keyword-stuffed? Check.
- AI Summary Nugget (200-char) at top of page? Check.
- Original Research / Data Experiment block present? Check.
- Map-to-informational internal link (local pages)? Check.
- Every claim validated against 2+ sources? Check.

- QDD check run -- UGC in top 10 flagged or cleared? Check.
- Site vs. Page audit -- competitor type identified? Check.
- Forensic EMQ ratio checked -- applied correctly? Check.
- Each 500-token chunk targets a distinct QFO facet? Check.
- ICP defined in brief and content tailored to their pain points? Check.
- Deep entity history / identity tags included where applicable? Check.
- No keyword cannibalization with existing site URLs? Check.
- Meta Entity Isolation -- entities pulled from competitor SERP snippets, not body? Check.
- N-Gram AI Alignment -- 2+ bigrams/trigrams in AI Summary Nugget? Check.
- Dual-Intent -- Primary intent in first 500 tokens + Secondary action funnel? Check.
- Status Code Governance -- explicit 301 or 410 for every legacy URL? Check.
- Trust Pilot entity profiling with exact service target bigrams? Check.
- Off-page assets mapped with cross-cutting Organization/Person schema to GBP? Check.
- Critical data points visible in raw HTML DOM (not buried solely in JSON-LD)? Check.
- Decision Fit -- heading structure maps to buyer stage (Research/Compare/Buy), not copied competitor H2s? Check.
- Brand Identity -- client differentiators woven verbatim into chunks + AI Summary Nugget? Check.
- Topical Silo -- `Recommended Spoke Pages` section appended from `missing_spokes`? Check.
- Anti-Paragraph Snippet -- primary H2 answers in block containers, not bare `<p>`? Check.
- DOM Flattening -- layout flat (max ~3 nesting levels), no wrapper-node bloat? Check.
- Goldilocks Entity Synergy -- subheadings repeat core entity pairings, not generic text? Check.
- Two-Gate Extraction -- satisfies Gate 1 retrieval AND Gate 2 citation extraction? Check.
- Anti-NLP Stuffing -- body free of force-repeated NLP-tool entity lists (de-indexation risk)? Check.
- Local Isolation -- local page targets one service+place, no multi-service stacking? Check.
- GBP Inner-Link Directive -- local page tells user to point GBP at this URL, not homepage? Check.
- Outbound Citations -- 5+ descriptive links to external authoritative sources? Check.
- Strict Phrase Placement -- exact match in Title and H1 only, never H2/H3/H4? Check.
- Entity-Fact Pairing -- entities bound to hard verifiable facts, not just named? Check.
- Intent Divergence -- CTAs stripped if informational, awards featured if local? Check.
- Anti-Boilerplate -- internal links contextual, no repeated site-wide blocks? Check.
- Off-Page Embed -- Tier 1 draft carries a Maps embed where the platform allows? Check.
- Unlinked Citation -- plain-text brand and URL mentions alongside the link? Check.
- SSR/SSG -- internal links present in the raw HTML DOM, not JS-injected? Check.

Pages scoring below 57/66 get flagged with specific items to fix. The scorecard is printed at the end of every output so you see exactly what passed.

---

## Data Integrations (BYOK)

Bring your own API keys. Use one, use all. The skill adapts:

| Integration | What It Provides | Required? |
|---|---|---|
| **DataForSEO** | Live SERP results, keyword volumes, People Also Ask, competitor content parsing | Yes (core) |
| **Google Search Console** | Your actual query data, CTR, positions, cannibalization detection | Optional |
| **Ahrefs** (via MCP) | Backlink profiles, domain authority, referring domains | Optional |
| **SEMRush** (via MCP) | Traffic estimates, keyword gaps, competitive positioning | Optional |

No keys at all? The skill falls back to web search. You lose precision but the workflow still runs.

---

## Install + Setup

### Step 1: Install the skill

**Claude Code (Mac app / CLI):**
```bash
git clone https://github.com/gbessoni/seobuild-onpage.git ~/.claude/skills/seobuild-onpage
```

**OpenClaw:**
```bash
git clone https://github.com/gbessoni/seobuild-onpage.git ~/.agents/skills/seobuild-onpage
```

**Codex:**
```bash
git clone https://github.com/gbessoni/seobuild-onpage.git ~/.codex/skills/seobuild-onpage
```

Then **restart your agent** so it picks up the new skill. Skills are loaded at session start, so a running session will not see it.

**Updating later:**
```bash
cd ~/.claude/skills/seobuild-onpage && git pull
```

If you have local changes (an edited `.env.example`, for example), stash them first so the pull does not abort:
```bash
cd ~/.claude/skills/seobuild-onpage && git stash && git pull && git stash pop
```

### Step 2: Install Python dependency

```bash
pip install requests
```

### Step 3: Configure API keys (optional but recommended)

```bash
mkdir -p ~/.config/seo-agi
cp ~/.claude/skills/seobuild-onpage/.env.example ~/.config/seo-agi/.env
```

Then edit `~/.config/seo-agi/.env` with your keys:

```env
# DataForSEO -- sign up at https://dataforseo.com (~$0.002/query)
DATAFORSEO_LOGIN=your_email@example.com
DATAFORSEO_PASSWORD=your_password

# Google Search Console (optional)
GSC_SERVICE_ACCOUNT_PATH=/path/to/service-account.json
```

**No API keys?** The skill still works. It falls back to Ahrefs/SEMRush MCP tools (if connected) or web search. You lose SERP content parsing but the framework still writes quality pages.

### Step 4: Verify it works

```bash
# Test the research pipeline (uses mock data, no API keys needed)
python3 ~/.claude/skills/seobuild-onpage/scripts/research.py "airport parking JFK" --mock --output=compact
```

You should see SERP results, PAA questions, related keywords, and heading structure data. If you see that, you're good.

### Step 5: Use it

Open Claude Code (or OpenClaw, or Codex) and type:

```
Write an SEO page for "airport parking JFK"
```

The skill auto-triggers on SEO content requests. It will:
1. Run the research script to pull competitive data
2. Show you a content brief and confirm before writing
3. Write the full page following the SEO-AGI framework
4. Validate against the quality checklist
5. Save to `~/Documents/SEO-AGI/pages/`

---

## Verify Your Setup (Troubleshooting)

**Check if the skill is installed:**
```bash
ls ~/.claude/skills/seobuild-onpage/SKILL.md && echo "Installed" || echo "Not found"
```

**Check if API keys are configured:**
```bash
cat ~/.config/seo-agi/.env 2>/dev/null || echo "No .env file -- skill will use fallback mode"
```

**Test with live DataForSEO (if you have keys):**
```bash
python3 ~/.claude/skills/seobuild-onpage/scripts/research.py "best crm software" --output=compact
```

**Run unit tests:**
```bash
cd ~/.claude/skills/seobuild-onpage
python3 tests/test_env.py && python3 tests/test_serp_analyze.py && python3 tests/test_dataforseo.py
```

---

## Use Cases

**Exact-match domain play**: Research competitor's top pages with OpenClaw, generate equivalent content with `/seoagi`, buy the domains, publish. Page 1.

**Location page generation**: `/seoagi "plumber in [city]"` x 50 cities. Each page gets city-specific research, local PAA questions, LocalBusiness schema. Not cookie-cutter templates.

**Content refresh**: Point it at your underperforming URLs. It pulls your actual GSC data, compares against current top 3, and tells you exactly what to add, expand, or restructure. Then does it.

**Competitive intelligence**: `/seoagi research "competitor keyword"` gives you the full landscape without writing anything. Word count ranges, heading structures, topic gaps, related keywords with volumes.

**Brief handoff**: `/seoagi brief "keyword"` generates a structured content brief you can hand to a human writer. Research-backed, not vibes-based.

---

## The Workflow That Got Me Here

I've been running this workflow manually for 20 years across ParkingAccess.com (1M+ bookings) and Shuttlefare.com (2M+ rides). The pattern never changed:

1. Find what's ranking
2. Figure out what they cover that you don't
3. Write something deeper
4. Add the technical SEO (schema, meta, structure)
5. Publish and move on

seobuild-onpage is that pattern, automated. The 20 years of pattern recognition compressed into a SKILL.md file, backed by live data APIs, running inside a super agent that can decompose and parallelize the work.

It's not AI replacing SEO expertise. It's SEO expertise finally having the right delivery mechanism.

---

## Testing

See "Verify Your Setup" above for full test commands. Quick version:

```bash
cd ~/.claude/skills/seobuild-onpage

# Unit tests (no API keys needed)
python3 tests/test_env.py && python3 tests/test_serp_analyze.py && python3 tests/test_dataforseo.py

# Mock mode (full pipeline with fixture data)
python3 scripts/research.py "airport parking JFK" --mock --output=compact

# No-creds mode (returns skeleton for agent to fill via MCP/WebSearch)
python3 scripts/research.py "test keyword" --output=compact
```

---

## Contributing

Open source, MIT license. PRs welcome.

The skill is modular. Want to add a new page template? Edit `references/page-templates.md`. New schema pattern? `references/schema-patterns.md`. Better quality checks? `references/quality-checklist.md`. New data source? Add a client in `scripts/lib/` and wire it into `research.py`.

---

## Credits

Built by [Greg Bessoni](https://github.com/gbessoni) ([@gregbessoni](https://x.com/gregbessoni)).

## License

MIT
