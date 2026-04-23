# Security Policy

## Supported Versions

The current release line is v0.2. Security fixes are backported to the
latest minor version only. Older versions do not receive fixes.

| Version | Supported |
|---|---|
| 0.2.x | yes |
| 0.1.x | no  |

## Reporting a Vulnerability

Please report security issues privately to:

**security@hardseal.ai**

Include:
1. A description of the issue.
2. Steps to reproduce, or a minimal proof-of-concept.
3. Your assessment of severity and impact.
4. Whether you want public attribution when the fix ships.

You will receive an acknowledgement within 72 hours. A remediation
timeline will be communicated within 10 business days of the initial
report.

## Scope

In scope:
1. The detection engine (`mismatch_engine_ai.py`, `template_guard.py`).
2. The commitment-hash verifier (`verify_commitment.py`).
3. The published regex bundles: leakage signatures, grounding patterns,
   mechanism tokens, the weight vector.
4. The test suites.

Out of scope:
1. Evasion techniques already acknowledged in the companion paper,
   Section 15 (Honest Limits).
2. Findings that require modifying the source bundles before running.
3. Issues in contributor tooling (IDEs, linters, shells).

## No Bounty Program

Hardseal LLC does not operate a paid bug bounty. Reporters are
acknowledged by name in release notes if they request attribution.

## Responsible Disclosure

Please do not publicly disclose a vulnerability before Hardseal has had
a reasonable opportunity to remediate. 90 days is the default window.
Coordinated disclosure is encouraged.

## Provenance

Every release of the scoring bundle is anchored to a SHA-256
commitment hash published in `README.md` and reproducible via
`verify_commitment.py`. If a downstream tool reports a scoring result,
you can verify which bundle version produced it. Scoring drift between
releases is always a dated, documented event.
