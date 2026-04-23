# Cold Outbound - AI Evidence Integrity Diagnostic

**Created:** April 22, 2026
**Last updated:** April 22, 2026 — added Wild Sample Appendix attachment after Round 2 critique.
**Goal:** Book one 15-minute call with a real DIB compliance lead by Friday April 24, 2026.
**Assets attached (two PDFs):**
- `Falcon_Edge_AI_Evidence_Integrity_Report_v2.pdf` — 3-page main report (Falcon Edge demo packet)
- `Falcon_Edge_Wild_Sample_Appendix.pdf` — 1-page proof the engine works on samples we did NOT author. Three SSP excerpts: human-authored = CLEAN, vendor-template = CONTAMINATED, LLM-generated = LIKELY SYNTHETIC. Closes the closed-loop credibility gap a sophisticated CISO would otherwise raise.

---

## The 3-sentence cold outbound

> Subject: Your CMMC evidence pack scored synthetic in 4 hours
>
> Hi [first name],
>
> I built a stdlib-only detector that scores CMMC SSPs, POA&Ms, and audit-log evidence for AI-contamination fingerprints (boilerplate clustering, synthetic timestamps, vendor-impossible tech-stack claims). On a sample [180-employee DIB sub] packet, it returned LIKELY SYNTHETIC at 0.81 in under 4 hours, including a vendor-impossible Azure AD on AWS GovCloud claim that would fail a C3PAO on first review. I'd like 15 minutes to show you the report and ask: would your team submit this packet, or would you want to know first?
>
> Sample 3-page report attached. Calendar: [link]
>
> Rico Allen | Hardseal | rico@hardseal.ai

**Word count: 117. Under the 180-word memory rule.**

**No em dashes (memory rule).**

---

## Cold outbound rationale (why this opens)

1. **Subject line is the entire hook.** "Your CMMC evidence pack scored synthetic in 4 hours" is a personalized future-pace threat. Compliance leads cannot ignore it.
2. **Sentence 1 names the engine concretely** (stdlib-only, three artifact types, four heuristics). Establishes you've built something, not vaporware.
3. **Sentence 2 is the proof.** Specific score (0.81), specific finding (Azure AD on AWS GovCloud), specific outcome (would fail a C3PAO).
4. **Sentence 3 is the ask, framed as the buyer's question, not yours.** "Would you submit this?" forces a yes/no internal answer that pulls them into a call.
5. **The attached PDF is the proof artifact.** They don't have to take your word.

---

## ICP target shortlist (5 prospects)

Target profile:
- 100-500 employees
- DIB subcontractor or prime
- NAICS 541330 (Engineering Services) or 541715 (R&D in Physical, Engineering, and Life Sciences)
- Has DFARS 252.204-7012 in active contracts
- Likely facing CMMC Level 2 in next 12 months
- Compliance lead has a LinkedIn presence

| # | Company type | Title to target | Why this fits | Channel |
|---|---|---|---|---|
| 1 | Aerospace structures fabricator (~150-300 emp) - target a Florida or California sub on a Lockheed or Boeing program | VP Compliance / CISO / Director of Information Security | Real CUI handling, real DFARS exposure, small enough that the comp-lead reads their own email | LinkedIn InMail + email |
| 2 | Defense electronics OEM (~200-400 emp) - microelectronics, EW, sensors | Chief Compliance Officer / CMMC Program Lead | High-value CUI, high cyber scrutiny, FY26 contracts already gating on CMMC posture | LinkedIn + warm intro through CyberAB Marketplace |
| 3 | Engineering services firm doing DoD R&D (~100-250 emp) - SBIR/STTR Phase II graduate | Founder / President / Director of Government Programs | Small enough that founder-to-founder cold opens land; SBIR primes are CMMC-aware and budget-light | Email + Twitter/X DM if active |
| 4 | MSP that serves DIB contractors (~50-200 emp internal, but services 20-50 DIB clients) | Founder / VP of Compliance Services | Channel play - one MSP yes can become 20-50 contractor reports | LinkedIn + warm intro through MSP community |
| 5 | DIB compliance consultancy (CCP-staffed, not yet C3PAO) (~10-50 emp) | Founder / Managing Director / Practice Lead | Direct buyer for the diagnostic - they resell it as part of their gap-assessment service | Email + LinkedIn |

---

## How to source the actual 5 names

Use this in order of speed:

1. **CyberAB Marketplace search** for CCP-credentialed individuals at small consultancies. Filter for "CMMC Level 2 readiness." Direct buyers.
2. **LinkedIn Sales Nav search** with filters: company size 100-500, industry "Defense and Space" or "Aviation and Aerospace Component Manufacturing", title "Compliance" OR "CISO" OR "Information Security Director", US-based. Sort by "recently posted about CMMC."
3. **SAM.gov** active contract search for DFARS 252.204-7012. Pull primes and named subs from the past 12 months.
4. **DSIP (Defense SBIR/STTR)** for Phase II awardees in your geography. Founder-direct cold opens.
5. **MSP/MSSP directories** filtered for "DIB" or "defense industrial base."

**Friday cutoff:** Identify all 5 by Wednesday end-of-day. Send all 5 outreaches Thursday morning. Book one 15-min call by Friday close.

---

## Validation question to carry into the call

The call is a discovery, not a pitch. Carry these three questions:

1. "When you read the verdict on page 1 of the sample report, what was your first thought?"
2. "If your own packet scored that way two weeks before a C3PAO assessment, what would you do?"
3. "What would $5,500 to know this two weeks early be worth to you?"

If they push back on $5,500, ask: "What price would make this an obvious yes?" Don't drop the price on the call. Capture the number, take it back to the model.

---

## Capture rubric (after the call)

Within 60 minutes of the call ending, write down:

- Did they say the report would be useful? [Y/N]
- Did they say the price was reasonable / too high / too low?
- What was the language they used for the pain? (capture verbatim - this becomes the website hero)
- Did they identify a peer who would also want this? (referral path)
- Will they take a follow-up if you ship a v0.4 patch addressing their objection? [Y/N]

Three of these answers feed directly into the next round of war-panel testing.
