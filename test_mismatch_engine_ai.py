"""
test_mismatch_engine_ai.py - Unit tests for the AI evidence contamination detector.
Stdlib-only. Run:

    python -m unittest test_mismatch_engine_ai.py -v
"""
from __future__ import annotations

import unittest
from datetime import datetime, timedelta

from mismatch_engine_ai import (
    AIProvenanceDetector,
    ArtifactSpecificityIndexDetector,
    BoilerplateClusterDetector,
    CitationGraphDetector,
    Confidence,
    MappingDensityDetector,
    PromptLeakageDetector,
    SentenceStructureAnomalyDetector,
    TimestampRegularityDetector,
)


# ---------------------------------------------------------------------------
# Heuristic 1 - Sentence structure
# ---------------------------------------------------------------------------

class TestSentenceStructureAnomaly(unittest.TestCase):

    def test_short_artifact_is_unscored(self):
        d = SentenceStructureAnomalyDetector()
        f = d.detect("short.md", "One sentence. Two sentence. Three.")
        self.assertEqual(f.score, 0.0)
        self.assertIn("Insufficient", f.evidence)

    def test_human_like_variance_passes(self):
        text = (
            "We enforce MFA. All administrative accounts at Hardseal require FIDO2 "
            "hardware tokens for authentication, with backup TOTP provisioned only "
            "after incident-commander approval and a 14-day review cycle. Okta is "
            "the IdP. Group Policy enforces session timeout at fifteen minutes. "
            "Nobody shares credentials. Passwords are rotated quarterly for service "
            "accounts. Splunk indexes all auth events. Reviews happen monthly."
        )
        d = SentenceStructureAnomalyDetector()
        f = d.detect("human.md", text)
        self.assertLess(f.score, 0.5, f"Unexpected flag: {f.evidence}")

    def test_flat_ai_like_output_flags(self):
        # 30 identical sentences -> zero variance -> score ~1.0
        text = " This control is implemented via policy." * 30
        d = SentenceStructureAnomalyDetector()
        f = d.detect("ai.md", text.strip())
        self.assertGreaterEqual(f.score, 0.5, f"Expected flag: {f.evidence}")


# ---------------------------------------------------------------------------
# Heuristic 2 - Boilerplate clustering
# ---------------------------------------------------------------------------

class TestBoilerplateCluster(unittest.TestCase):

    def test_distinct_narratives_pass(self):
        narratives = {
            "3.1.1": ("Access to CUI systems is gated through Okta with group-based "
                      "entitlements, reviewed quarterly by the ISSO."),
            "3.13.1": ("Boundary protection is enforced by a Palo Alto firewall "
                       "stack with inspection rules on all egress traffic."),
            "3.3.1": ("Splunk indexes syslog from all endpoints and routers, "
                      "retained for one year in an encrypted S3 bucket."),
        }
        d = BoilerplateClusterDetector()
        findings = d.detect_packet(narratives)
        for f in findings:
            self.assertLess(f.score, 0.5, f"Unexpected cluster for {f.artifact_id}: {f.evidence}")

    def test_cloned_narratives_flag_all(self):
        boilerplate = (
            "This control is implemented through a combination of policy, "
            "procedure, and technical configuration. Our security team reviews "
            "the control quarterly and documents evidence in the compliance "
            "repository. All findings are tracked in our POA&M and remediated "
            "according to severity."
        )
        narratives = {f"3.{i}.1": boilerplate for i in range(1, 6)}
        d = BoilerplateClusterDetector()
        findings = d.detect_packet(narratives)
        flagged = [f for f in findings if f.score >= 0.5]
        self.assertEqual(len(flagged), len(narratives),
                         "All cloned narratives should flag")


# ---------------------------------------------------------------------------
# Heuristic 3 - Timestamp regularity
# ---------------------------------------------------------------------------

class TestTimestampRegularity(unittest.TestCase):

    def test_too_few_samples_unscored(self):
        d = TimestampRegularityDetector()
        ts = [datetime(2026, 4, 1, 0, 0, i) for i in range(5)]
        f = d.detect("tiny.log", ts)
        self.assertEqual(f.score, 0.0)

    def test_poisson_like_log_passes(self):
        base = datetime(2026, 4, 1, 0, 0, 0, 123456)
        intervals = [3, 17, 1, 45, 8, 2, 91, 4, 33, 6, 22, 11, 58, 3, 14, 7, 29]
        ts = [base]
        for i in intervals:
            # bump microseconds to simulate real sub-second resolution
            next_ts = ts[-1] + timedelta(seconds=i, microseconds=(i * 7919) % 999999)
            ts.append(next_ts)
        d = TimestampRegularityDetector()
        f = d.detect("real.log", ts)
        self.assertLess(f.score, 0.5, f"Unexpected flag: {f.evidence}")

    def test_uniform_synthetic_log_flags(self):
        # Every 10 seconds on the second, no microseconds.
        base = datetime(2026, 4, 1, 0, 0, 0)
        ts = [base + timedelta(seconds=10 * i) for i in range(30)]
        d = TimestampRegularityDetector()
        f = d.detect("synth.log", ts)
        self.assertGreaterEqual(f.score, 0.5, f"Expected flag: {f.evidence}")

    def test_all_identical_timestamps_is_max_score(self):
        t = datetime(2026, 4, 1, 0, 0, 0)
        ts = [t for _ in range(15)]
        d = TimestampRegularityDetector()
        f = d.detect("dupe.log", ts)
        self.assertEqual(f.score, 1.0)


