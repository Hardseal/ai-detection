# WAR PANEL PROMPT — SHIP QUALITY, 10/10 CHECK
## Hardseal AI-Detection v0.2.1 public release, April 22, 2026

**Instructions: this identical prompt is going to ChatGPT, Gemini, Perplexity, and Grok in parallel. Answer as if the other three panels do not exist. Be blunt. No hedging. No hype. We are hours from pushing the repo public and I want every flaw found before a stranger finds it.**

---

## Context

You have been tracking this project across three prior fires (v0.1 red-team, v0.2 next-move, v0.3 open-source decision). You told me to open-source under MIT. I am doing that today, not Sunday.

## What has landed since the v0.3 fire

Three hardening docs added to the repo based directly on your failure-mode callouts:

1. **REGULATORY_DISCLAIMER.md** (Gemini's liability gap). Explicit no-regulatory-guarantee clause; a CLEAN verdict is a heuristic signal, not a CMMC determination; no substitute for a C3PAO assessor; paired with the MIT no-warranty clause.

2. **SUPPORT.md + .github/ISSUE_TEMPLATE/** (Grok's solo-founder support burden). Triage-aware routing: DIB/C3PAO/paid inquiries go to rico@hardseal.ai with dated SLAs; GitHub issues are best-effort weekly triage; three issue templates (bug, detector accuracy, blank disabled); config.yml redirects commercial/press/security inbound to email or SECURITY.md.

3. **ANCHOR_PLAN.md** (Perplexity's mindshare-capture risk). Thirty-day and ninety-day commitments to stay the named home: trademark filing by May 10; "Powered by Hardseal" authorized-implementations registry; weekly release cadence through paper drop; paper-as-canonical-reference; vocabulary lock (the 7 detector names + 4 confidence tiers); "no relicensing, no suing forks, out-ship them" posture.

## Ship-day state

- 48 tests passing across Python 3.10 / 3.11 / 3.12 (CI matrix live in .github/workflows/ci.yml).
- Commitment hash reproduces: `32f1e682b0544b1af20077cc33f0604ec76238489182190c8d77a1cb01f42bbf`.
- CLI demos green: clean CLEAN@0.16, contaminated LIKELY_SYNTHETIC@1.0, templated-with-guard CLEAN@0.00.
- License: MIT, copyright 2026 Hardseal LLC. LICENSE, SECURITY.md, CONTRIBUTING.md, CHANGELOG.md all in place.
- README rewritten to match: open-source from day one, commitment-hash table, full file index, link to paper.
- Paper "State of AI-Era Defense Compliance Evidence" drafted (10,760 words, 16 sections, 3 appendices, 12 attack patterns, full NIST 800-171A crosswalk). Scheduled publish April 27 on hardseal.ai.

## Pre-push cleanup decision on the table

Six files sit in the repo directory that may or may not belong in the public push:

1. `paper/outreach/C3PAO_SHADOW_AUDIT_PITCHES.md` — draft outreach to 3 C3PAOs. Not yet sent.
2. `paper/outreach/MSP_INTEGRATOR_PITCHES.md` — draft outreach to 5 MSPs. Not yet sent.
3. `REDTEAM_PROMPT_V0.1.md` — internal war-panel prompt with runway, pricing, business state.
4. `REDTEAM_PROMPT_V0.2.md` — same vintage, same exposure.
5. `REDTEAM_PROMPT_V0.3_OPEN_SOURCE.md` — same.
6. `paper/STATE-OF-AI-ERA-COMPLIANCE-EVIDENCE.md` — the full field report, scheduled publish April 27 on hardseal.ai (5 days from now).

My current recommendation to the founder: delete the two outreach files (burns prospects), delete the three redteam prompts (leaks business intel), and ship the paper in the repo today so the README claims match reality.

## What I need from you

**Five items. Be surgical.**

1. **On a scale of 1-10, rate the ship-readiness of this public v0.2.1 release for the stated mission ("own the trust layer of AI-era defense compliance"). One number. One sentence of justification.**

2. **Agree or disagree with the pre-push cleanup recommendation on the six files above? If you disagree on any of the six, say which one and why.**

3. **Name the single highest-leverage change that would move your rating one full point closer to 10.** Be specific enough to implement in the next 60 minutes. "Polish the README" is not an answer. "Add a LICENSE-ATTRIBUTION.md that names the trademark policy and the no-relicensing promise in one place so a competitor forks you with the obligation visible on line one" is the level of specificity I want.

4. **Name one failure mode of shipping today (not Sunday) that you have not mentioned in any prior fire.** The v0.3 fire already surfaced the liability gap, mindshare capture, and support-burden flood. Go past those.

5. **If we repeated this rating exercise 90 days from now (July 22, 2026), what is the single thing about the repo's state today that you predict will look embarrassing in hindsight?**

## What I need back

- **The 1-10 rating** with one-sentence justification.
- **Agree/disagree on each of the six files.** One line each.
- **The one 60-minute change** that moves the rating +1.
- **One new failure mode** of shipping today.
- **One 90-day hindsight prediction** of embarrassment.

**Length cap: 500 words. No filler. No pep talk.**
