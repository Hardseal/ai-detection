"""
template_guard.py — Template False-Positive Guard for mismatch_engine_ai.py
=========================================================================

v0.2 — April 21, 2026. Implements the unanimous April-21 war-panel finding:
the single most embarrassing false positive is a legitimate heavily-templated
CMMC evidence packet (consultant-built SSP, MSSP-standardized narrative,
GRC-exported document) being flagged as AI-contaminated by v0.1 heuristics
1 (SentenceStructure) and 2 (BoilerplateCluster) that fire on any uniform,
stock-phrase-dense prose.

Defends against:
    - Consultants reusing identical phrasing across 50+ control narratives
    - MSSP standard templates deployed across multi-site SMB contractors
    - Legacy hand-written but templated Word-template SSPs
    - GRC tooling that auto-generates rhythmically uniform SSP sections

Two mechanisms:
    1. Hardcoded NIST/CMMC stock-phrase whitelist — always active. These are
       legitimate SSP stock phrases that appear in almost every compliant
       packet. Counting them against the contractor is a bug.
    2. User-supplied baseline template(s) — optional. Pre-ingest the skeleton
       the contractor (or their MSSP) actually uses and subtract its shingles
       before Jaccard similarity is computed.

Sacred-rule compliant:
    - Stdlib-only (re, pathlib)
    - Deterministic
    - No network
    - Auditable in ten minutes

C3PAO question this answers:
    "Would this tool ever flag my standard consultant-built SSP as synthetic?"
    With TemplateGuard active: no, provided the template is pre-ingested or
    the stock phrases cover the uniform regions.

License: Proprietary — Hardseal LLC. Open-source release July 2026.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Optional

__all__ = ["TemplateGuard", "NIST_STOCK_PHRASES"]


# ---------------------------------------------------------------------------
# Hardcoded NIST/CMMC stock-phrase whitelist.
#
# These are phrases that appear verbatim in almost every legitimate SSP, POA&M,
# or CMMC readiness packet. They are NOT evidence of AI contamination; they are
# evidence of following NIST 800-171 / CMMC AB-standard language.
#
# Do NOT add phrases that overlap with LEAKAGE_SIGNATURES in the main engine
# (e.g. "I hope this helps", "As an AI language model"). Those are AI
# contamination markers and must still flag.
# ---------------------------------------------------------------------------

NIST_STOCK_PHRASES: tuple = (
    # Document / framework names
    "system security plan",
    "plan of action and milestones",
    "plan of action",
    "nist sp 800-171",
    "nist 800-171",
    "nist sp 800-171a",
    "nist 800-171a",
    "nist sp 800-53",
    "cmmc level 2",
    "cmmc level 1",
    "cmmc 2.0",
    "cyber ab",
    "c3pao",
    "assessment objective",
    "assessment objectives",
    "joint surveillance",
    # Standard SSP framing language
    "policy, procedure, and technical configuration",
    "combination of policy, procedure",
    "policy and procedure",
    "technical configuration",
    "implementation statement",
    "evidence of implementation",
    "shared responsibility",
    "external service provider",
    "responsible role",
    "inherited from",
    "customer responsibility matrix",
    "the organization implements",
    "the organization ensures",
    "the organization requires",
    "the organization has",
    # Review / cadence language
    "reviews the control quarterly",
    "reviews this control quarterly",
    "quarterly review",
    "annual review",
    "continuous monitoring",
    "reviewed and approved",
    "reviewed annually",
    "documented in the compliance repository",
    "tracked in our poa",
    "tracked in our poa&m",
    "tracked in the poa&m",
    "remediated according to severity",
    "in accordance with",
    "applicable nist",
    "all applicable",
    "the required audit controls",
    "the required controls",
    # CUI / boundary
    "controlled unclassified information",
    "cui boundary",
    "cui environment",
    "covered defense information",
    "defense industrial base",
    "federal contract information",
    # Assessor verbs
    "examine", "interview", "test",
)


class TemplateGuard:
    """Subtracts legitimate templated content before AI-contamination scoring.

    Instantiate once per assessment. Pass into AIProvenanceDetector via the
    `template_guard` kwarg. BoilerplateClusterDetector and
    SentenceStructureAnomalyDetector will consult it automatically.

    Parameters
    ----------
    extra_stock_phrases : iterable of str, optional
        Additional contractor-specific stock phrases to whitelist. Case
        insensitive. Appended to NIST_STOCK_PHRASES.
    shingle_size : int, default 5
        k for k-shingle extraction. Must match the BoilerplateCluster k.

    Examples
    --------
    >>> guard = TemplateGuard()
    >>> guard.strip_boilerplate("Per NIST 800-171 we review quarterly.")
    '  we   .'

    >>> guard = TemplateGuard.from_template_file("our_mssp_skeleton.md")
    >>> guard.template_match_ratio({"foo bar baz quux zap"})
    0.0
    """

    STOCK_PHRASES: tuple = NIST_STOCK_PHRASES

    def __init__(
        self,
        extra_stock_phrases: Iterable[str] = (),
        shingle_size: int = 5,
    ) -> None:
        self.k: int = int(shingle_size)
        merged = tuple(s.lower() for s in self.STOCK_PHRASES)
        extras = tuple(s.lower() for s in extra_stock_phrases)
        # Sort by length descending so longer phrases strip first.
        self.stock_phrases: tuple = tuple(
            sorted(set(merged + extras), key=lambda s: -len(s))
        )
        self._stock_re: Optional[re.Pattern] = None
        if self.stock_phrases:
            self._stock_re = re.compile(
                "|".join(re.escape(p) for p in self.stock_phrases),
                re.IGNORECASE,
            )
        self.template_shingles: set = set()
        self._source_paths: list = []

    # ------------------------------------------------------------------ factories

    @classmethod
    def from_template_file(
        cls, path, **kwargs
    ) -> "TemplateGuard":
        guard = cls(**kwargs)
        guard.add_template_file(path)
        return guard

    @classmethod
    def from_template_files(
        cls, paths: Iterable, **kwargs
    ) -> "TemplateGuard":
        guard = cls(**kwargs)
        for p in paths:
            guard.add_template_file(p)
        return guard

    # ------------------------------------------------------------------ ingest

    def add_template(self, text: str) -> int:
        """Extract k-shingles from a baseline template and cache for subtraction.

        Returns the number of shingles added (excluding duplicates).
        """
        tokens = re.findall(r"\b\w+\b", text.lower())
        if len(tokens) < self.k:
            return 0
        before = len(self.template_shingles)
        for i in range(len(tokens) - self.k + 1):
            self.template_shingles.add(" ".join(tokens[i : i + self.k]))
        return len(self.template_shingles) - before

    def add_template_file(self, path) -> int:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Template not found: {p}")
        self._source_paths.append(str(p))
        return self.add_template(p.read_text(encoding="utf-8", errors="replace"))

    # ------------------------------------------------------------------ query

    def strip_boilerplate(self, text: str) -> str:
        """Remove stock-phrase occurrences so sentence analysis isn't dampened.

        Returns text with stock phrases replaced by a single space. Punctuation
        survives, sentence boundaries (.!?) are preserved, so the downstream
        sentence splitter still works.
        """
        if not self._stock_re:
            return text
        return self._stock_re.sub(" ", text)

    def filter_shingles(self, shingles: set) -> set:
        """Return a copy of `shingles` with template baseline shingles removed."""
        if not self.template_shingles:
            return set(shingles)
        return set(shingles) - self.template_shingles

    def template_match_ratio(self, shingles: set) -> float:
        """Fraction of the artifact's shingles that match the baseline template."""
        if not shingles or not self.template_shingles:
            return 0.0
        return len(shingles & self.template_shingles) / len(shingles)

    def stock_phrase_density(self, text: str) -> float:
        """Fraction of characters in `text` covered by a stock-phrase match.

        Useful for diagnostics and for orchestrator-level dampening. Returns a
        value in [0.0, 1.0]. 0.0 means no stock phrases; 1.0 means the entire
        text is stock phrases.
        """
        if not text or not self._stock_re:
            return 0.0
        covered = 0
        for m in self._stock_re.finditer(text):
            covered += len(m.group(0))
        return min(1.0, covered / len(text))

    # ------------------------------------------------------------------ introspection

    def describe(self) -> dict:
        return {
            "k": self.k,
            "stock_phrase_count": len(self.stock_phrases),
            "template_shingle_count": len(self.template_shingles),
            "source_paths": list(self._source_paths),
        }

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"TemplateGuard(k={self.k}, "
            f"stock_phrases={len(self.stock_phrases)}, "
            f"template_shingles={len(self.template_shingles)})"
        )
