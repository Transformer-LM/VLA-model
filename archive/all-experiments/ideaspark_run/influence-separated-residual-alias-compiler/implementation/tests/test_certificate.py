from __future__ import annotations

import unittest
from dataclasses import replace
import hashlib
import math

from israc.certificate import AliasCertificate, NoiseEnvelope, certify_alias_pair
from israc.toy_physics import action_indexed_copy, make_world, rollout


class CertificateTests(unittest.TestCase):
    def setUp(self) -> None:
        low = make_world("world_low", 0.10)
        high = make_world("world_high", 1.10)
        self.factual_low = rollout(low, "factual_free", 1)
        self.factual_high = rollout(high, "factual_free", 1)
        self.candidate_low = rollout(low, "candidate_contact", 2)
        self.candidate_high = rollout(high, "candidate_contact", 2)
        self.envelope = NoiseEnvelope(0.0, 0.0, 0.0, 1e-12)
        self.certificate = AliasCertificate(
            factual_action_id="factual_free",
            candidate_action_id="candidate_contact",
            top_k=8,
            search_objective_terms=("task_effect_separation", "factual_transcript_constraint"),
            compiler_seed=20260831,
            simulator="toy-only",
            task_id="contact-transfer-unit-test",
            snapshot_id="deterministic-s0",
            allowed_activation_lag=0,
        )

    def certify(self, **changes):
        values = {
            "factual_plus": self.factual_low,
            "factual_minus": self.factual_high,
            "candidate_plus": self.candidate_low,
            "candidate_minus": self.candidate_high,
            "certificate": self.certificate,
            "envelope": self.envelope,
        }
        values.update(changes)
        return certify_alias_pair(**values)

    def test_valid_physical_alias_passes(self) -> None:
        result = self.certify()
        self.assertTrue(result.passed, result.failures)
        self.assertEqual(
            result.certificate_sha256,
            hashlib.sha256(result.canonical_payload.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(result.measurements["candidate_first_divergence_frame"], 3)
        self.assertEqual(result.measurements["parameter_first_activation_frame"], 3)

    def test_action_indexed_parameter_is_rejected(self) -> None:
        result = self.certify(
            factual_plus=action_indexed_copy(self.factual_low),
            candidate_plus=action_indexed_copy(self.candidate_low),
        )
        self.assertFalse(result.passed)
        self.assertIn("action_conditioned_parameter_forbidden", result.failures)

    def test_target_wam_objective_is_rejected(self) -> None:
        certificate = AliasCertificate(
            **{**self.certificate.__dict__, "search_objective_terms": ("target_wam",)}
        )
        result = self.certify(certificate=certificate)
        self.assertFalse(result.passed)
        self.assertIn("target_wam_leaked_into_compiler_objective", result.failures)

    def test_low_support_candidate_is_rejected(self) -> None:
        low = rollout(make_world("world_low", 0.10), "candidate_contact", 9)
        high = rollout(make_world("world_high", 1.10), "candidate_contact", 9)
        result = self.certify(candidate_plus=low, candidate_minus=high)
        self.assertFalse(result.passed)
        self.assertIn("candidate_outside_policy_top_k", result.failures)

    def test_nonfinite_trace_and_envelope_fail_closed(self) -> None:
        first = self.factual_low.frames[0]
        broken = replace(
            self.factual_low,
            frames=(replace(first, state=(math.nan,)),) + self.factual_low.frames[1:],
        )
        result = self.certify(factual_plus=broken)
        self.assertFalse(result.passed)
        self.assertIn("trace_contains_nonfinite_or_invalid_digest", result.failures)
        result = self.certify(envelope=replace(self.envelope, state=math.inf))
        self.assertFalse(result.passed)
        self.assertIn("factual_state_envelope_invalid", result.failures)

    def test_two_changed_blocks_are_rejected(self) -> None:
        def add_block(trace):
            second = replace(
                trace.parameters[0],
                block_id="second_contact_block",
                engine_field="geom_friction[second]",
            )
            return replace(trace, parameters=trace.parameters + (second,))

        result = self.certify(
            factual_plus=add_block(self.factual_low),
            factual_minus=add_block(self.factual_high),
            candidate_plus=add_block(self.candidate_low),
            candidate_minus=add_block(self.candidate_high),
        )
        self.assertFalse(result.passed)
        self.assertIn("expected_exactly_one_changed_parameter_block", result.failures)

    def test_certificate_hash_binds_evidence_hash(self) -> None:
        left = self.certify(
            certificate=replace(self.certificate, evidence_sha256=("a" * 64,))
        )
        right = self.certify(
            certificate=replace(self.certificate, evidence_sha256=("b" * 64,))
        )
        self.assertNotEqual(left.certificate_sha256, right.certificate_sha256)

    def test_factual_digest_mismatch_is_rejected(self) -> None:
        first = self.factual_high.frames[0]
        broken = replace(
            self.factual_high,
            frames=(replace(first, rgb_sha256="f" * 64),) + self.factual_high.frames[1:],
        )
        result = self.certify(factual_minus=broken)
        self.assertFalse(result.passed)
        self.assertIn("factual_rgb_digest_mismatch", result.failures)

    def test_divergence_before_activation_is_rejected(self) -> None:
        frames = list(self.candidate_high.frames)
        frames[2] = replace(frames[2], state=(99.0, 99.0))
        result = self.certify(candidate_minus=replace(self.candidate_high, frames=tuple(frames)))
        self.assertFalse(result.passed)
        self.assertIn("candidate_diverges_before_physical_activation", result.failures)

    def test_changed_parameter_activation_in_factual_is_rejected(self) -> None:
        block_id = self.factual_low.parameters[0].block_id
        low_frames = list(self.factual_low.frames)
        high_frames = list(self.factual_high.frames)
        low_frames[1] = replace(low_frames[1], active_parameter_blocks=(block_id,))
        high_frames[1] = replace(high_frames[1], active_parameter_blocks=(block_id,))
        result = self.certify(
            factual_plus=replace(self.factual_low, frames=tuple(low_frames)),
            factual_minus=replace(self.factual_high, frames=tuple(high_frames)),
        )
        self.assertFalse(result.passed)
        self.assertIn("changed_parameter_activated_in_factual", result.failures)
        self.assertEqual(
            result.measurements["parameter_first_factual_activation_frame"], 1
        )


if __name__ == "__main__":
    unittest.main()
