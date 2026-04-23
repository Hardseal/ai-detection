# Regulatory Disclaimer

**Read this before you rely on any output from this tool.**

## What this tool is

Hardseal AI-Detection is a stdlib-only heuristic detector for AI-generated
and AI-contaminated artifacts in CMMC Level 2 readiness packets. It produces
a numeric confidence score and a four-tier verdict: `CLEAN`,
`PARTIALLY_CONTAMINATED`, `CONTAMINATED`, `LIKELY_SYNTHETIC`.

## What this tool is not

1. This tool is not a CMMC assessment. Only a Certified Third-Party
   Assessment Organization (C3PAO) under authorization from the Cyber-AB
   can perform a CMMC Level 2 assessment.
2. This tool is not a legal opinion, an accounting opinion, or a
   professional judgment of any kind.
3. This tool is not a substitute for human review of evidence artifacts
   by a qualified compliance professional.
4. A `CLEAN` verdict does not certify that a packet is compliant with
   NIST SP 800-171 Rev 2 or with the CMMC Final Rule. A `CLEAN` verdict
   says only that the heuristics implemented in this release did not
   fire above their configured thresholds on the input provided.
5. A `CONTAMINATED` or `LIKELY_SYNTHETIC` verdict does not prove that a
   packet was authored by a large language model, that it is
   fraudulent, or that its authors acted in bad faith. It indicates
   that patterns associated with machine generation or with low
   grounding specificity were present at scoring time.

## No regulatory guarantee

No output of this tool guarantees any outcome of a CMMC assessment, a
DIBCAC audit, a DoD contract award, or any other regulatory
determination. Regulatory determinations are made by authorized
assessors and officials under the applicable frameworks, not by this
software.

Hardseal LLC disclaims any warranty that the use of this tool will
cause any artifact to pass, or to fail, any assessment performed by any
authorized assessor. Use of this tool does not create a professional
relationship between the user and Hardseal LLC.

## No warranty

This software is provided under the MIT License, without warranty of
any kind, express or implied, including but not limited to the
warranties of merchantability, fitness for a particular purpose, and
non-infringement. See `LICENSE` for the full text.

## Known limitations

See Section 15 of *State of AI-Era Defense Compliance Evidence* (the
companion paper) for a full inventory of acknowledged evasion vectors
and failure modes. A sophisticated adversary with access to this code
and to the companion paper can construct artifacts that pass every
signature currently implemented. The detector is designed to raise the
cost of contamination, not to make contamination impossible.

## How to use the output responsibly

1. Treat verdicts as inputs to human judgment, not as conclusions.
2. Review the per-detector feature values, not just the aggregated
   confidence score.
3. Pair every run with human review of any artifact that scored
   `PARTIALLY_CONTAMINATED` or worse.
4. Do not make hiring, vendor selection, or disciplinary decisions
   about a packet's author solely on the basis of a verdict from this
   tool.
5. Do not represent a `CLEAN` verdict to an assessor as an attestation
   of authenticity. Represent it as a heuristic signal with the
   acknowledged limits above.

## Contact

Questions about the appropriate use of this tool in an assessment
context should go to `rico@hardseal.ai`.
