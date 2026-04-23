# v0.2 War Panel — Strategic Decision Consult
**Date:** April 21, 2026 (PM, post-v0.2 ship)
**Target panels:** ChatGPT, Gemini, Perplexity, Grok — identical prompt, simultaneous fire
**Synthesis target:** `Security+ Study Command Center/HARDSEAL-AI-DETECTION-V0.2-NEXT-MOVE — WAR PANEL SYNTHESIS.md`

Paste the block below verbatim into each panel. Identical input -> comparable output -> clean synthesis.

---

I am Rico Allen, solo founder of Hardseal — a stdlib-only Python CMMC Level 2 compliance platform. North Star: own the trust layer of AI-era defense compliance. The 90-day wedge is `mismatch_engine_ai.py`: a stdlib-only detector for AI-generated and AI-contaminated evidence in CMMC L2 readiness packets.

**Shipped today (April 21, 2026):**

v0.1 (AM): 6 heuristics (SentenceStructure, BoilerplateCluster, TimestampRegularity, MappingDensity, CitationGraph, PromptLeakage). 22 tests green. Demo: clean packet CLEAN @ 0.13; contaminated packet LIKELY_SYNTHETIC @ 1.0.

v0.1 red-team (midday, four-panel fire — YOU were one of the panels). Unanimous: (1) legitimate consultant-templated packets false-positive; (2) missing 7th heuristic around provenance/grounding. Verdict: 3-NO / 1-CONDITIONAL-YES.

v0.2 (PM): shipped `template_guard.py` (NIST/CMMC stock-phrase whitelist + user-baseline-template shingle ingestion) and `ArtifactSpecificityIndex` (grounding-token ratio — versions, hex hashes, IPs, paths, ticket IDs, emails, dates, filenames, crypto+bits, hw models, protocol+version, durations — vs named mechanisms). Weight rebalance: PromptLeakage 0.25 to 0.15, TimestampRegularity 0.20 to 0.25, ArtifactSpecificityIndex 0 to 0.20. **48 tests passing. 1,809 LOC. Regression sample locked.** Proof: 4-control consultant-templated packet scored CONTAMINATED @ 0.518 bare v0.1 -> CLEAN @ 0.0 guarded v0.2. AI-residue-poisoned packet still scores SYNTHETIC.

**Business state:** zero paying customers, $0 revenue, personal-savings runway. Target: $5K-$8K AI-detection overlay inside a $3K-$5K Readiness Pack, sold to small DIB contractors before November 10, 2026 Phase 2 enforcement. No competitor (Vanta, Drata, Secureframe) is detecting AI contamination. First to name the category wins.

**Which move is highest-leverage next?**

A. **PAPER** — draft *State of AI-Era Defense Compliance Evidence.* 12 attack-pattern sections, 3 pages, each with stdlib detection signature + NIST 800-171A mapping. Publish PDF + HTML on hardseal.ai. Category capture before the code gets forked.

B. **COMMITMENT HASH** — move weights + full regex list to `config/*.json`; publish SHA-256 in README. Open repo ships a 10-phrase starter list + every class. Enables the "methods public, tuning lagged" credibility story.

C. **PILOT OUTREACH** — cold-email 5 DIB contractors this week, offer $5K-$8K AI-detection overlay. Get first revenue + real-world evidence packets for v0.3 calibration.

D. **MORE HEURISTICS** — TerminologyDrift, CrossArtifactEntity, EditLineageCoherence. Framework completeness before paper.

**Answer these five questions. Under 700 words total. No hedging.**

1. Rank A/B/C/D for 90-day Revenue North Star AND 10-year trust-layer mission. Justify the ranking.

2. What breaks first if I pick your #1 and ignore the others?

3. Is there a 0-th option that dominates all four? If yes, name it. If no, say so.

4. Paper specifically: outline (1 day) + draft (3 days) + publish PDF+HTML on hardseal.ai — what percent of the category-capture value do I capture vs waiting for peer review / conference / journal? Give a single number.

5. Pilot outreach specifically: with v0.2 in the bank, zero field data, zero testimonials — realistic expected value of cold-emailing 5 DIB contractors this week? Conversion rate, cycle time, dollar expectation.

End with one sentence: ship the paper this week, ship the commitment hash this week, do pilot outreach this week, or stay heads-down on heuristics. Pick one.
