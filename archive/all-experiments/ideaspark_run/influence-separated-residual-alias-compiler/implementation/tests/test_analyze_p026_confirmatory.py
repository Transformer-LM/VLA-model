from __future__ import annotations

import unittest
from pathlib import Path

from analyze_p026_confirmatory import (
    assert_equal_fields,
    distinct_witness_count,
    extended_empirical_quantile,
    hierarchical_ratio_bootstrap,
    validate_locked_path_set,
)


def row(*keys: str, charged: int = 100) -> dict:
    return {
        "blocks": [
            {"witness_key": key, "unique_witness": 1} for key in keys
        ],
        "unique_witness_count": len(keys),
        "charged_simulator_step_cap": charged,
    }


class AnalyzeP026Tests(unittest.TestCase):
    def test_cross_seed_duplicate_witness_is_counted_once(self) -> None:
        self.assertEqual(
            distinct_witness_count([row("same"), row("same"), row("same")]),
            1,
        )

    def test_extended_percentile_preserves_infinity(self) -> None:
        self.assertEqual(
            extended_empirical_quantile([float("inf")] * 100, 0.025),
            "infinite",
        )

    def test_zero_over_zero_bootstrap_is_neutral_not_removed(self) -> None:
        key = ("source", 1)
        selectors = ("israc-contact-subtraction", "candidate-contact")
        index = {
            selector: {seed: {key: row()} for seed in (0, 1, 2)}
            for selector in selectors
        }
        result = hierarchical_ratio_bootstrap(
            index,
            selectors[0],
            selectors[1],
            {"source": [key]},
            [0, 1, 2],
            1000,
            7,
        )
        self.assertEqual(result["ci95"], [1.0, 1.0])
        self.assertFalse(result["ci_lower_gt_1"])
        self.assertEqual(result["undefined_zero_over_zero_samples"], 1000)

    def test_positive_over_zero_bootstrap_retains_infinity(self) -> None:
        key = ("source", 1)
        index = {
            "israc-contact-subtraction": {
                seed: {key: row("source-boundary-geom")} for seed in (0, 1, 2)
            },
            "candidate-contact": {
                seed: {key: row()} for seed in (0, 1, 2)
            },
        }
        result = hierarchical_ratio_bootstrap(
            index,
            "israc-contact-subtraction",
            "candidate-contact",
            {"source": [key]},
            [0, 1, 2],
            1000,
            9,
        )
        self.assertEqual(result["ci95"], ["infinite", "infinite"])
        self.assertTrue(result["ci_lower_gt_1"])

    def test_cross_cell_invariant_mismatch_fails(self) -> None:
        with self.assertRaises(ValueError):
            assert_equal_fields(
                [{"boundary_eligible": True}, {"boundary_eligible": False}],
                ("boundary_eligible",),
                "synthetic-boundary",
            )

    def test_locked_path_set_rejects_missing_duplicate_and_extra(self) -> None:
        with self.assertRaises(ValueError):
            validate_locked_path_set([Path("a")], 2, require_exists=False)
        with self.assertRaises(ValueError):
            validate_locked_path_set([Path("a"), Path("a")], 2, require_exists=False)
        with self.assertRaises(ValueError):
            validate_locked_path_set(
                [Path("a"), Path("b"), Path("c")], 2, require_exists=False
            )


if __name__ == "__main__":
    unittest.main()
