# Content Quality Checklist

SEO-AGI validates every page against this checklist before final output.
Each item is scored pass/fail. Pages scoring below 80% get flagged with
specific items to fix.

## Title Tag (10 points)

- [ ] Contains target keyword (or close variant)
- [ ] Under 60 characters
- [ ] Unique and compelling (not just "[Keyword] | [Brand]")
- [ ] Includes a differentiating element (year, number, qualifier)
- [ ] Not duplicating another page's title on the same site

## Meta Description (10 points)

- [ ] Under 155 characters
- [ ] Contains target keyword naturally
- [ ] Includes a call-to-action or value proposition
- [ ] Not a copy of the first paragraph
- [ ] Would make someone click vs competitors in the SERP

## Heading Structure (15 points)

- [ ] Exactly one H1
- [ ] H1 closely matches or mirrors title tag
- [ ] Logical H2 > H3 hierarchy (no skipped levels)
- [ ] H2 count within competitive range (see analysis)
- [ ] Headings are descriptive (not "Section 1" or "More Info")

## Content Depth (25 points)

- [ ] Word count within competitive range (not arbitrarily long or short)
- [ ] Answers at least 3 People Also Ask questions
- [ ] Includes specific data, statistics, or concrete examples
- [ ] Covers topics that appear in 2+ competitor pages
- [ ] No thin sections (every H2 has 150+ words of substance)

## Search Intent Match (15 points)

- [ ] Page type matches detected intent (informational/commercial/transactional)
- [ ] Content format matches SERP expectations (list vs guide vs comparison)
- [ ] Addresses the primary user need within the first 200 words
- [ ] If commercial intent: includes pricing or comparison elements
- [ ] If informational intent: includes step-by-step or explanatory depth

## Technical SEO (15 points)

