# v0.1 Red-Team Prompt — Submit to ChatGPT / Gemini / Perplexity / Grok

**Use:** Paste this verbatim into each panel. Keep responses under 700 words. Do not edit between panels — identical inputs → comparable outputs → cleaner synthesis.

---

I am Rico Allen, solo founder of Hardseal — a stdlib-only Python CMMC Level 2 compliance platform (65 modules, ~55K LOC, 1,847 tests, zero external dependencies). My North Star is "own the trust layer of AI-era defense compliance." The 90-day lever is `mismatch_engine_ai.py`: a detection engine for AI-generated and AI-contaminated evidence in CMMC Level 2 readiness packets.

v0.1 ships today. Six stdlib-only heuristics, weighted into a single Confidence verdict (CLEAN / PARTIALLY_CONTAMINATED / CONTAMINATED / LIKELY_SYNTHETIC):

1. **SentenceStructureAnomaly** (0.10) — coefficient of variation + Shannon entropy of sentence lengths. LLM prose is rhythmically uniform; human SSPs are bursty.
2. **BoilerplateCluster** (0.15) — k-shingle Jaccard similarity across control narratives. Detects paste-and-rename LLM output.
3. **TimestampRegularity** (0.20) — variance-to-mean ratio of log inter-arrival times + round-second rounding rate. Detects synthetic audit logs.
4. **MappingDensity** (0.15) — ratio of control-ID mentions to mechanism/tool tokens (Okta, Splunk, YubiKey, TLS 1.3, etc.). LLMs cite controls without naming mechanisms.
5. **CitationGraph** (0.15) — max depth, orphan rate, cycle count across evidence artifacts. Catches circular references and dangling nodes common in synthetic packets.
6. **PromptLeakage** (0.25, highest weight) — regex hits against a curated list of LLM residue phrases ("As an AI language model", "Certainly! Here", "[INSERT X HERE]", ChatML tokens).

v0.1 demo result: clean hand-authored packet → CLEAN @ 0.13. Contaminated packet (visible LLM residue + citation-only narratives) → LIKELY_SYNTHETIC @ 1.0.

Constraints that are non-negotiable: zero external dependencies (no numpy, no sklearn, no network calls — this is a security differentiator, not a limitation). Deterministic. Auditable by a C3PAO assessor in one afternoon. Runs inside a CUI enclave with no internet.

**I need you to red-team v0.1 on exactly these five questions. Keep your full response under 700 words. Be specific — no consultant-speak, no hedging.**

1. What is the single highest-value 7th heuristic I am missing? Name it, explain the attack it catches that heuristics 1–6 miss, and give me the stdlib-only signal it would compute.

2. What is the most realistic evasion technique a motivated adversary would use against heuristics 1–6 in combination? Assume they have read the paper and the code. What breaks first?

3. What is the most defensible way to publish the heuristic weights and regex lists so that this doesn't become a how-to-beat-the-detector guide — while still honoring the open-source credibility play that makes the trust layer defensible?

4. What is the right public release schedule — open-source on day one, keep private until the field report drops, or staged release (paper → code → weights)? Justify in terms of category capture, not just risk.

5. What is the single most embarrassing false-positive case I have not thought of — the one that would discredit the tool in front of a C3PAO on a first demo? Be specific enough that I can go build a guard against it today.

End your response with: one sentence on whether v0.1 is ready to ship to a paying DIB contractor as a $5K–$8K overlay inside a Readiness Pack, or whether a specific gap must close first.

---

**Synthesis target:** `Security+ Study Command Center/HARDSEAL-AI-DETECTION-V0.1-REDTEAM — WAR PANEL SYNTHESIS.md`
