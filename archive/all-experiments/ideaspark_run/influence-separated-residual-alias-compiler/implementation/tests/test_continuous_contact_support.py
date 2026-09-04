from __future__ import annotations

import unittest

import numpy as np

from certify_continuous_contact_support import (
    array_digest_probe,
    assert_no_audit_payload_fields,
    boundary_eligibility,
    execute_nominal_contacts,
    fixed_budget_accounting,
    select_blocks,
    static_contact_config_hash,
    subtract_blocks,
    trace_matches_unedited_reference,
    SimulatorStepCounter,
)
from israc.certificate import FrameTrace, RolloutTrace


class ContinuousProtocolTests(unittest.TestCase):
    @staticmethod
    def _trace(state_value: float, rgb: str = "a" * 64) -> RolloutTrace:
        frame = FrameTrace(
            state=(state_value,),
            proprio=(0.0,),
            rgb_sha256=rgb,
            depth_sha256="b" * 64,
            physical_effect_probe=(0.0,),
            task_effect=(0.0,),
            contact_geom_pairs=((1, 2),),
        )
        return RolloutTrace("world", "action", 1, (frame,), ())

    def test_source_factual_match_uses_nominal_repeat_envelope(self) -> None:
        nominal = self._trace(0.0)
        repeated = self._trace(0.1)
        self.assertTrue(
            trace_matches_unedited_reference(self._trace(0.1), nominal, repeated)
        )
        self.assertFalse(
            trace_matches_unedited_reference(self._trace(0.106), nominal, repeated)
        )
        self.assertFalse(
            trace_matches_unedited_reference(
                self._trace(0.0, rgb="c" * 64), nominal, repeated
            )
        )

    def test_digest_covers_values_shape_and_dtype(self) -> None:
        left = np.zeros((2, 2), dtype=np.float32)
        right = left.copy()
        right[1, 1] = 1.0
        self.assertEqual(array_digest_probe(left), array_digest_probe(left.copy()))
        self.assertNotEqual(array_digest_probe(left), array_digest_probe(right))
        self.assertNotEqual(array_digest_probe(left), array_digest_probe(left.astype(np.float64)))

    def test_subtraction_is_geom_level(self) -> None:
        factual = {"geom:1:a": (1,), "geom:3:c": (3,)}
        candidate = {"geom:2:b": (2,), "geom:3:c": (3,)}
        self.assertEqual(subtract_blocks(candidate, factual), {"geom:2:b": (2,)})

    def test_candidate_selector_does_not_need_israc_count(self) -> None:
        pool = {f"geom:{index}": (index,) for index in range(10)}
        first = select_blocks(
            pool, selector="candidate-contact", max_blocks=3, seed=7
        )
        second = select_blocks(
            pool, selector="candidate-contact", max_blocks=3, seed=7
        )
        self.assertEqual(first, second)
        self.assertEqual(len(first), 3)

    def test_same_seed_rule_applies_to_israc_pool(self) -> None:
        pool = {f"geom:{index}": (index,) for index in range(10)}
        first = select_blocks(
            pool, selector="israc-contact-subtraction", max_blocks=3, seed=9
        )
        second = select_blocks(
            pool, selector="candidate-contact", max_blocks=3, seed=9
        )
        self.assertEqual(first, second)

    def test_priority_is_subset_consistent(self) -> None:
        full = {f"geom:{index}": (index,) for index in range(10)}
        subset = {key: value for key, value in full.items() if value[0] not in {1, 4, 8}}
        full_order = select_blocks(full, selector="candidate-contact", max_blocks=10, seed=31)
        subset_order = select_blocks(subset, selector="israc-contact-subtraction", max_blocks=10, seed=31)
        self.assertEqual([row for row in full_order if row[0] in subset], subset_order)

    def test_full_contact_config_hash_changes_one_endpoint(self) -> None:
        arrays = {
            "model.geom_solref": np.ones((4, 2), dtype=np.float64),
            "model.geom_friction": np.ones((4, 3), dtype=np.float64),
            "model.body_mass": np.ones((2,), dtype=np.float64),
        }
        left = static_contact_config_hash(arrays, (2,), "compliance", 0.004)
        right = static_contact_config_hash(arrays, (2,), "compliance", 0.100)
        self.assertNotEqual(left, right)

    def test_audit_payload_key_is_rejected(self) -> None:
        with self.assertRaises(RuntimeError):
            assert_no_audit_payload_fields({"wam_ranking": [1, 2]})
        assert_no_audit_payload_fields({"compiler_target_wam_blind": True})

    def test_endpoint_mismatch_fails_closed(self) -> None:
        eligible, reasons, tolerance = boundary_eligibility(
            1e-3, 0.0, {(1, 2)}, {(1, 2)}, {(2, 3)}, {(2, 3)}
        )
        self.assertFalse(eligible)
        self.assertIn("replayed_factual_endpoint_mismatches_saved_boundary", reasons)
        self.assertGreaterEqual(tolerance, 1e-10)

    def test_large_repeat_error_fails_closed(self) -> None:
        eligible, reasons, _ = boundary_eligibility(
            0.009, 0.5, {(1, 2)}, {(1, 2)}, {(2, 3)}, {(2, 3)}
        )
        self.assertFalse(eligible)
        self.assertIn("nominal_endpoint_repeat_exceeds_absolute_cap", reasons)

    def test_fixed_budget_uses_steps_and_charges_unused_pool(self) -> None:
        accounting = fixed_budget_accounting(
            factual_steps=8,
            candidate_steps=32,
            selected_blocks=1,
            max_blocks=3,
            boundary_eligible=True,
            measured_actual_steps=240,
        )
        self.assertEqual(accounting["actual_continuous_executions"], 6)
        self.assertEqual(accounting["charged_continuous_execution_cap"], 14)
        self.assertEqual(accounting["actual_simulator_steps"], 240)
        self.assertEqual(accounting["charged_simulator_step_cap"], 560)

    def test_p026_invalid_boundary_remains_zero_yield_but_fully_charged(self) -> None:
        accounting = fixed_budget_accounting(
            factual_steps=8,
            candidate_steps=32,
            selected_blocks=0,
            max_blocks=3,
            boundary_eligible=False,
            measured_actual_steps=80,
            charge_invalid=True,
        )
        self.assertEqual(accounting["actual_continuous_executions"], 2)
        self.assertEqual(accounting["charged_continuous_execution_cap"], 14)
        self.assertEqual(accounting["charged_simulator_step_cap"], 560)
        self.assertEqual(accounting["unused_simulator_step_budget"], 480)

    def test_nominal_execution_uses_real_step_counter(self) -> None:
        class Modes:
            def trace(self):
                return None

        class State:
            def flatten(self):
                return np.zeros(2, dtype=np.float64)

        class Sim:
            class Data:
                ncon = 0
                contact = ()
            data = Data()
            def get_state(self):
                return State()

        class Env:
            sim = Sim()
            def step(self, action):
                return {}, 0.0, False, {}

        counter = SimulatorStepCounter()
        execute_nominal_contacts(
            Env(), Modes(), lambda: None,
            np.zeros((3, 1)), np.zeros((5, 1)), counter,
        )
        self.assertEqual(counter.count, 8)


if __name__ == "__main__":
    unittest.main()