- [ ] JSON-LD schema markup included and matches page type
- [ ] Schema uses correct types (see schema-patterns.md)
- [ ] Image alt text suggestions included
- [ ] At least 2 internal link suggestions with context
- [ ] No orphaned sections (every section connects to the page's topic)

## Readability (10 points)

- [ ] No keyword stuffing (target keyword appears naturally, not forced)
- [ ] Paragraphs are scannable (no walls of text)
- [ ] Uses formatting aids where appropriate (bold key terms, tables for comparisons)
- [ ] Transitions between sections are logical
- [ ] Reads like it was written by a subject matter expert, not a content mill

## Scoring

| Score | Rating | Action |
|---|---|---|
| 90-100 | Exceptional | Ship it |
| 80-89 | Strong | Minor tweaks optional |
| 70-79 | Acceptable | Fix flagged items before publishing |
| 60-69 | Below standard | Significant revision needed |
| <60 | Rewrite | Start over with revised brief |

## Red Flags (automatic fail)

These issues override the score and require fixing regardless:

- Duplicate title tag matching another page on the site
- Missing H1 or multiple H1 tags
- Zero data/statistics in the entire page
- Word count more than 50% below competitive median
- No FAQ or PAA coverage
- Missing schema markup entirely
- Keyword density above 3% (stuffing)

---

## v1.7.1 -- 45-Point Pass/Fail Checklist

In addition to the rubric above, every page must pass the SKILL.md 66-point YES/NO checklist (Section 14). Pages scoring below 57/66 require revision before delivery. The four checks added in v1.7.1:

- [ ] **#42 -- Meta Entity Isolation Check.** The entity set used in the brief was sourced from the bolded query-matched terms inside competitor SERP descriptions (`research.meta_entities`), not from generic body-content entity extraction. Snippet entities are the tokens Google's own snippet generator already validated as relevant.
- [ ] **#43 -- N-Gram AI Alignment Check.** The AI Summary Nugget at the top of the page contains 2 or more bigrams or trigrams pulled verbatim from the top 3 ranking competitors' body text (`research.target_ngrams`). LLM retrieval scoring rewards token-window overlap with consensus phrasing.
- [ ] **#44 -- Dual-Intent Check.** Primary intent (`research.primary_intent`) is satisfied within the first 500 tokens AND a Secondary action funnel (`research.secondary_intent`) is present in the next two chunks. Single-intent pages fail this check.
- [ ] **#45 -- Status Code Governance.** For rewrites only. Every legacy URL evaluated has an explicit `301` (preserve equity, topic survives) or `410` (prune, thin/cannibalizing/out-of-circle) recommendation. Silent leave-as-is is a fail.

---

## v1.8.0 -- Gemini 3.5 Flash RAG + Off-Page Trust (48-Point)

Three new checks for the AI-Overview era. Pages scoring below 39/48 require revision before delivery.

- [ ] **#46 -- Trust Pilot Entity Profiling.** A Trust Pilot profile (or scheduled draft for one) exists for the target brand, with the page's exact service target bigrams (from `research.target_ngrams`) seeded into the profile description. See SKILL.md Section 11A for why Trustpilot now counts as Tier 1.
- [ ] **#47 -- Off-Page Schema Mapping.** Companion content on Tier 1 properties (Cloud Pages, PRs, Medium, etc.) carries `Organization` and `Person` JSON-LD with explicit links back to the brand's GBP CID. This is the NavBoost-shuffle defense.
- [ ] **#48 -- DOM-Visible Critical Data.** Pricing tables, capacity figures, schedules, and other primary data points appear in front-facing `<table>` markup or inline RDFa spans -- not buried solely in a JSON-LD block. Google's RAG pipeline (Gemini 3.5 Flash) extracts shards from the rendered DOM, not from `<head>` script tags.

---

## v1.9.1 -- Decision Fit, Brand Voice, Missing Spokes (51-Point)

Three new checks for buyer-stage alignment, brand identity preservation, and topical silo completeness. Pages scoring below 42/51 require revision before delivery.

- [ ] **#49 -- Decision Fit Check.** Does the heading structure map directly to the user's psychological buying stage (Research, Compare, or Buy) instead of just copying competitor H2s? A "best CRM 2026" page (Compare stage) needs comparison-shaped H2s. A "how to choose a CRM" page (Research stage) needs framework-shaped H2s. A "Salesforce pricing" page (Buy stage) needs decision-shaped H2s. Copy-paste of competitor headings is a fail -- the page must serve the searcher's job, not mirror the SERP.
- [ ] **#50 -- Brand Identity Check.** Are the client's specific differentiators (provided via `--differentiators=` on `research.py` or in the brief) explicitly woven verbatim into the 500-token chunks to prevent generic AI homogenization? Each differentiator must appear at least once in body content, and the AI Summary Nugget at the top must surface at least one of them. Paraphrasing into marketing-flavored synonyms is a fail -- the exact phrase the client gave is the test.
- [ ] **#51 -- Topical Silo Check.** Did the agent append a `## Recommended Spoke Pages` block at the bottom using the `missing_spokes` data extracted from competitor analysis? See `research.missing_spokes` in the research output. The list is the client's build-order priority for filling the topical silo gap, not link stubs to be written today. Tag uncertain slugs with `{{MANUAL CHECK: slug needed}}`.

---

## v2.0.0 -- Two-Gate AEO & DOM Flattening (55-Point)

Four new checks for the Two-Gate AEO framework and runtime DOM optimization. Pages scoring below 46/55 require revision before delivery. See SKILL.md "NEW IN v2.0.0" and Sections 3 + 6 for the full protocols.

- [ ] **#52 -- Anti-Paragraph Snippet Check.** Are the primary 2-3 sentence answers directly beneath H2 headings wrapped in clean block-level structural containers (`<div class="answer">`, `<blockquote>`, `<dl>`/`<dd>`, leading `<table>` row, or RDFa/Microdata span block) instead of bare `<p>` tags? Bare `<p>` answers are routinely skipped for first-position citations (Gate 2 extraction failure). Body prose that is not the primary answer may still use `<p>`.
- [ ] **#53 -- DOM Flattening Depth Filter.** Is the structural DOM layout flat (max ~3 nesting levels from the nearest semantic landmark to the text node) and free of deep wrapper-node bloat? Visual-builder output (`<div><div><div>...`) is penalized at runtime for node-processing cost and Main Content dilution.
- [ ] **#54 -- Goldilocks Entity Synergy Check.** Do subheadings systematically repeat the core associated entity pairings (primary entity + tightest semantic neighbors) to trigger citation weight, instead of generic text ("Overview", "Details", "More Info")? Not too sparse, not stuffed -- deliberate repeated pairings across passages.
- [ ] **#55 -- Two-Gate Extraction Pass.** Does the page explicitly satisfy Gate 1 (retrieval-pool entry: topical relevance, entity coverage, crawler-visible structure) AND structure its data blocks for Gate 2 (selected-citation extraction: liftable block-level answer units)? Entering the pool without extractable blocks is a Gate 2 failure; perfect blocks on an irrelevant page is a Gate 1 failure. Both must pass.

---

## v2.1.0 -- Anti-NLP Stuffing Protocol (56-Point)

One new check enforcing the Anti-NLP Protocol. Pages scoring below 47/56 require revision before delivery. See SKILL.md "The NLP SEO Lie", Section 4 (Structural Entity Placement), and Section 9 Never Do.

- [ ] **#56 -- Anti-NLP Stuffing Check.** Is the body content free of artificially stuffed, repetitive "NLP entities" -- the salience-ranked term lists exported from Surfer SEO, Google's Natural Language API, Clearscope, etc. -- force-repeated in prose to hit a coverage/density number? Practitioner testing links this pattern to ~25% de-indexation. Entities must earn weight through structural placement (headings, table cells, definition terms, schema fields), never through repetition targets. If the page reads like it was written to satisfy a content-score tool, it fails.

---

## v2.2.0 -- Local Isolation & GBP Canonical Link (58-Point)

Two new local-only checks (score N/A pass on non-local pages). Pages scoring below 49/58 require revision before delivery. See SKILL.md "Strict Local Service Isolation" and Section 10.

- [ ] **#57 -- Local Isolation Check.** If this is a local page, is it strictly isolated to one primary service intent (e.g., "Water Heater Repair Anaheim") without bloating the page with unrelated secondary services? Multi-service catch-all pages get truncated by AI parsers -- the extractor cannot form a clean service-to-place association. N services in a city = N separate pages, never one stacked page.
- [ ] **#58 -- GBP Inner-Link Directive.** If this is a local page, is there a clear instruction at the top of the brief telling the user to point their Google Business Profile website field directly at THIS URL (the service+city inner page), not the homepage? A homepage-pointed GBP wastes the strongest local-relevance signal available.

---

## v2.3.0 -- AI SEO Correlation Protocols (63-Point)

Five new checks derived from AI-citation correlation analysis. Pages scoring below 54/63 require revision before delivery. See SKILL.md "NEW IN v2.3.0", Section 3, and Strict Phrase Placement.

- [ ] **#59 -- Outbound Citation Protocol.** Does the page contain at least 5 descriptive outbound links to external sources or evidence? Pages with zero outbound links face severe citation penalties: an engine checking whether the page synthesizes real sources finds nothing to verify against. Anchor text must name the source or the fact, never a bare URL. Destinations must be genuinely authoritative (.gov, .edu, operating authority, primary research, published rate cards). Note: do NOT default these to `rel="nofollow"` -- nofollow has not preserved equity since 2009 and it forfeits the editorial trust signal. Reserve nofollow/sponsored for paid, affiliate, or untrusted links.
- [ ] **#60 -- Strict Phrase Placement.** Is the exact-match keyword restricted strictly to the Title tag and the H1, avoiding H2/H3/H4 entirely? Also absent from meta description and image alt text per Section 9. This is unconditional and supersedes the retired competitor-ratio EMQ logic. Copying an over-optimized competitor's heading pattern imports their demotion risk, not their ranking.
- [ ] **#61 -- Entity-Fact Pairing.** Are core entities explicitly paired with hard, verifiable facts rather than just named? Every entity in a chunk must be bound to a time, place, cost, capacity, frequency, distance, or date in that same chunk. "Lot 9 offers long-term parking" fails. "Lot 9 holds 8,500 spaces and fills by 6am Saturdays at $20/day" passes. Crucial non-obvious information is the highest-weighted retrieval signal because the engine cannot synthesize it from elsewhere.
- [ ] **#62 -- Intent Divergence Check.** If the page is informational or global, are aggressive CTAs, "free estimate" offers, and award mentions stripped? Sales furniture on an informational page makes the engine read it as promotional rather than referential and severely demotes citation rate. If the page is local service targeting Ask Maps, are local project counts, awards, certifications, and brand differentiators featured prominently? Same elements, opposite treatment. Check `research.primary_intent` before applying.
- [ ] **#63 -- Anti-Boilerplate Check.** Are all internal links uniquely contextual rather than repetitive site-wide in-content blocks? A templated link block injected into every page is boilerplate and gets stripped before retrieval. The required `Recommended Spoke Pages` block is exempt only because it is derived per-page from that keyword's own competitor anchors; if two pages produce identical spoke lists, it has become boilerplate and must be regenerated.

---

## v2.4.0 -- Discovery Routes & Off-Page Embeds (66-Point)

Three new checks. Two are off-page-only and score N/A pass on money pages. Pages scoring below 57/66 require revision before delivery. See SKILL.md "NEW IN v2.4.0" and Section 11A.

- [ ] **#64 -- Off-Page Embed.** If this is a Tier 1 off-page draft, does it include an embed pointing at the money entity where the host platform supports one? Default to the **Google Maps embed** of the business location: it is officially supported and renders reliably. An `<iframe>` of the money page works only if that page does not send `X-Frame-Options: DENY` or a restrictive `frame-ancestors` CSP, so verify before relying on it. Google Business Profile pages cannot be framed at all. Medium, LinkedIn, and Reddit strip arbitrary iframes, so on those platforms this scores N/A and the plain-text mention (#65) carries the requirement instead. Do not fail a draft for omitting an embed the platform does not permit, and do not treat the embed as a ranking mechanism: no published evidence shows behavioral signals passing through a third-party iframe.
- [ ] **#65 -- Unlinked Citation Check.** Does the off-page draft include plain-text brand and URL mentions **alongside** the standard HTML link? RAG pipelines read plain text, so bare-text mentions add retrieval coverage that anchor-only linking misses. This supplements link signals while a new domain's links mature; it does not bypass a filter, and Google denies a formal sandbox exists. Plain text is additive, never a replacement for the link.
- [ ] **#66 -- SSR/SSG Validation.** Is the output formatted for a server-side-rendered or statically generated environment, with every internal link present in the raw HTML DOM of the initial server response? Client-side-rendered SPAs are banned as an output target. Google renders JavaScript, but rendering is deferred and imperfect, and JS-injected internal link graphs are routinely missed or crawled late. Answer-engine crawlers handle it materially worse than Googlebot. If the project is a CSR SPA, the fix is prerendering or SSG for content routes. Pairs with the DOM Flattening rule (#53).
