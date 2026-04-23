"""
rebuttal_generator.py — Defensive rebuttal kit for every detector finding.

War-panel Round 1 gap (Gemini, April 22, 2026):
    "You don't have a 'Defensive Rebuttal' section. Without the 'how to fight
     back' component, you are only selling them anxiety, not a solution."

Buyer truth:
    A finding from the engine is a flag, not a verdict. A real DIB compliance
    lead needs to know — for every red mark — how to either (a) prove the
    finding is a false positive with concrete evidence, or (b) remediate fast
    if the finding is real. Without this, the report is fear theater.

This module produces, per Finding:
    - rebuttal_steps      : 2-5 numbered steps the contractor can execute
                            to refute or remediate the finding
    - evidence_to_produce : what artifacts will reverse the score
    - escalation_path     : when to call counsel (FCA-relevant findings)

Sacred rules honored:
    - Stdlib only.
    - No invented compliance facts.
    - Rebuttals are ACTIONABLE — every step names a concrete artifact, system,
      or person, not a generic "review your evidence."

Design note:
    Rebuttals are templated per heuristic, then customized with finding-level
    detail (artifact_id, score, evidence string) where useful. We deliberately
    do NOT use an LLM here — that would defeat the purpose of an AI-detection
    tool. Templates are auditable, reproducible, and stdlib-only.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Iterable, List, Optional


# --------------------------------------------------------------------------
# Outputs
# --------------------------------------------------------------------------


@dataclass
class Rebuttal:
    artifact_id: str
    heuristic: str
    score: float
    rebuttal_steps: List[str]
    evidence_to_produce: List[str]
    escalation_path: str

    def to_dict(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------
# Per-heuristic playbooks
# --------------------------------------------------------------------------
# Each entry: (rebuttal_steps, evidence_to_produce, escalation_path)
# Steps are intentionally specific. Generic "review the evidence" wording is
# banned — every step names a concrete artifact, system, or person.

_PLAYBOOKS = {
    "FactualPlausibility": {
        "steps": [
            "Identify the named author of the SSP section. Confirm they signed off "
            "on the technical claim flagged here.",
            "Pull the actual identity-broker configuration export from the system "
            "named in the flagged paragraph (e.g., AWS IAM Identity Center config, "
            "Entra Conditional Access JSON, CASB policy export).",
            "Compare the exported configuration to the SSP text. If the config "
            "contradicts the SSP text, REWRITE the SSP. The detector finding is "
            "TRUE.",
            "If the SSP text is correct and the detector caught a wording ambiguity, "
            "add a one-sentence clarification with the exact product names and "
            "boundary, then re-run the detector.",
        ],
        "evidence": [
            "Identity-broker config export (JSON or screenshot) for the named system.",
            "Conditional Access policy list (Entra ID admin center export).",
            "AWS IAM Identity Center permission set + assignment export.",
            "Network architecture diagram showing the cross-cloud trust path.",
            "Named SSP author + technical reviewer attestation.",
        ],
        "escalation": (
            "ESCALATE TO COUNSEL if the SSP has already been signed and submitted "
            "to the government with the factual error intact. DOJ Civil Cyber-Fraud "
            "Initiative treats knowingly false cyber representations as actionable. "
            "Do not 'fix and forget' a submitted artifact without legal guidance."
        ),
    },
    "PromptLeakage": {
        "steps": [
            "Search the artifact for the flagged phrase(s) and confirm presence.",
            "Identify the human author of record. If no human author owns this "
            "section, the finding is TRUE — assign an owner and rewrite.",
            "If a human author claims ownership, ask them to attest in writing "
            "that they wrote the flagged section without LLM scaffolding.",
            "Strip the LLM scaffolding strings, rewrite in the author's voice, "
            "and re-run the detector. Score should drop to 0.0.",
        ],
        "evidence": [
            "Authoring history (Word/Google Docs revision log, git blame for "
            "Markdown sources).",
            "Author attestation (signed, dated).",
            "Screenshot of the artifact in the authoring system showing the "
            "named author in the metadata.",
        ],
        "escalation": (
            "ESCALATE TO COUNSEL only if the artifact has been submitted to the "
            "government and contains visible LLM scaffolding. Otherwise, this is "
            "a remediation-and-resubmit before assessor review."
        ),
    },
    "BoilerplateCluster": {
        "steps": [
            "Pull the cluster of similar narratives the detector flagged.",
            "For each narrative, ask: does this control's implementation actually "
            "differ between the named systems? If yes, the boilerplate is hiding "
            "real implementation differences and must be split.",
            "If the implementation truly is identical across systems (e.g., same "
            "M365 tenant policy applies to all in-scope mailboxes), add an explicit "
            "'inheritance' or 'shared responsibility' note citing the common control "
            "and the systems it covers.",
            "Re-run the detector. Boilerplate score should drop because the "
            "narratives now carry distinguishing context.",
        ],
        "evidence": [
            "Per-system implementation evidence (screenshots, config exports).",
            "Inheritance/shared-responsibility statement with named common control.",
            "Updated SSP narratives with system-specific detail.",
        ],
        "escalation": (
            "Counsel escalation NOT typically required. This is a sufficiency-of-"
            "evidence question, not a knowing-falsity question."
        ),
    },
    "TimestampRegularity": {
        "steps": [
            "Pull the source-of-truth log file (raw .evtx, syslog, JSON event "
            "stream) for the time window the detector evaluated.",
            "Compare event-time distribution in the source log against what the "
            "detector saw. If the source log shows realistic variance and the "
            "detected artifact was an AI summary or excerpt, supply the source log "
            "as the assessor's evidence and DEPRECATE the AI summary.",
            "If the source log itself is uniform, the audit-log evidence is "
            "fabricated or generated. Treat as a CRITICAL finding and escalate.",
            "Going forward, never submit AI-summarized log evidence to an assessor. "
            "Always submit the raw collector export or a SIEM-issued report.",
        ],
        "evidence": [
            "Raw source log (.evtx, syslog, CloudTrail event stream).",
            "SIEM-issued report with event-time distribution.",
            "Log-collector configuration showing the source.",
            "Hash chain or write-once storage proof for the source log.",
        ],
        "escalation": (
            "ESCALATE TO COUNSEL if the log evidence has been submitted to the "
            "government and the source log cannot be produced. Fabricated audit "
            "evidence is a high-severity FCA exposure under the Civil Cyber-Fraud "
            "Initiative."
        ),
    },
    "MappingDensity": {
        "steps": [
            "Review the SSP for control coverage that is too perfect (e.g., every "
            "objective marked MET with no inheritance and no POA&M items).",
            "Identify shared-responsibility controls (cloud service provider "
            "controls, MSP-managed controls). These should be marked as inherited, "
            "not implemented in-house.",
            "Identify gaps that should be on the POA&M but are not. Real systems "
            "have gaps. A 1.00 mapping density usually means gaps are hidden.",
            "Re-run the detector after splitting inheritance and adding POA&M items.",
        ],
        "evidence": [
            "Updated SSP with explicit inheritance markers.",
            "Updated POA&M with realistic gap items.",
            "CRM (Customer Responsibility Matrix) from cloud provider.",
        ],
        "escalation": (
            "Counsel escalation NOT typically required. This is a credibility "
            "concern, not a falsity claim."
        ),
    },
    "CitationGraph": {
        "steps": [
            "For each cited NIST publication or external source, verify the source "
            "exists at the cited identifier (NIST 800-171 Rev 2, NIST 800-53 Rev 5, "
            "etc.). Hallucinated identifiers (wrong revision, wrong number) are "
            "TRUE positives.",
            "If the citation graph shows every control citing the same source, "
            "split citations to reflect actual control inheritance and reference "
            "the right per-control source.",
            "Replace any hallucinated citations with verified ones.",
            "Re-run the detector.",
        ],
        "evidence": [
            "Verified citation list with NIST identifier + revision.",
            "CRM showing cloud-inherited controls and their actual source-of-truth.",
            "Updated SSP with corrected references.",
        ],
        "escalation": (
            "ESCALATE TO COUNSEL if the artifact has been submitted with citations "
            "to non-existent NIST publications. Misrepresentation of authoritative "
            "source is FCA-relevant under the Civil Cyber-Fraud Initiative."
        ),
    },
    "SentenceStructureAnomaly": {
        "steps": [
            "Identify the named author of the flagged narrative.",
            "Ask the author to confirm authorship in writing. If the author cannot "
            "or will not, treat as TRUE positive and reassign.",
            "If the author confirms, accept the finding as a credibility flag and "
            "leave the narrative as-is. This heuristic alone is not a control "
            "failure.",
            "Optional: rewrite the narrative with concrete system names and dates "
            "to add specificity, which will lower the score on re-run.",
        ],
        "evidence": [
            "Author attestation (signed, dated).",
            "Authoring system revision log.",
        ],
        "escalation": (
            "Counsel escalation NOT required. This is a low-impact credibility "
            "flag, not a control failure or falsity claim."
        ),
    },
    "ArtifactSpecificityIndex": {
        "steps": [
            "Identify the generic phrases the detector flagged ('the organization', "
            "'the system', 'as appropriate').",
            "Replace each generic phrase with the specific named system, owner, "
            "or date that applies.",
            "If the SSP truly cannot be made specific because the contractor does "
            "not know the answer, that is a real evidence gap — open a POA&M item "
            "for the underlying control.",
            "Re-run the detector. Specificity score should rise.",
        ],
        "evidence": [
            "Updated SSP with named systems, owners, dates.",
            "System inventory mapping ('the system' resolves to which CIs).",
        ],
        "escalation": (
            "Counsel escalation NOT typically required."
        ),
    },
}

_DEFAULT = {
    "steps": [
        "Review the flagged finding with the named system owner.",
        "If the finding is a false positive, document why and request re-test.",
        "If the finding is real, open a POA&M item with named owner and date.",
    ],
    "evidence": [
        "System owner attestation.",
        "Updated SSP or POA&M.",
    ],
    "escalation": (
        "No specific escalation guidance. Use general FCA-disclosure judgment."
    ),
}


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------


def build_rebuttal(finding) -> Rebuttal:
    heuristic = getattr(finding, "heuristic", "Unknown")
    artifact_id = getattr(finding, "artifact_id", "unknown")
    score = float(getattr(finding, "score", 0.0))

    book = _PLAYBOOKS.get(heuristic, _DEFAULT)
    return Rebuttal(
        artifact_id=artifact_id,
        heuristic=heuristic,
        score=score,
        rebuttal_steps=list(book["steps"]),
        evidence_to_produce=list(book["evidence"]),
        escalation_path=book["escalation"],
    )


def build_packet_rebuttals(findings: Iterable) -> List[Rebuttal]:
    return [build_rebuttal(f) for f in findings]


# --------------------------------------------------------------------------
# Smoke test
# --------------------------------------------------------------------------


if __name__ == "__main__":
    class _MockFinding:
        def __init__(self, heuristic, artifact_id, score):
            self.heuristic = heuristic
            self.artifact_id = artifact_id
            self.score = score

    sample = [
        _MockFinding("FactualPlausibility", "ssp_falcon_edge.txt", 1.0),
        _MockFinding("PromptLeakage", "ssp_falcon_edge.txt", 0.85),
        _MockFinding("TimestampRegularity", "siem_log.txt", 0.92),
    ]
    for f in sample:
        r = build_rebuttal(f)
        print(f"\n=== {r.heuristic} (score {r.score:.2f}) on {r.artifact_id} ===")
        for i, step in enumerate(r.rebuttal_steps, 1):
            print(f"  {i}. {step}")
        print("  Evidence to produce:")
        for e in r.evidence_to_produce:
            print(f"    - {e}")
        print(f"  Escalation: {r.escalation_path}")
