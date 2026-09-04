from __future__ import annotations

import copy
import hashlib
import json
import unittest

from analyze_p025_fixed_budget import analyze, boundary_key, validate_record


def record(selector: str, seed: int, boundary: int, witnesses: int) -> dict:
    blocks = []
    for index in range(3):
        passed = int(index < witnesses)
        left = {"path": f"/tmp/{selector}-{seed}-{boundary}-{index}-left", "sha256": f"{index + 1:064x}"}
        middle = {"path": f"/tmp/{selector}-{seed}-{boundary}-{index}-middle", "sha256": f"{index + 10:064x}"}
        right = {"path": f"/tmp/{selector}-{seed}-{boundary}-{index}-right", "sha256": f"{index + 4:064x}"}
        repeat = {"path": f"/tmp/{selector}-{seed}-{boundary}-{index}-repeat", "sha256": f"{index + 7:064x}"}
        certificate_payload = {
            "certificate": {
                "snapshot_id": f"snapshot-{boundary}",
                "factual_action_sha256": f"factual-{boundary}",
                "candidate_action_sha256": f"candidate-{boundary}",
                "simulator_model_sha256": "model",
                "task_asset_sha256": "task",
                "engine_identity": "engine",
                "parameter_addresses": [f"geom[{index}]"],
                "evidence_sha256": [left["sha256"], right["sha256"], repeat["sha256"]],
                "static_config_sha256": ["static-left", "static-right"],
                "search_objective_terms": ["realized_contact_support"],
            },
            "measurements": {},
            "failures": [],
        }
        certificate_sha256 = hashlib.sha256(
            json.dumps(certificate_payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        strength = [{
            "left_value": 0.004,
            "right_value": 0.1,
            "left_static_contact_config_sha256": "static-left",
            "right_static_contact_config_sha256": "static-right",
            "measurements": {},
            "certificate_sha256": certificate_sha256,
            "certificate_payload": certificate_payload,
            "left_evidence": left,
            "right_evidence": right,
        }] if passed else []
        witness_fields = {
            "source_trajectory_sha256": f"rollout-{boundary}",
            "arrays_sha256": f"arrays-{boundary}",
            "snapshot_sha256": f"snapshot-{boundary}",
            "factual_action_sha256": f"factual-{boundary}",
            "boundary_step": boundary,
            "candidate_sha256": f"candidate-{boundary}",
            "geom_ids": [index],
            "parameter_family": "compliance",
        }
        witness_key = hashlib.sha256(
            json.dumps(witness_fields, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        blocks.append(
            {
                "certified_endpoint_pairs": passed,
                "attempted_endpoint_pairs": 3,
                "endpoint_strength_curve": strength,
                "unique_witness": passed,
                "witness_key": witness_key,
                "witness_key_fields": witness_fields,
                "geom_ids": [index],
                "repeat_evidence": repeat,
                "endpoint_evidence": {"0.004": left, "0.02": middle, "0.1": right},
                "parameter_metadata": {"engine_field": f"geom[{index}]"},
                "static_diff_schema": {"legal_endpoints": [0.004, 0.02, 0.1]},
            }
        )
    return {
        "kind": "israc_continuous_geom_contact_support_e0",
        "protocol_version": "P025-v5",
        "controller_reset_mode": (
            "fresh_seeded_reset_set_benchmark_init_then_replay_warmup_full_prefix_candidate"
        ),
        "block_selector": selector,
        "selector_seed": seed,
        "rollout_sha256": f"rollout-{boundary}",
        "arrays_sha256": f"arrays-{boundary}",
        "candidate_boundary_step": boundary,
        "candidate_sha256": f"candidate-{boundary}",
        "snapshot_sha256": f"snapshot-{boundary}",
        "factual_action_sha256": f"factual-{boundary}",
        "factual_action_id": f"factual-id-{boundary}",
        "candidate_action_id": f"candidate-id-{boundary}",
        "simulator_model_contact_schema_sha256": "model",
        "task_asset_bddl_sha256": "task",
        "engine_identity": "engine",
        "arguments": {"family": "compliance"},
        "blocks": blocks,
        "baseline_static_evidence": {},
        "selected_block_count": 3,
        "raw_endpoint_pair_count": witnesses,
        "unique_witness_count": witnesses,
        "boundary_eligible": True,
        "invalid_boundary_reasons": [],
        "nominal_continuous_executions": 2,
        "continuous_executions_per_selected_block": 4,
        "factual_action_steps": 8,
        "candidate_action_steps": 32,
        "max_selected_blocks": 3,
        "actual_continuous_executions": 14,
        "actual_simulator_steps": 560,
        "expected_actual_simulator_steps": 560,
        "charged_simulator_step_cap": 560,
        "unused_simulator_step_budget": 0,
    }


class AnalyzeP025Tests(unittest.TestCase):
    def test_schema_counts_are_strict(self) -> None:
        item = record("candidate-contact", 0, 1, 1)
        validate_record(item, allowed_root=None, verify_evidence=False)  # type: ignore[arg-type]
        broken = copy.deepcopy(item)
        broken["raw_endpoint_pair_count"] = 9
        with self.assertRaises(ValueError):
            validate_record(broken, allowed_root=None, verify_evidence=False)  # type: ignore[arg-type]

    def test_duplicate_boundary_key_binds_actions_and_arrays(self) -> None:
        left = record("candidate-contact", 0, 1, 1)
        right = copy.deepcopy(left)
        right["candidate_sha256"] = "other"
        self.assertNotEqual(boundary_key(left), boundary_key(right))

    def test_missing_selector_fails(self) -> None:
        records = []
        for seed in range(3):
            records.append(record("israc-contact-subtraction", seed, 1, 2))
            records.append(record("candidate-contact", seed, 1, 1))
        with self.assertRaises(ValueError):
            analyze(records, [0, 1, 2], bootstrap_samples=100, bootstrap_seed=0)

    def test_cluster_bootstrap_two_x(self) -> None:
        records = []
        for seed in range(3):
            for boundary in (1, 2, 3):
                records.append(record("israc-contact-subtraction", seed, boundary, 2))
                records.append(record("candidate-contact", seed, boundary, 1))
                records.append(record("random-scene", seed, boundary, 0))
        result = analyze(records, [0, 1, 2], bootstrap_samples=500, bootstrap_seed=0)
        self.assertEqual(result["pilot_decision"]["point_yield_ratio"], 2.0)
        self.assertTrue(result["comparisons"]["candidate-contact"]["ci_lower_gt_1"])

    def test_zero_over_zero_is_undefined_not_infinite(self) -> None:
        records = []
        for seed in range(3):
            for selector in (
                "israc-contact-subtraction",
                "candidate-contact",
                "random-scene",
            ):
                records.append(record(selector, seed, 1, 0))
        result = analyze(records, [0, 1, 2], bootstrap_samples=100, bootstrap_seed=0)
        self.assertIsNone(result["pilot_decision"]["point_yield_ratio"])
        self.assertEqual(
            result["comparisons"]["candidate-contact"]["undefined_zero_over_zero_samples"],
            100,
        )


if __name__ == "__main__":
    unittest.main()
