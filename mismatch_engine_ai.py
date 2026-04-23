"""
mismatch_engine_ai.py - AI-Era Evidence Contamination Detector
===============================================================
Hardseal's extension of mismatch_engine.py for detecting AI-generated,
AI-contaminated, or AI-hallucinated evidence in CMMC Level 2 readiness
packets. Stdlib-only. Zero external dependencies.

See THREAT_MODEL.md for the complete threat model, kill-chain mapping,
and per-heuristic design rationale.

USAGE
-----
    # Single artifact
    detector = AIProvenanceDetector()
    report = detector.analyze_artifact("ssp_3.1.1.md", text)
    print(report.to_json())

    # Full packet
    report = detector.analyze_packet(
        narratives={"3.1.1": "...", "3.13.1": "..."},
        citation_edges=[("ssp", "policy_ac"), ("policy_ac", "okta_log")],
        timestamps_by_artifact={"audit.log": [datetime, ...]},
    )

    # CLI
    python -m mismatch_engine_ai /path/to/evidence/ --json

Sacred rule: stdlib-only. Every dependency is an attack surface inside a
CUI environment. Hardseal is the only CMMC platform whose supply chain
can be fully audited in an afternoon.

License: Proprietary - Hardseal LLC. Open-source release planned July 2026.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from template_guard import TemplateGuard


# ---------------------------------------------------------------------------
# Domain vocabulary — aligns with the existing mismatch_engine.py conventions
# ---------------------------------------------------------------------------

class Confidence(str, Enum):
    CLEAN = "CLEAN"                       # No AI-contamination signal
    PARTIAL = "PARTIALLY_CONTAMINATED"    # One or two weak signals
    CONTAMINATED = "CONTAMINATED"         # Strong signal on at least one heuristic
    SYNTHETIC = "LIKELY_SYNTHETIC"        # Multiple strong signals


@dataclass
class Finding:
    heuristic: str
    artifact_id: str
    score: float                       # 0.0 clean .. 1.0 strongly AI
    evidence: str
    nist_objectives: tuple = ()
    recommendation: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Report:
    artifact_id: str
    confidence: Confidence
    aggregate_score: float
    findings: list = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["confidence"] = self.confidence.value
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


# ---------------------------------------------------------------------------
# Heuristic 1 — Sentence-Structure Anomaly ("AI flatness")
# ---------------------------------------------------------------------------

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")


class SentenceStructureAnomalyDetector:
    """Flags text whose sentence-length distribution is too flat for human prose."""

    NAME = "SentenceStructureAnomaly"
    NIST = ("3.12.1[a]", "3.12.3[a]")

    def __init__(self, cv_threshold: float = 0.45, entropy_threshold: float = 2.5,
                 template_guard: Optional[TemplateGuard] = None):
        self.cv_threshold = cv_threshold
        self.entropy_threshold = entropy_threshold
        self.template_guard = template_guard

    def detect(self, artifact_id: str, text: str) -> Finding:
        # v0.2: Strip NIST/CMMC stock phrases + user baseline template text
        # before flatness analysis. Without this, a legitimate consultant-built
        # SSP full of stock language reads as "too uniform" and false-positives.
        if self.template_guard is not None:
            text = self.template_guard.strip_boilerplate(text)
        sentences = [s for s in _SENTENCE_SPLIT.split(text.strip()) if s.strip()]
        if len(sentences) < 8:
            return Finding(
                self.NAME, artifact_id, 0.0,
                f"Insufficient sentences ({len(sentences)}); cannot evaluate.",
                self.NIST,
                "Artifact too short for structural analysis.",
            )

        lengths = [len(re.findall(r"\b\w+\b", s)) for s in sentences]
        lengths = [L for L in lengths if L > 0]
        if len(lengths) < 2:
            return Finding(self.NAME, artifact_id, 0.0, "No measurable words.",
                           self.NIST, "Artifact too short.")

        mean_len = statistics.mean(lengths)
        stdev_len = statistics.stdev(lengths)
        cv = stdev_len / mean_len if mean_len > 0 else 0.0

        counts = Counter(lengths)
        total = sum(counts.values())
        entropy = -sum((c / total) * math.log2(c / total) for c in counts.values())

        cv_score = ((self.cv_threshold - cv) / self.cv_threshold) if cv < self.cv_threshold else 0.0
        ent_score = ((self.entropy_threshold - entropy) / self.entropy_threshold) if entropy < self.entropy_threshold else 0.0
        score = max(0.0, min(1.0, max(cv_score, ent_score)))

        evidence = (
            f"n={len(lengths)} sentences; mean={mean_len:.1f} words; "
            f"stdev={stdev_len:.1f}; CV={cv:.3f} (threshold {self.cv_threshold}); "
            f"entropy={entropy:.2f} (threshold {self.entropy_threshold})"
        )
        rec = (
            "Low sentence-length variance is consistent with LLM output. "
            "Request narrative author attestation or revision by a named human."
            if score >= 0.5
            else "Sentence-structure distribution within human range."
        )
        return Finding(self.NAME, artifact_id, round(score, 3), evidence, self.NIST, rec)


# ---------------------------------------------------------------------------
# Heuristic 2 — Boilerplate Cluster across control narratives
# ---------------------------------------------------------------------------

class BoilerplateClusterDetector:
    """Flags narratives that share too much phrasing with other narratives."""

    NAME = "BoilerplateCluster"
    NIST = ("3.12.4[a]",)

    def __init__(self, shingle_size: int = 5, similarity_threshold: float = 0.55,
                 template_guard: Optional[TemplateGuard] = None):
        self.k = shingle_size
        self.threshold = similarity_threshold
        self.template_guard = template_guard

    def _shingles(self, text: str) -> set:
        tokens = re.findall(r"\b\w+\b", text.lower())
        if len(tokens) < self.k:
            return set()
        shingles = {" ".join(tokens[i:i + self.k]) for i in range(len(tokens) - self.k + 1)}
        # v0.2: Subtract user-supplied baseline template shingles so the only
        # collisions that count are the ones outside the declared template.
        if self.template_guard is not None:
            shingles = self.template_guard.filter_shingles(shingles)
        return shingles

    @staticmethod
    def _jaccard(a: set, b: set) -> float:
        if not a or not b:
            return 0.0
        return len(a & b) / len(a | b)

    def detect_packet(self, narratives: dict) -> list:
        findings = []
        ids = list(narratives.keys())
        shingles = {cid: self._shingles(narratives[cid]) for cid in ids}

        for cid_a in ids:
            max_sim = 0.0
            max_other = None
            for cid_b in ids:
                if cid_a == cid_b:
                    continue
                sim = self._jaccard(shingles[cid_a], shingles[cid_b])
                if sim > max_sim:
                    max_sim = sim
                    max_other = cid_b

            score = 0.0
            if max_sim >= self.threshold:
                # scale so threshold hit -> 0.5, sim=1.0 -> 1.0
                score = 0.5 + 0.5 * (max_sim - self.threshold) / max(1e-9, 1.0 - self.threshold)
                score = min(1.0, score)

            evidence = f"Max Jaccard vs another control: {max_sim:.3f} (peer={max_other})"
            rec = (
                f"Narrative for {cid_a} shares {max_sim:.0%} of {self.k}-grams with {max_other}. "
                "Rewrite with mechanism-specific details (tool names, config values, "
                "responsible role, review cadence)."
                if score >= 0.5
                else "Narrative sufficiently distinct from peers."
            )
            findings.append(Finding(self.NAME, cid_a, round(score, 3),
                                    evidence, self.NIST, rec))
        return findings


# ---------------------------------------------------------------------------
# Heuristic 3 — Timestamp Regularity (synthetic audit log detector)
# ---------------------------------------------------------------------------

class TimestampRegularityDetector:
    """Flags audit logs whose inter-arrival timing is too regular or too-rounded."""

    NAME = "TimestampRegularity"
    NIST = ("3.3.1[a]", "3.3.1[b]", "3.3.8[a]")

    def __init__(self, vmr_threshold: float = 0.5, round_second_threshold: float = 0.85):
        # Real Poisson VMR ~= 1.0; values well below 0.5 are suspicious.
        self.vmr_threshold = vmr_threshold
        self.round_threshold = round_second_threshold

    def detect(self, artifact_id: str, timestamps: list) -> Finding:
        if len(timestamps) < 10:
            return Finding(
                self.NAME, artifact_id, 0.0,
                f"Too few timestamps ({len(timestamps)}); need >= 10.",
                self.NIST, "Request larger log sample.",
            )

        sorted_ts = sorted(timestamps)
        deltas = [(sorted_ts[i + 1] - sorted_ts[i]).total_seconds()
                  for i in range(len(sorted_ts) - 1)]
        deltas = [d for d in deltas if d > 0]

        if not deltas:
            return Finding(
                self.NAME, artifact_id, 1.0,
                "All timestamps identical — synthetic.",
                self.NIST,
                "Reject artifact. No real log produces zero-delta events.",
            )

        mean_d = statistics.mean(deltas)
        var_d = statistics.variance(deltas) if len(deltas) > 1 else 0.0
        vmr = var_d / mean_d if mean_d > 0 else 0.0

        round_count = sum(1 for t in sorted_ts if t.microsecond == 0)
        round_fraction = round_count / len(sorted_ts)

        vmr_score = (self.vmr_threshold - vmr) / self.vmr_threshold if vmr < self.vmr_threshold else 0.0
        round_score = ((round_fraction - self.round_threshold)
                       / max(1e-9, 1.0 - self.round_threshold)
                       if round_fraction > self.round_threshold else 0.0)
        score = max(0.0, min(1.0, max(vmr_score, round_score)))

        evidence = (
            f"n={len(deltas)} intervals; mean={mean_d:.2f}s; variance={var_d:.2f}; "
            f"VMR={vmr:.3f}; round-second fraction={round_fraction:.2f}"
        )
        rec = (
            "Log timing is too regular for a real event stream. "
            "Request raw source log (syslog, CloudTrail, Azure Monitor) with microsecond fidelity."
            if score >= 0.5
            else "Timestamp distribution within expected range."
        )
        return Finding(self.NAME, artifact_id, round(score, 3), evidence, self.NIST, rec)


# ---------------------------------------------------------------------------
# Heuristic 4 — Mapping Density vs Mechanism Specificity
# ---------------------------------------------------------------------------

# Seed list; expand in v0.2 once we benchmark against real DIB SSPs.
MECHANISM_TOKENS = {
    # Identity / auth
    "okta", "duo", "yubikey", "fido2", "webauthn", "entra", "azure ad",
    "active directory", "group policy", "intune", "jamf", "kandji",
    # EDR / SIEM
    "splunk", "sentinel", "crowdstrike", "defender", "carbon black", "qradar",
    "wazuh", "datadog", "elastic", "sumo logic", "graylog",
    # Cloud native logs
    "cloudtrail", "guardduty", "macie", "cloudwatch", "kms", "hsm", "vault",
    # Endpoint / crypto
    "bitlocker", "filevault", "tls 1.2", "tls 1.3", "aes-256", "sha-256",
    "sha256", "rsa-2048", "rsa 2048", "fips 140", "pkcs#11", "mfa",
    # Vuln / config
    "tenable", "rapid7", "nessus", "wiz", "terraform", "ansible",
    # Roles / cadence
    "ciso", "isso", "sysadmin", "mssp", "quarterly review", "annual review",
    "incident response plan", "playbook",
}

_CONTROL_ID_PATTERN = re.compile(r"\b3\.\d{1,2}\.\d{1,2}\b")


class MappingDensityDetector:
    """Flags narratives with many control citations but few mechanism specifics."""

    NAME = "MappingDensity"
    NIST = ("3.12.4[b]", "3.12.4[c]")

    def __init__(self, ratio_threshold: float = 2.0):
        self.threshold = ratio_threshold

    def detect(self, artifact_id: str, text: str) -> Finding:
        lower = text.lower()
        control_mentions = len(_CONTROL_ID_PATTERN.findall(text))
        mechanism_hits = sum(lower.count(tok) for tok in MECHANISM_TOKENS)

        if control_mentions == 0 and mechanism_hits == 0:
            return Finding(
                self.NAME, artifact_id, 0.0,
                "No control refs or mechanism tokens; cannot evaluate.",
                self.NIST, "Artifact may be a summary; apply to narrative sections.",
            )

        denom = max(mechanism_hits, 1)
        ratio = control_mentions / denom

        score = 0.0
        if ratio > self.threshold:
            score = min(1.0, (ratio - self.threshold) / self.threshold)

        evidence = (
            f"control_id_mentions={control_mentions}; "
            f"mechanism_tokens={mechanism_hits}; ratio={ratio:.2f} "
            f"(threshold {self.threshold})"
        )
        rec = (
            "High citation-to-mechanism ratio is a hallmark of AI-drafted SSPs. "
            "Require every control narrative to name (a) the tool, (b) a config value, "
            "(c) the responsible role."
            if score >= 0.5
            else "Mechanism specificity within expected range."
        )
        return Finding(self.NAME, artifact_id, round(score, 3), evidence, self.NIST, rec)


# ---------------------------------------------------------------------------
# Heuristic 5 — Citation-Graph Anomaly
# ---------------------------------------------------------------------------

class CitationGraphDetector:
    """Flags evidence packets with shallow / orphan-heavy / cyclic citation graphs."""

    NAME = "CitationGraph"
    NIST = ("3.12.4[a]", "3.12.4[d]")

    def __init__(self, min_depth: int = 2, max_orphan_rate: float = 0.30,
                 min_nodes_for_analysis: int = 5):
        self.min_depth = min_depth
        self.max_orphan_rate = max_orphan_rate
        self.min_nodes = min_nodes_for_analysis

    def detect_packet(self, edges: list, nodes: list) -> Finding:
        if len(nodes) < self.min_nodes:
            return Finding(
                self.NAME, "PACKET", 0.0,
                f"Packet too small ({len(nodes)} nodes); skipping graph analysis.",
                self.NIST, "Add more artifacts before evaluating traceability.",
            )

        adjacency = defaultdict(set)
        reverse = defaultdict(set)
        for src, dst in edges:
            adjacency[src].add(dst)
            reverse[dst].add(src)

        orphans = [n for n in nodes if not adjacency[n] and not reverse[n]]
        orphan_rate = len(orphans) / len(nodes)

        # Cycle detection via iterative DFS (stack-safe for deep packets).
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {n: WHITE for n in nodes}
        cycles_found = 0

        for start in nodes:
            if color[start] != WHITE:
                continue
            stack = [(start, iter(adjacency[start]))]
            color[start] = GRAY
            while stack:
                node, it = stack[-1]
                try:
                    nxt = next(it)
                    c = color.get(nxt, WHITE)
                    if c == GRAY:
                        cycles_found += 1
                    elif c == WHITE:
                        color[nxt] = GRAY
                        stack.append((nxt, iter(adjacency[nxt])))
                except StopIteration:
                    color[node] = BLACK
                    stack.pop()

        # Max depth from every root (node with no incoming edges).
        max_depth = 0
        roots = [n for n in nodes if not reverse[n]]
        for root in roots:
            depth = 0
            frontier = {root}
            visited = {root}
            while frontier:
                nxt = set()
                for u in frontier:
                    for v in adjacency[u]:
                        if v not in visited:
                            nxt.add(v)
                            visited.add(v)
                if nxt:
                    depth += 1
                frontier = nxt
            if depth > max_depth:
                max_depth = depth

        depth_score = (self.min_depth - max_depth) / self.min_depth if max_depth < self.min_depth else 0.0
        orphan_score = ((orphan_rate - self.max_orphan_rate)
                        / max(1e-9, 1.0 - self.max_orphan_rate)
                        if orphan_rate > self.max_orphan_rate else 0.0)
        cycle_score = min(1.0, cycles_found * 0.3)

        score = max(0.0, min(1.0, max(depth_score, orphan_score, cycle_score)))

        evidence = (
            f"nodes={len(nodes)}; edges={len(edges)}; max_depth={max_depth}; "
            f"orphan_rate={orphan_rate:.2f}; cycles={cycles_found}"
        )
        rec = (
            "Evidence packet lacks traceable citation depth. "
            "Require every SSP claim to cite a policy; every policy to cite a procedure; "
            "every procedure to cite a raw log, config export, or timestamped screenshot."
            if score >= 0.5
            else "Citation-graph structure within expected range."
        )
        return Finding(self.NAME, "PACKET", round(score, 3), evidence, self.NIST, rec)


# ---------------------------------------------------------------------------
# Heuristic 7 — ArtifactSpecificityIndex (grounding-token ratio)  [v0.2 P1]
#
# Unanimous 7th-heuristic call from the April 21 war panel. The real attack
# surface of AI-era compliance evidence is the gap between named mechanisms
# (Okta, Splunk, YubiKey) and GROUNDED mechanisms (Okta tenant URL, Splunk
# saved-search name, YubiKey firmware version, ticket IDs, commit SHAs,
# timestamped artifact filenames). LLMs name, but they do not ground.
# ---------------------------------------------------------------------------

# Grounding-token regex family. Each pattern matches an artifact that cannot
# be hallucinated without real operational exposure: version strings, hex
# hashes, IPv4[:port], filesystem paths, UNC paths, S3 URIs, email addresses,
# ticket IDs, ISO dates, fiscal quarters, filenames with extensions, crypto
# algorithms with bit counts, hardware model strings, and tenant hostnames.
_GROUNDING_PATTERNS = [
    r"\bv?\d+\.\d+(?:\.\d+)?(?:-[a-zA-Z0-9]+)?\b",          # version strings
    r"\b[0-9a-f]{8,64}\b",                                    # hex hashes / SHAs
    r"\b(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?\b",                 # IPv4[:port]
    r"(?:^|[\s(])[A-Za-z]?[/\\][\w./\\\-]{6,}",              # abs paths
    r"\\\\[\w.$\-]+\\[\w./\\$\-]+",                           # UNC paths
    r"\bs3://[\w.\-]+",                                        # S3 URIs
    r"\b[\w\-]+@[\w.\-]+\.[a-z]{2,}\b",                        # emails
    r"\b(?:POAM|POA&M|INC|TICKET|MEMO|RFC|CVE|CR|TKT)[\-_]?\d+",  # ticket IDs
    r"\b\d{4}-\d{2}-\d{2}\b",                                  # ISO dates
    r"\b\d{4}Q[1-4]\b",                                        # fiscal quarter
    r"\b[\w\-]+\.(?:md|log|csv|pdf|xlsx|cfg|xml|json|tf|yml|yaml|py|sh)\b",
    r"\b[\w\-]+\.(?:okta|auth0|github|gitlab|slack|atlassian)\.com\b",
    r"\b(?:AES|SHA|RSA|ECDSA|HMAC|ECC)[\-]?\d{2,4}\b",         # crypto+bits
    r"\b[A-Z]{2,}[\-_]?\d{3,}\b",                              # hw model IDs
    r"\b(?:TLS|SSL|IPsec|IKE|SSH|SMB)[\- ]?v?\d+(?:\.\d+)?\b",  # protocol+ver
    r"\b\d{1,4}\s*(?:days?|hours?|minutes?|seconds?|months?|years?)\b",  # durations
]

_GROUNDING_RE = [re.compile(p, re.IGNORECASE) for p in _GROUNDING_PATTERNS]


class ArtifactSpecificityIndexDetector:
    """Flags narratives that name mechanisms without grounding them in artifacts.

    The core insight (war-panel consensus, April 21): an LLM can produce
    'Okta enforces MFA' at scale, but cannot, without a human operator,
    produce the tenant URL, YubiKey firmware version, ticket ID, commit SHA,
    or timestamped artifact filename that proves a real deployment.

    Scoring:
        * If mechanism_hits < min_mechanisms -> 0.0 (insufficient signal)
        * If grounding_hits == 0 and mechanism_hits >= min_mechanisms -> 1.0
        * ratio = grounding_hits / mechanism_hits
        * If ratio >= min_ratio -> 0.0 (clean)
        * Otherwise scale linearly from min_ratio (0.0) to 0 (1.0).

    Defends against the realistic humanization-pipeline evasion documented
    in HARDSEAL-AI-DETECTION-V0.1-REDTEAM: paraphrasing, mechanism-noun
    injection, and prompt-residue scrubbing cannot fabricate grounded
    operational detail without actual filesystem, git, ticketing, or
    identity-provider access.
    """

    NAME = "ArtifactSpecificityIndex"
    NIST = ("3.12.4[b]", "3.12.4[c]", "3.3.1[a]")

    def __init__(self, min_mechanisms: int = 4, min_ratio: float = 0.25):
        self.min_mechanisms = min_mechanisms
        self.min_ratio = min_ratio

    def detect(self, artifact_id: str, text: str) -> Finding:
        lower = text.lower()
        mech_hits = sum(lower.count(tok) for tok in MECHANISM_TOKENS)

        if mech_hits < self.min_mechanisms:
            return Finding(
                self.NAME, artifact_id, 0.0,
                f"mechanism_tokens={mech_hits} (<{self.min_mechanisms}); "
                f"insufficient signal for grounding analysis.",
                self.NIST,
                "Narrative too short or mechanism-sparse for this heuristic.",
            )

        grounding_hits = 0
        for pattern in _GROUNDING_RE:
            for _ in pattern.finditer(text):
                grounding_hits += 1

        if grounding_hits == 0:
            score = 1.0
            ratio = 0.0
        else:
            ratio = grounding_hits / mech_hits
            if ratio >= self.min_ratio:
                score = 0.0
            else:
                score = min(1.0, (self.min_ratio - ratio) / self.min_ratio)

        evidence = (
            f"mechanism_tokens={mech_hits}; grounding_tokens={grounding_hits}; "
            f"ratio={ratio:.2f} (floor {self.min_ratio})"
        )
        rec = (
            "Narrative names mechanisms without grounding. LLMs name tools; "
            "they cannot fabricate tenant URLs, firmware versions, ticket "
            "IDs, commit SHAs, or timestamped artifact paths. Require every "
            "control claim to cite a specific artifact ID a C3PAO can open."
            if score >= 0.5
            else "Artifact specificity within expected range."
        )
        return Finding(self.NAME, artifact_id, round(score, 3), evidence, self.NIST, rec)


# ---------------------------------------------------------------------------
# Heuristic 6 — Prompt-Leakage Signatures (highest-weight heuristic)
# ---------------------------------------------------------------------------

LEAKAGE_SIGNATURES = [
    r"\bas an ai language model\b",
    r"\bi('|)m sorry,?\s+but\b",
    r"\bi cannot (provide|help|assist)\b",
    r"\bcertainly!?\s+here\b",
    r"\bhere is (a|the) (revised|updated|improved)\b",
    r"\bi hope this helps\b",
    r"\bplease let me know if\b",
    r"\b(assistant|system|user)\s*:\s+",
    r"<\|im_(start|end)\|>",                 # ChatML tokens
    r"<\|endoftext\|>",
    r"\[INSERT [A-Z_ ]+ HERE\]",             # template placeholder
    r"\[TODO\]", r"\[TBD\]",
    r"\bchatgpt\b", r"\bgemini\b", r"\bcopilot\b",
    r"\bclaude(?:\s+ai)?\b",
]

_LEAK_RE = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in LEAKAGE_SIGNATURES]


class PromptLeakageDetector:
    """Detects residual LLM artifacts left in pasted text. Near-certain signal when positive."""

    NAME = "PromptLeakage"
    NIST = ("3.12.4[a]",)

    def detect(self, artifact_id: str, text: str) -> Finding:
        hits = []
        for pattern in _LEAK_RE:
            for m in pattern.finditer(text):
                hits.append((pattern.pattern, m.group(0)[:80]))

        score = min(1.0, len(hits) * 0.4) if hits else 0.0

        if hits:
            sample = "; ".join(f"{p!r} -> {m!r}" for p, m in hits[:3])
            evidence = f"{len(hits)} leakage signatures matched. Samples: {sample}"
            rec = (
                "CRITICAL: Raw LLM output detected in evidence artifact. "
                "Reject artifact and require human-authored replacement. "
                "Investigate whether CUI was pasted into a consumer LLM (3.1.3 violation)."
            )
        else:
            evidence = "No LLM-residue phrases detected."
            rec = "Clean."

        return Finding(self.NAME, artifact_id, round(score, 3), evidence, self.NIST, rec)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

# v0.2 P1 weight rebalance — rationale:
#   * PromptLeakage 0.25 -> 0.15: easiest heuristic for a literate adversary
#     to scrub in 10-15 minutes of editing. Keep it, but de-weight it.
#   * TimestampRegularity 0.20 -> 0.25: structural signal (clock skew, batch
#     spikes) is harder to fake than prose. Trust it more.
#   * ArtifactSpecificityIndex 0.00 -> 0.20: the unanimous war-panel 7th
#     heuristic. Grounded operational detail is the hardest thing for an
#     LLM to fabricate without real system access.
# Weights are relative; the aggregator normalizes by sum.
DEFAULT_WEIGHTS = {
    "SentenceStructureAnomaly": 0.10,
    "BoilerplateCluster":       0.15,
    "TimestampRegularity":      0.25,   # was 0.20
    "MappingDensity":           0.15,
    "CitationGraph":            0.15,
    "PromptLeakage":            0.15,   # was 0.25
    "ArtifactSpecificityIndex": 0.20,   # new in v0.2
}


class AIProvenanceDetector:
    """Runs all six heuristics and classifies the artifact or packet."""

    def __init__(self, weights: Optional[dict] = None,
                 template_guard: Optional[TemplateGuard] = None):
        self.weights = weights or DEFAULT_WEIGHTS
        self.template_guard = template_guard
        self.h_sentence = SentenceStructureAnomalyDetector(template_guard=template_guard)
        self.h_boilerplate = BoilerplateClusterDetector(template_guard=template_guard)
        self.h_timestamps = TimestampRegularityDetector()
        self.h_mapping = MappingDensityDetector()
        self.h_citation = CitationGraphDetector()
        self.h_leakage = PromptLeakageDetector()
        self.h_specificity = ArtifactSpecificityIndexDetector()

    def analyze_artifact(self, artifact_id: str, text: str,
                         timestamps: Optional[list] = None) -> Report:
        findings = [
            self.h_sentence.detect(artifact_id, text),
            self.h_mapping.detect(artifact_id, text),
            self.h_leakage.detect(artifact_id, text),
            self.h_specificity.detect(artifact_id, text),
        ]
        if timestamps:
            findings.append(self.h_timestamps.detect(artifact_id, timestamps))
        return self._aggregate(artifact_id, findings)

    def analyze_packet(self, narratives: dict,
                       citation_edges: Optional[list] = None,
                       timestamps_by_artifact: Optional[dict] = None) -> Report:
        findings = []
        for cid, text in narratives.items():
            findings.append(self.h_sentence.detect(cid, text))
            findings.append(self.h_mapping.detect(cid, text))
            findings.append(self.h_leakage.detect(cid, text))
            findings.append(self.h_specificity.detect(cid, text))

        findings.extend(self.h_boilerplate.detect_packet(narratives))

        if citation_edges is not None:
            findings.append(self.h_citation.detect_packet(
                citation_edges, list(narratives.keys())))

        if timestamps_by_artifact:
            for aid, ts in timestamps_by_artifact.items():
                findings.append(self.h_timestamps.detect(aid, ts))

        return self._aggregate("PACKET", findings)

    def _aggregate(self, artifact_id: str, findings: list) -> Report:
        # Take worst score per heuristic, then weighted average across heuristics.
        by_heuristic = {}
        for f in findings:
            cur = by_heuristic.get(f.heuristic, 0.0)
            if f.score > cur:
                by_heuristic[f.heuristic] = f.score

        total_w = sum(self.weights.get(h, 0.0) for h in by_heuristic)
        agg = (sum(by_heuristic[h] * self.weights.get(h, 0.0) for h in by_heuristic) / total_w
               if total_w > 0 else 0.0)

        confidence = self._classify(agg, by_heuristic)
        return Report(
            artifact_id=artifact_id,
            confidence=confidence,
            aggregate_score=round(agg, 3),
            findings=findings,
        )

    @staticmethod
    def _classify(agg: float, by_heuristic: dict) -> Confidence:
        strong = sum(1 for s in by_heuristic.values() if s >= 0.7)
        if strong >= 2 or agg >= 0.65:
            return Confidence.SYNTHETIC
        if strong >= 1 or agg >= 0.4:
            return Confidence.CONTAMINATED
        if agg >= 0.2:
            return Confidence.PARTIAL
        return Confidence.CLEAN


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _main(argv: Optional[list] = None) -> int:
    p = argparse.ArgumentParser(
        description="Hardseal AI-Era Evidence Contamination Detector (stdlib-only)",
    )
    p.add_argument("path", help="File (single-artifact) or directory (packet)")
    p.add_argument("--json", action="store_true", help="Output JSON report")
    p.add_argument(
        "--template", action="append", default=[], metavar="PATH",
        help=(
            "Baseline template file (consultant SSP skeleton, MSSP standard, "
            "GRC export) whose shingles should be subtracted before boilerplate "
            "analysis. Repeatable. Always active: NIST/CMMC stock-phrase whitelist."
        ),
    )
    args = p.parse_args(argv)

    target = Path(args.path)

    # Build template guard — always active (stock-phrase whitelist) even with
    # no --template files. If the user passes templates, they also contribute
    # their own baseline shingles.
    if args.template:
        guard = TemplateGuard.from_template_files(args.template)
    else:
        guard = TemplateGuard()
    detector = AIProvenanceDetector(template_guard=guard)

    if target.is_file():
        text = target.read_text(encoding="utf-8", errors="replace")
        report = detector.analyze_artifact(target.name, text)
    elif target.is_dir():
        # Template files passed via --template should not also be analyzed
        # as control narratives. Resolve both sides to absolute paths so
        # the compare is path-equivalence, not string-equivalence.
        template_paths = {Path(t).resolve() for t in args.template}
        narratives = {
            f.name: f.read_text(encoding="utf-8", errors="replace")
            for f in target.iterdir()
            if f.is_file() and f.suffix in (".md", ".txt")
            and f.resolve() not in template_paths
        }
        if not narratives:
            print(f"No .md/.txt artifacts in {target}", file=sys.stderr)
            return 2
        report = detector.analyze_packet(narratives)
    else:
        print(f"Path not found: {target}", file=sys.stderr)
        return 2

    if args.json:
        print(report.to_json())
    else:
        print(f"Artifact:         {report.artifact_id}")
        print(f"Confidence:       {report.confidence.value}")
        print(f"Aggregate Score:  {report.aggregate_score}")
        print(f"Findings ({len(report.findings)}):")
        for f in report.findings:
            print(f"  [{f.score:.2f}] {f.heuristic:28s} on {f.artifact_id}")
            print(f"       {f.evidence}")
            if f.recommendation and f.score >= 0.5:
                print(f"       ACTION: {f.recommendation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
