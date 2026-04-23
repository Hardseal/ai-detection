# Contributing to Hardseal AI-Detection

Thanks for your interest in contributing. This project has a narrow
brief and a hard architectural rule. Both are important.

## The non-negotiable rule: stdlib only

Every module in this repository uses only the Python standard library.
The `import` statements at the top of the engine are:
`argparse`, `json`, `math`, `re`, `statistics`, `sys`, `collections`,
`dataclasses`, `datetime`, `enum`, `pathlib`, `typing`, `hashlib`.

Pull requests that add a third-party runtime dependency will be closed.

Why this is a rule, not a preference:

1. This detector runs inside a CUI-authorized enclave where every
   pip-installed dependency is an attack-surface review a C3PAO has
   to defend.
2. Deterministic behavior is a first-class feature. Third-party
   packages add nondeterminism risk from floating-point drift, lazy
   evaluation, model updates, or version skew.
3. A stdlib-only codebase can be supply-chain-audited in an afternoon.
   Dozens of transitive dependencies cannot.

If the thing you want to add is not expressible in stdlib, open an
issue to discuss the design before writing the code. There may be a
stdlib-only approach, or the feature may belong in a sister project.

## The test discipline

Every change ships with tests. No exceptions for "obvious" fixes. If a
detector threshold moves, a test asserts the new threshold. If a new
heuristic lands, it carries at least one positive case, one negative
case, and one edge case.

Run the full suite before sending a PR:

```
python3 -m unittest test_mismatch_engine_ai.py test_template_guard.py -v
```

All tests must pass. The CI workflow reruns them on Python 3.10, 3.11,
and 3.12.

## Commitment-hash integrity

If your change modifies any of the following:

1. `DEFAULT_WEIGHTS`
2. `LEAKAGE_SIGNATURES`
3. `_GROUNDING_PATTERNS`
4. `MECHANISM_TOKENS`

then you must also:

1. Run `python3 verify_commitment.py` to compute the new hashes.
2. Update the commitment-hash table in `README.md`.
3. Regenerate `bundle_v0.2.canonical.json` (or bump to a new
   versioned file for a new release line).
4. Note the scoring change in `CHANGELOG.md`.

Silent retuning of the scoring bundle is a trust-breaking failure.
Every scoring change is a dated, documented, verifiable event.

## Pull request format

Keep PRs narrowly scoped. A good PR changes one thing and includes:

1. A short description of the change and the motivation.
2. A link to the issue, if one exists.
3. Test coverage for the change.
4. A note if the commitment hashes moved, with the new values.

## Signing commits

Signed commits are encouraged but not required. If you sign, the
release notes will reflect the signing identity.

## License

By contributing, you agree that your contributions are licensed under
the MIT License. See `LICENSE`.
