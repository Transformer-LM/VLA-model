from __future__ import annotations

import unittest
import hashlib
from pathlib import Path
import tempfile
from dataclasses import asdict

from certify_continuous_contact_support import FAMILY_VALUES, parameter
from verify_p025_manifest import (
    validate_derived_pair_accounting,
    validate_selected_block_rows,
    verify_protocol_amendments,
)


def block(keys, failures):
    return {
        "endpoint_strength_curve": [
            {"left_value": left, "right_value": right} for left, right in keys
        ],
        "certified_endpoint_pairs": len(keys),
        "unique_witness": int(bool(keys)),
        "failure_reason_counts": dict(sorted(failures.items())),
    }


class CompletePairAccountingTests(unittest.TestCase):
    def test_honest_all_failed_block_is_accepted(self) -> None:
        validate_derived_pair_accounting(
            block([], {"candidate_has_no_physical_divergence": 3}),
            [],
            {"candidate_has_no_physical_divergence": 3},
        )

    def test_deleted_true_passing_pair_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "passing endpoint set"):
            validate_derived_pair_accounting(
                block([], {"candidate_has_no_physical_divergence": 3}),
                [(0.004, 0.02)],
                {"candidate_has_no_physical_divergence": 2},
            )

    def test_both_amendments_are_hash_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            v1 = root / "P026_PROTOCOL_AMENDMENT.md"
            v2 = root / "P026_PROTOCOL_AMENDMENT_V2.md"
            v1.write_text("v1 disclosure", encoding="utf-8")
            v1_sha = hashlib.sha256(v1.read_bytes()).hexdigest()
            v2.write_text(f"v2 disclosure predecessor={v1_sha}", encoding="utf-8")

            def digest(path: Path) -> str:
                return hashlib.sha256(path.read_bytes()).hexdigest()

            lock = {
                "protocol_amendments": [
                    {"version": "v1", "path": str(v1), "sha256": digest(v1)},
                    {
                        "version": "v2", "path": str(v2), "sha256": digest(v2),
                        "predecessor_sha256": digest(v1),
                    },
                ]
            }
            self.assertEqual(verify_protocol_amendments(lock, root), 2)
            v1.write_text("mutated", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "v1 changed"):
                verify_protocol_amendments(lock, root)

    def test_amendment_version_or_reference_swap_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            v1 = root / "P026_PROTOCOL_AMENDMENT.md"
            v2 = root / "P026_PROTOCOL_AMENDMENT_V2.md"
            v1.write_text("v1", encoding="utf-8")
            v2.write_text("v2", encoding="utf-8")
            lock = {
                "protocol_amendments": [
                    {"version": "v2", "path": str(v1), "sha256": "0" * 64},
                    {"version": "v1", "path": str(v2), "sha256": "0" * 64},
                ]
            }
            with self.assertRaisesRegex(ValueError, "exact v1/v2"):
                verify_protocol_amendments(lock, root)

    def test_duplicate_amendment_reference_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            v2 = root / "P026_PROTOCOL_AMENDMENT_V2.md"
            v2.write_text("same", encoding="utf-8")
            digest = hashlib.sha256(v2.read_bytes()).hexdigest()
            lock = {"protocol_amendments": [
                {"version": "v1", "path": str(v2), "sha256": digest},
                {
                    "version": "v2", "path": str(v2), "sha256": digest,
                    "predecessor_sha256": digest,
                },
            ]}
            with self.assertRaisesRegex(ValueError, "aliased"):
                verify_protocol_amendments(lock, root)

    def selector_record(self, selected):
        family = "compliance"
        legal = FAMILY_VALUES[family]
        rows = []
        for address, geom_ids in selected:
            block_id = f"candidate-contact_{family}:{address}"
            rows.append({
                "parameter_address": address,
                "geom_ids": list(geom_ids),
                "parameter_metadata": asdict(
                    parameter(block_id, geom_ids, legal[0], family, legal)
                ),
            })
        return {
            "block_selector": "candidate-contact",
            "arguments": {"family": family},
            "selector_visible_pool_count": 4,
            "selected_block_count": len(rows),
            "blocks": rows,
        }

    def test_deleted_selected_block_is_rejected(self) -> None:
        selected = [("geom:2:a", (2,)), ("geom:5:b", (5,))]
        record = self.selector_record(selected)
        record["blocks"] = record["blocks"][:1]
        record["selected_block_count"] = 1
        with self.assertRaisesRegex(ValueError, "selected block count"):
            validate_selected_block_rows(record, selected, 4)

    def test_all_selected_blocks_deleted_is_rejected(self) -> None:
        selected = [("geom:2:a", (2,)), ("geom:5:b", (5,))]
        record = self.selector_record(selected)
        record["blocks"] = []
        record["selected_block_count"] = 0
        with self.assertRaisesRegex(ValueError, "selected block count"):
            validate_selected_block_rows(record, selected, 4)

    def test_selected_block_order_change_is_rejected(self) -> None:
        selected = [("geom:2:a", (2,)), ("geom:5:b", (5,))]
        record = self.selector_record(selected)
        record["blocks"].reverse()
        with self.assertRaisesRegex(ValueError, "block list/order"):
            validate_selected_block_rows(record, selected, 4)

    def test_fabricated_passing_pair_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "passing endpoint set"):
            validate_derived_pair_accounting(
                block([(0.004, 0.02)], {"candidate_has_no_physical_divergence": 2}),
                [],
                {"candidate_has_no_physical_divergence": 3},
            )


if __name__ == "__main__":
    unittest.main()