# ---------------------------------------------------------------------------
# Heuristic 4 - Mapping density
# ---------------------------------------------------------------------------

class TestMappingDensity(unittest.TestCase):

    def test_mechanism_heavy_text_passes(self):
        text = (
            "MFA is enforced via Okta and YubiKey FIDO2 tokens. "
            "TLS 1.3 is mandatory for all CUI transport. "
            "Splunk indexes CloudTrail events with SHA-256 integrity hashing. "
            "Intune enforces BitLocker on Windows endpoints. Azure AD Conditional "
            "Access blocks untrusted devices. Quarterly review by the CISO."
        )
        d = MappingDensityDetector()
        f = d.detect("mech.md", text)
        self.assertLess(f.score, 0.5, f"Unexpected flag: {f.evidence}")

    def test_citation_heavy_empty_text_flags(self):
        text = (
            "Per 3.1.1, 3.1.2, 3.1.3, 3.1.4, 3.1.5, and 3.13.1 through 3.13.16, "
            "we implement the required controls. 3.3.1 and 3.3.2 are satisfied. "
            "3.5.1, 3.5.2, 3.5.3 are implemented. 3.14.1, 3.14.2, 3.14.3 apply."
        )
        d = MappingDensityDetector()
        f = d.detect("ai.md", text)
        self.assertGreaterEqual(f.score, 0.5, f"Expected flag: {f.evidence}")


# ---------------------------------------------------------------------------
# Heuristic 5 - Citation graph
# ---------------------------------------------------------------------------

class TestCitationGraph(unittest.TestCase):

    def test_packet_too_small_unscored(self):
        d = CitationGraphDetector()
        f = d.detect_packet([], ["a", "b"])
        self.assertEqual(f.score, 0.0)

    def test_layered_graph_passes(self):
        nodes = ["ssp", "access_policy", "mfa_procedure", "okta_log_query",
                 "incident_runbook", "config_baseline"]
        edges = [
            ("ssp", "access_policy"),
            ("access_policy", "mfa_procedure"),
            ("mfa_procedure", "okta_log_query"),
            ("ssp", "incident_runbook"),
            ("incident_runbook", "config_baseline"),
        ]
        d = CitationGraphDetector()
        f = d.detect_packet(edges, nodes)
        self.assertLess(f.score, 0.5, f"Unexpected flag: {f.evidence}")

    def test_shallow_graph_flags(self):
        nodes = [f"doc_{i}" for i in range(8)]
        edges = [("doc_0", "doc_1"), ("doc_2", "doc_3")]
        d = CitationGraphDetector()
        f = d.detect_packet(edges, nodes)
        self.assertGreaterEqual(f.score, 0.5, f"Expected flag: {f.evidence}")

    def test_cycle_detected(self):
        nodes = ["a", "b", "c", "d", "e"]
        edges = [("a", "b"), ("b", "c"), ("c", "a"), ("d", "e")]
        d = CitationGraphDetector()
        f = d.detect_packet(edges, nodes)
        self.assertIn("cycles=", f.evidence)


# ---------------------------------------------------------------------------
# Heuristic 6 - Prompt leakage
# ---------------------------------------------------------------------------

class TestPromptLeakage(unittest.TestCase):

    def test_clean_text_passes(self):
        text = "Okta enforces MFA for all administrators. Reviewed quarterly by ISSO."
        d = PromptLeakageDetector()
        f = d.detect("policy.md", text)
        self.assertEqual(f.score, 0.0)

    def test_llm_residue_flags_hard(self):
        text = (
            "As an AI language model, I cannot provide specific legal advice. "
            "However, here is a revised access control policy: [INSERT COMPANY NAME HERE]. "
            "I hope this helps!"
        )
        d = PromptLeakageDetector()
        f = d.detect("leaked.md", text)
        self.assertGreaterEqual(f.score, 0.8)

    def test_chatml_tokens_flag(self):
        text = "Access control policy.\n<|im_start|>assistant: The policy is...<|im_end|>"
        d = PromptLeakageDetector()
        f = d.detect("chatml.md", text)
        self.assertGreater(f.score, 0.0)


# ---------------------------------------------------------------------------
# Heuristic 7 - Artifact Specificity Index (grounding-token ratio)  [v0.2]
# ---------------------------------------------------------------------------

