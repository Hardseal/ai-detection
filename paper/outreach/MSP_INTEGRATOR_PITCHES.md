# MSP / MSSP / Compliance Integrator Pitches

**Purpose:** Warm outreach to MSPs and MSSPs serving DIB contractors, offering the Hardseal AI-detection engine as a pre-submission check they can bundle inside their existing CMMC readiness sprint product. No send. Draft only.

**The packaging thesis (Perplexity's 0-th from the war panel):**

MSPs already sell $5K-$25K CMMC readiness sprints. Hardseal's engine is not a competitor to that sprint. It is a differentiating deliverable inside the sprint: an AI-contamination sweep the MSP runs on the client's packet before final submission, producing a report the client signs as part of the deliverable. It closes a question C3PAOs have started asking. It raises the MSP's defensibility. It charges the client zero incremental cost.

**The engine is stdlib-only Python, runs offline, no telemetry. It runs inside the MSP's existing CUI-authorized environment without adding any attack surface.**

**Ship date target:** Week of April 28, 2026 (after paper publishes April 27).

**Do NOT send yet.**

---

## Variant 1. Differentiator angle. For MSPs who publicly sell CMMC readiness sprints.

Subject: A deliverable you can add to your next readiness sprint at zero marginal cost

Body:

Hi [Name],

I am the founder of Hardseal. I published a technical paper today naming twelve attack patterns that AI-generated compliance evidence produces in CMMC Level 2 packets. Seven stdlib-only open-source detectors that catch those patterns ship alongside the paper. Paper: hardseal.ai/research/state-of-ai-era-compliance-evidence. Code: github.com/hardseal/ai-detection (MIT license, 65 tests passing, zero external dependencies).

Here is why I am writing to you specifically.

C3PAOs are starting to reject packets for AI-contamination signatures they cannot always articulate cleanly. The field report you just read articulates them. If you run the engine as a final pre-submission check inside your existing readiness sprint, you get:

1. A clean deliverable in the sprint (the AI-contamination sweep report) with no incremental licensing cost.
2. A defensible answer when your client asks why you caught something their in-house consultant did not.
3. An independent, auditable signal that differentiates your sprint from the three other MSPs in their buying shortlist.

The engine is stdlib-only Python. It runs inside your existing CUI-authorized environment. No network calls. No telemetry. No external model. The CLI runs in under five seconds on a typical packet.

I am happy to walk a senior engineer on your team through a demo on a contrived contaminated packet, pro bono, so you can see the output shape. 30 minutes. Your call, your agenda.

Rico Allen
Hardseal
rico@hardseal.ai

---

## Variant 2. Pain-led. For MSPs who have publicly mentioned C3PAO rejection rates.

Subject: The pattern your C3PAO is flagging and cannot always name

Body:

Hi [Name],

If you have been reading the CMMC subreddit or the CyberAB forums lately you have seen the pattern: contractor submits a packet, C3PAO returns it with a comment like "narrative reads as generated" or "evidence lacks operational specificity." That is not a technical verdict the contractor can act on. It is a feeling the assessor cannot always justify in writing.

I just published the technical paper that turns the feeling into twelve named patterns with deterministic detection signatures. It is at hardseal.ai/research/state-of-ai-era-compliance-evidence. Seven of the twelve are shipping today as open-source stdlib-only Python: github.com/hardseal/ai-detection.

The relevant question for your readiness practice: if you run the engine inside your existing sprint before your client submits, you catch the patterns the assessor would have caught, at the stage where you can still fix them.

Mechanics: the engine is stdlib-only, runs offline, no dependencies, five-second CLI. Your engineer can audit the code in an afternoon. It runs inside your existing CUI environment with no network egress.

30-minute demo, pro bono, against a contrived contaminated packet so you can see the output. Your call.

Rico Allen
Hardseal
rico@hardseal.ai

---

## Variant 3. Channel-led. For MSPs with a visible CMMC practice lead.

Subject: Free pre-submission AI-contamination sweep you can attach to your next SOW

Body:

Hi [Name],

Quick note, one thing. I am the founder of Hardseal. I published a paper today naming the twelve AI-contamination attack patterns in CMMC Level 2 evidence packets, with seven stdlib-only open-source detectors that catch them.

You can attach the sweep to your next CMMC readiness SOW at zero marginal cost. It runs inside your CUI environment, no network calls, no dependencies, five-second CLI. Your client signs the sweep report as part of the sprint deliverable. Your C3PAO gets a defensible pre-submission artifact. You get a differentiator.

Paper: hardseal.ai/research/state-of-ai-era-compliance-evidence
Code: github.com/hardseal/ai-detection (MIT license)

If you want a 30-minute walkthrough, I am in the calendar. If you want to run it yourself first, the CLI usage is in the repository README.

Rico Allen
Hardseal
rico@hardseal.ai

---

## Variant 4. Blunt. For MSPs who have a history of moving fast on new tooling.

Subject: You can bolt this onto your readiness sprint this week

Body:

Hi [Name],

New paper, new tool, both public, both free to use. Point of contact is me.

Paper names twelve attack patterns on AI-contaminated CMMC Level 2 evidence. The tool is the engine that detects seven of them. Open source, MIT licensed, stdlib-only, 65 tests, runs in your CUI environment.

You can bolt the sweep onto your existing readiness sprint this week. Zero licensing cost. The deliverable is a report your client signs and you include in the SOW closeout.

Paper: hardseal.ai/research/state-of-ai-era-compliance-evidence
Code: github.com/hardseal/ai-detection

If you want me in on a demo call with your engineer, 30 minutes, pro bono. If you want to just run it, the README is all you need.

Rico Allen
Hardseal
rico@hardseal.ai

---

## Variant 5. Deep. For MSPs whose CTO or head of engineering is the buyer.

Subject: Stdlib-only Python AI-contamination detector, MIT licensed, 65 tests, for your readiness practice

Body:

Hi [Name],

I am writing because your engineering leadership looks like it would actually read a stdlib-only Python codebase before deciding whether to bundle it into a client deliverable.

Hardseal just shipped v0.2 of its AI-era evidence contamination detector. The companion technical paper ships this week: hardseal.ai/research/state-of-ai-era-compliance-evidence. The engine is at github.com/hardseal/ai-detection.

The things you will care about most:

1. Zero external dependencies. The `import` block is `argparse, json, math, re, statistics, sys, collections, dataclasses, datetime, enum, pathlib, typing`. All stdlib. The supply chain is auditable in an afternoon.
2. Deterministic. Same input produces the same verdict. No non-determinism from sampling, no model drift.
3. No network calls, no telemetry. Runs inside your existing CUI enclave.
4. Seven detectors orchestrated into four confidence tiers (CLEAN, PARTIALLY_CONTAMINATED, CONTAMINATED, LIKELY_SYNTHETIC). Public weights, public SHA-256 commitment hash in the README, so scoring cannot silently drift between releases.
5. Reference test suite includes a deliberate regression for templated-legitimate-packet false positives (the v0.2 TemplateGuard work). The engine does not flag consultant-built packets that share stock phrasing.

The pitch: inside your existing CMMC readiness sprint product, run the engine as a final pre-submission sweep. Client signs the report. You differentiate on a public, auditable artifact at no marginal licensing cost.

45 minutes with your lead engineer and me, pro bono, if that accelerates a decision. Your agenda.

Rico Allen
Hardseal
rico@hardseal.ai
