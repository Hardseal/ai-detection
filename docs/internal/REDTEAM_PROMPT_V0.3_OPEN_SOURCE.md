# WAR PANEL PROMPT — THE OPEN-SOURCE DECISION
## Hardseal AI-Detection v0.2, April 21, 2026

**Instructions: this identical prompt is being submitted to ChatGPT, Gemini, Perplexity, and Grok in parallel. Answer as if the other three panels do not exist. Be blunt. No hedging.**

---

## Who we are

I am Rico Allen, solo founder of Hardseal, a stdlib-only Python CMMC Level 2 compliance automation platform. I am a career-changer with zero prior cybersecurity background, 18 months into building, studying Security+ with a June 2026 target and a decade-long trajectory toward CCP / CCA / optional C3PAO ownership. The mission is a single sentence: **"Own the trust layer of AI-era defense compliance."** The path is Code → Paper → Stage.

## What just shipped

**v0.2 of the AI-era evidence contamination detector.** Seven stdlib-only heuristics (SentenceStructureAnomaly, BoilerplateCluster, TimestampRegularity, MappingDensity, CitationGraph, PromptLeakage, ArtifactSpecificityIndex), orchestrated into four confidence tiers, 48 passing tests, TemplateGuard wired in (fixes the unanimous v0.1 red-team false positive on consultant-built SSPs), zero external dependencies. Weights are published. The regex bundles are published. A SHA-256 commitment hash of the combined bundle is published in the README and reproducible via `verify_commitment.py`. Combined bundle hash is `32f1e682…1f42bbf`.

**Field report "State of AI-Era Defense Compliance Evidence"**, drafted and ready to publish April 27, 2026. 10,760 words, 16 sections, 3 appendices, 12 attack patterns (7 with detector code shipping today, 5 with signatures published and code committed by end of May 2026), full NIST 800-171A objective crosswalk, full failure-mode inventory. The paper repeatedly claims the code is MIT licensed and available at `github.com/hardseal/ai-detection`.

**Outreach drafts** ready for post-paper sequence: 3 C3PAO pro-bono shadow-audit pitches, 5 MSP integrator pitches.

## The current state of the code repository

The code lives locally. The README currently says: *"License: Proprietary — Hardseal LLC. Open-source release planned July 2026."* The paper, the outreach, and the commitment-hash story all assume the code is MIT licensed and public at `github.com/hardseal/ai-detection` by ship day.

## Business state

Zero revenue. 203 days to the November 10, 2026 CMMC Phase 2 enforcement deadline. The revenue product is the Readiness Pack ($3K-$5K). The detection engine is the wedge that builds credibility for the pack, not the revenue line.

## The decision

**Option A. Open-source the code now (MIT license).** Push `github.com/hardseal/ai-detection` public before the paper ships April 27. The paper's claims match reality on day one. Risk: adversary has the detection code and can engineer evasion. Cost: one hard Sunday of repository prep (CI, LICENSE, security sweep, docs polish).

**Option B. Keep closed-source. Rewrite paper and outreach to remove MIT license claims.** Offer signed-bundle downloads via hardseal.ai with a "free for assessment use, license required for commercial integration" model. Preserves engine IP. Rewrites several paper sections and all eight outreach drafts. Delays ship of nothing.

**Option C. Hybrid. Publish the paper as scheduled with the code under a source-available license (e.g., Business Source License, converting to MIT after 2 years).** Public readable, commercially restricted. Mid-way between A and B on IP and credibility.

**Option D. Delay paper ship by 2–4 weeks to do a proper open-source release.** Security audit, polish docs, set up CI, cleaner tests, contributor guide, code signing. Open-source when it lands with a ship-quality release rather than racing to ship.

## Five questions

1. **What is the correct move for a founder trying to own the "trust layer" of a regulated-industry compliance category where the customer (C3PAOs and DIB contractors) will not trust a closed-source detection algorithm?**

2. **What does closing or restricting the code do to the paper's credibility as a category-capture artifact?** The paper's whole thesis is auditability. Does closed-source kill the paper, wound it, or just slow it?

3. **What is the commercial cost of open-sourcing the wedge when the revenue product is the Readiness Pack?** Am I overestimating or underestimating the risk that a competitor forks the engine and eats the wedge without citing back?

4. **What evasion and adversary concerns become material once the code is public?** The paper's Section 15 already concedes that a sophisticated adversary with the paper and the code can pass every signature. Is that concession enough, or does open-sourcing materially accelerate detector evasion beyond what the paper admits?

5. **Name one failure mode of your top-ranked option that I have not already named above.**

## What I need back

- **Ranking of A, B, C, D.** One line per option.
- **Final verdict: one sentence.** Which option do I ship with?
- **One failure mode** of your top-ranked option I have not already named.
- **One question I should have asked you but did not.**
