from __future__ import annotations

import unittest

import numpy as np

from search_p027_blackbox_cem import (
    categorical_update,
    choose_distinct_blocks,
    evaluation_rank_key,
    sample_distinct_log_pair,
    truncated_log_sample,
)
from certify_continuous_contact_support import CONTINUOUS_EXECUTIONS_PER_BLOCK
from certify_p027_selected_plan import (
    certification_grid,
    invoke_base_main,
    reconstruct_selected,
)


class P027BlackboxCEMTest(unittest.TestCase):
    def test_categorical_update_is_normalized_and_smoothed(self) -> None:
        probabilities = categorical_update(3, [1, 1], 0.2)
        self.assertAlmostEqual(float(probabilities.sum()), 1.0)
        self.assertTrue(np.all(probabilities > 0.0))
        self.assertGreater(probabilities[1], probabilities[0])
        self.assertAlmostEqual(probabilities[0], probabilities[2])

    def test_empty_elite_update_is_uniform(self) -> None:
        np.testing.assert_allclose(categorical_update(4, [], 0.2), np.full(4, 0.25))

    def test_truncated_sample_stays_in_bounds(self) -> None:
        rng = np.random.default_rng(7)
        values = [truncated_log_sample(rng, 0.0, 5.0, -1.0, 1.0) for _ in range(100)]
        self.assertTrue(all(-1.0 <= value <= 1.0 for value in values))

    def test_distinct_selection_uses_best_feasible_activated_row(self) -> None:
        common = {
            "candidate_task_effect_max_abs_between_values": 1.0,
            "candidate_physical_effect_max_abs_between_values": 1.0,
            "parameter_values": [0.1, 1.0],
            "geom_ids": [1],
            "certifiable_proxy": True,
        }
        rows = [
            {**common, "parameter_address": "a", "score": 1.0, "feasible": True,
             "candidate_activated": True, "evaluation_index": 0},
            {**common, "parameter_address": "a", "score": 2.0, "feasible": True,
             "candidate_activated": True, "evaluation_index": 1},
            {**common, "parameter_address": "b", "score": 9.0, "feasible": False,
             "candidate_activated": True, "evaluation_index": 2},
            {**common, "parameter_address": "c", "score": 1.5, "feasible": True,
             "candidate_activated": True, "evaluation_index": 3},
        ]
        selected = choose_distinct_blocks(rows, 2)
        self.assertEqual([row["parameter_address"] for row in selected], ["a", "c"])
        self.assertEqual(selected[0]["evaluation_index"], 1)

    def test_continuous_pair_is_ordered_distinct_and_bounded(self) -> None:
        rng = np.random.default_rng(11)
        for _ in range(100):
            left, right = sample_distinct_log_pair(rng, 0.0, 5.0, -1.0, 1.0)
            self.assertGreater(right, left)
            self.assertGreaterEqual(left, -1.0)
            self.assertLessEqual(right, 1.0)

    def test_rank_key_prefers_state_then_task_then_physical(self) -> None:
        base = {
            "score": 2.0,
            "candidate_task_effect_max_abs_between_values": 1.0,
            "candidate_physical_effect_max_abs_between_values": 1.0,
            "evaluation_index": 3,
        }
        better = dict(base, score=3.0, evaluation_index=4)
        self.assertLess(evaluation_rank_key(better), evaluation_rank_key(base))

    def test_reconstruct_selected_rejects_noncanonical_indices(self) -> None:
        plan = {
            "evaluations": [
                {
                    "evaluation_index": 1,
                    "parameter_values": [0.1, 1.0],
                }
            ]
        }
        with self.assertRaises(ValueError):
            reconstruct_selected(plan)

    def test_selected_pair_preserves_frozen_p026_execution_accounting(self) -> None:
        grid = certification_grid([{"parameter_address": "a"}], (0.1, 0.9))
        self.assertEqual(len(grid), 3)
        self.assertEqual(len(grid) + 1, CONTINUOUS_EXECUTIONS_PER_BLOCK)
        self.assertAlmostEqual(grid[1], 0.3)

    def test_base_normal_system_exit_reaches_adapter_postchecks(self) -> None:
        calls: list[str] = []

        def exits_normally() -> None:
            calls.append("entered")
            raise SystemExit(0)

        invoke_base_main(exits_normally)
        calls.append("postcheck")
        self.assertEqual(calls, ["entered", "postcheck"])

    def test_base_nonzero_system_exit_is_not_swallowed(self) -> None:
        with self.assertRaises(SystemExit):
            invoke_base_main(lambda: (_ for _ in ()).throw(SystemExit(2)))


if __name__ == "__main__":
    unittest.main()
