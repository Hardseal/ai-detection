#!/usr/bin/env python3
"""
verify_commitment.py - Reproduce the v0.2 commitment hashes.

Publishes a tamper-evidence guarantee: the weights and regex bundles that
control scoring in this release are frozen. If the published SHA-256 in
the README differs from what this script computes, the scoring logic has
been modified since publication.

Run:
    python3 verify_commitment.py

Expected output: four per-field hashes and one combined bundle hash,
matching the values in README.md under "Commitment Hashes (v0.2)".

Zero external dependencies. Stdlib only.
"""
from __future__ import annotations

import hashlib
import json
import sys

import mismatch_engine_ai as m


def canonical_bytes(obj) -> bytes:
    """Deterministic JSON encoding: sorted keys, no whitespace, UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def sha256_hex(obj) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def main() -> int:
    bundle = {
        "version": "0.2",
        "generated": "2026-04-21",
        "weights": dict(m.DEFAULT_WEIGHTS),
        "leakage_signatures": list(m.LEAKAGE_SIGNATURES),
        "grounding_patterns": list(m._GROUNDING_PATTERNS),
        "mechanism_tokens": sorted(m.MECHANISM_TOKENS),
    }

    print("Hardseal AI-Detection v0.2 Commitment Verification")
    print("=" * 60)
    print(f"weights             sha256={sha256_hex(bundle['weights'])}")
    print(f"leakage_signatures  sha256={sha256_hex(bundle['leakage_signatures'])}")
    print(f"grounding_patterns  sha256={sha256_hex(bundle['grounding_patterns'])}")
    print(f"mechanism_tokens    sha256={sha256_hex(bundle['mechanism_tokens'])}")
    print(f"COMBINED BUNDLE     sha256={sha256_hex(bundle)}")
    print()
    print(f"Bundle contents: {len(bundle['weights'])} weights, "
          f"{len(bundle['leakage_signatures'])} leakage regexes, "
          f"{len(bundle['grounding_patterns'])} grounding regexes, "
          f"{len(bundle['mechanism_tokens'])} mechanism tokens.")
    print()
    print("Compare against the hashes published in README.md.")
    print("If any hash differs, scoring logic has been modified since publication.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