class TestArtifactSpecificityIndex(unittest.TestCase):

    def test_mechanism_sparse_text_unscored(self):
        d = ArtifactSpecificityIndexDetector()
        # One mechanism mention, nothing to evaluate
        f = d.detect("short.md", "We enforce MFA via the IdP.")
        self.assertEqual(f.score, 0.0)
        self.assertIn("insufficient signal", f.evidence)

    def test_named_mechanisms_with_zero_grounding_flags_hard(self):
        # Classic LLM output: names mechanisms, grounds none of them.
        text = (
            "Our environment uses Okta for identity, Splunk for logging, "
            "YubiKey for MFA, and BitLocker for disk encryption. Defender "
            "handles EDR. Active Directory manages group policy. Quarterly "
            "review is performed by the ISSO."
        )
        d = ArtifactSpecificityIndexDetector()
        f = d.detect("ai.md", text)
        self.assertGreaterEqual(f.score, 0.9,
                                f"Zero-grounding narrative must flag hard: {f.evidence}")

    def test_grounded_narrative_passes(self):
        # Real operational detail: versions, paths, tenant, ticket, dates, hash
        text = (
            "Okta tenant widgetdefense.okta.com gates access. YubiKey FIDO2 "
            "firmware 5.4.3 is provisioned to every admin. Splunk 9.3.2 "
            "indexes events into s3://widgetdefense-cui-audit-cold with "
            "SHA-256 integrity. Entitlement review ran 2026-03-18 per "
            "POAM-2026-047. Firewall config commit a3f91b7e8d2c pushed "
            "to infra-fw-prod. Retention 365 days. Owner Janelle Ruiz at "
            "janelle.ruiz@widgetdefense.com."
        )
        d = ArtifactSpecificityIndexDetector()
        f = d.detect("real.md", text)
        self.assertLess(f.score, 0.5,
                        f"Well-grounded narrative should not flag: {f.evidence}")

    def test_partial_grounding_partial_score(self):
        # Some mechanisms, only one grounding token -> low ratio -> partial flag
        text = (
            "Okta enforces MFA across all CUI users. Splunk indexes the "
            "relevant audit logs. BitLocker handles endpoint encryption. "
            "Defender runs on every Windows host. The ISSO reviews quarterly. "
            "Evidence is retained for 365 days."
        )
        d = ArtifactSpecificityIndexDetector()
        f = d.detect("partial.md", text)
        # Not zero (one duration token "365 days"), not a hard flag either
        self.assertGreater(f.score, 0.0)


# ---------------------------------------------------------------------------
# Orchestrator - full end-to-end
# ---------------------------------------------------------------------------

class TestOrchestrator(unittest.TestCase):

    def test_clean_packet_is_clean_or_partial(self):
        narratives = {
            "3.1.1": (
                "Access to CUI systems is controlled through Okta Single Sign-On. "
                "All administrators authenticate using YubiKey FIDO2 hardware tokens. "
                "The ISSO reviews all access entitlements on a quarterly cadence, "
                "referencing the access-review log stored in Splunk. Documented "
                "exceptions require written approval and expire in 90 days."
            ),
            "3.13.1": (
                "Network boundaries are enforced by a Palo Alto PA-3220 firewall "
                "stack. Firewall rules are managed under version control and "
                "peer-reviewed before deployment via Terraform. All east-west "
                "traffic passes through an inspection layer logging to Splunk "
                "with SHA-256 flow integrity. Reviewed monthly by the ISSO."
            ),
            "3.3.1": (
                "Splunk indexes syslog from every endpoint, router, and switch "
                "with a one-year retention period. Logs are replicated to an "
                "AES-256-encrypted S3 bucket with object-lock. Quarterly review "
                "by the ISSO validates coverage of all in-scope assets."
            ),
        }
        d = AIProvenanceDetector()
        report = d.analyze_packet(narratives)
        self.assertIn(report.confidence, (Confidence.CLEAN, Confidence.PARTIAL),
                      f"Unexpected: {report.to_json()}")

    def test_contaminated_packet_classifies_synthetic(self):
        boilerplate = (
            "As an AI language model, this control is implemented through "
            "policy and procedure. Per 3.1.1 and 3.13.1 we ensure compliance. "
            "[INSERT TOOL HERE] enforces the control. Per 3.3.1 and 3.12.1 "
            "documentation is maintained. Per 3.14.1 systems are updated. "
            "Certainly! Here is the revised approach."
        )
        narratives = {f"3.{i}.1": boilerplate for i in range(1, 5)}
        d = AIProvenanceDetector()
        report = d.analyze_packet(narratives)
        self.assertEqual(report.confidence, Confidence.SYNTHETIC,
                         f"Expected SYNTHETIC, got: {report.to_json()}")

    def test_determinism(self):
        narratives = {
            "3.1.1": ("Okta enforces MFA quarterly. Splunk indexes CloudTrail. "
                      "Reviewed by the ISSO monthly. BitLocker on endpoints.")
        }
        d = AIProvenanceDetector()
        r1 = d.analyze_packet(narratives)
        r2 = d.analyze_packet(narratives)
        self.assertEqual(r1.aggregate_score, r2.aggregate_score)
        self.assertEqual(r1.confidence, r2.confidence)

    def test_json_serialization(self):
        narratives = {"3.1.1": "Okta with MFA. Reviewed quarterly by ISSO."}
        d = AIProvenanceDetector()
        report = d.analyze_packet(narratives)
        j = report.to_json()
        self.assertIn('"confidence"', j)
        self.assertIn('"aggregate_score"', j)


if __name__ == "__main__":
    unittest.main()
