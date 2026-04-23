# Support

Hardseal AI-Detection is open source under the MIT License. The project
is maintained by a solo founder. This document tells you how to get help
and what to expect.

## Where to send what

| Type of inquiry | Where it goes | Response target |
|---|---|---|
| Bug in the detector or the verifier | GitHub Issues, `bug` template | Weekly triage, best effort |
| Suspected false positive or false negative | GitHub Issues, `detector-accuracy` template. Requires redacted packet metadata. No CUI. | Weekly triage, best effort |
| DIB contractor or C3PAO readiness inquiry | `rico@hardseal.ai` with subject line `[DIB]` or `[C3PAO]` | 48-hour acknowledgement |
| Paid Readiness Pack or AI-detection overlay | `rico@hardseal.ai` with subject line `[PAID]` | 24-hour acknowledgement |
| Security vulnerability | `security@hardseal.ai`. See `SECURITY.md` for the full policy | 72-hour acknowledgement |
| Media, research, or conference inquiry | `rico@hardseal.ai` with subject line `[PRESS]` | Replied in order received |

## What this project is

A stdlib-only heuristic detector for AI-contaminated compliance
artifacts. It runs on Python 3.10, 3.11, and 3.12 with zero external
dependencies. If you read the README, the CHANGELOG, and the companion
paper, you have everything the maintainer has.

## What this project is not

1. A paid product. The detector is free under MIT. The paid product is
   the Hardseal Readiness Pack. Inquiries about the paid product use
   the email addresses above.
2. A support contract. Filing a GitHub issue does not obligate the
   maintainer to reply on any timeline.
3. A regulatory service. See `REGULATORY_DISCLAIMER.md`.

## How to file a good issue

Bug reports with a minimal reproduction close faster than bug reports
without one. If your issue depends on packet data you cannot share,
reproduce the behaviour on one of the sample packets in `samples/` and
include the command you ran.

Feature requests that conflict with the stdlib-only rule will be
closed. See `CONTRIBUTING.md`.

Tone matters. Rude issues get closed without reply.

## On support bandwidth

The maintainer is a solo founder, a full-time builder of a compliance
platform, and a Security+ candidate. Expect best-effort response times
on free-tier inquiries. Commercial customers of Hardseal LLC receive
committed SLAs under a separate agreement.

## On CUI and sensitive data

Do not include Controlled Unclassified Information, regulated
export-controlled content, or production secrets in GitHub issues,
sample packets, or email to any Hardseal address. Redact before
sending. If a genuine sample requires CUI handling, email
`rico@hardseal.ai` to set up a proper intake.

## On ego support

This repository is not the right venue for debates about whether
heuristic detection is a valid approach, whether stdlib-only is a real
constraint, or whether large language models can be detected at all.
Those are interesting questions and the companion paper addresses them
in Sections 1, 15, and 16. Ego-driven issues get closed with a
pointer to the paper.
