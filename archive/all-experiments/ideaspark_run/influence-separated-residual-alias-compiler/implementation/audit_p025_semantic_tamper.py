#!/usr/bin/env python3
"""Adversarial end-to-end audit for one real P025-v5 artifact."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
from typing import Any, Callable

import numpy as np

from analyze_p025_fixed_budget import load_records, sha256_file


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def copy_case(source: Path, case_dir: Path) -> tuple[Path, dict[str, Any]]:
    manifest = json.loads(source.read_text(encoding="utf-8"))
    source_evidence = source.with_suffix(source.suffix + ".evidence")
    case_dir.mkdir(parents=False)
    target_evidence = case_dir / source_evidence.name
    shutil.copytree(source_evidence, target_evidence)

    def rewrite(value: Any) -> None:
        if isinstance(value, dict):
            if "path" in value and "sha256" in value:
                old = Path(str(value["path"]))
                if old.parent.resolve() == source_evidence.resolve():
                    value["path"] = str(target_evidence / old.name)
            for item in value.values():
                rewrite(item)
        elif isinstance(value, list):
            for item in value:
                rewrite(item)

    rewrite(manifest)
    target_manifest = case_dir / source.name
    atomic_json(target_manifest, manifest)
    return target_manifest, manifest


def mutate_npz(path: Path, mutation: Callable[[dict[str, np.ndarray]], None]) -> None:
    with np.load(path, allow_pickle=False) as archive:
        arrays = {name: np.asarray(archive[name]).copy() for name in archive.files}
    mutation(arrays)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        np.savez_compressed(handle, **arrays)
    os.replace(temporary, path)


def rebind_certificates(manifest: dict[str, Any], changed_path: Path) -> None:
    digest = sha256_file(changed_path)

    def update_reference(value: Any) -> None:
        if isinstance(value, dict):
            if value.get("path") == str(changed_path) and "sha256" in value:
                value["sha256"] = digest
            for item in value.values():
                update_reference(item)
        elif isinstance(value, list):
            for item in value:
                update_reference(item)

    update_reference(manifest)
    for block in manifest["blocks"]:
        for pair in block["endpoint_strength_curve"]:
            payload = pair["certificate_payload"]
            payload["certificate"]["evidence_sha256"] = [
                pair["left_evidence"]["sha256"],
                pair["right_evidence"]["sha256"],
                block["repeat_evidence"]["sha256"],
            ]
            canonical = json.dumps(
                payload, sort_keys=True, separators=(",", ":"), allow_nan=False
            )
            pair["certificate_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()


def first_passing_evidence(manifest: dict[str, Any]) -> Path:
    for block in manifest["blocks"]:
        for pair in block["endpoint_strength_curve"]:
            return Path(pair["left_evidence"]["path"])
    raise ValueError("tamper audit requires a passing certificate")


def copy_source_rollout(
    manifest: dict[str, Any], case_dir: Path, *, copy_arrays: bool = False
) -> tuple[Path, dict[str, Any], Path | None]:
    source_path = Path(str(manifest["rollout"])).resolve()
    source_value = json.loads(source_path.read_text(encoding="utf-8"))
    copied_arrays: Path | None = None
    if copy_arrays:
        original_arrays = Path(str(source_value["arrays"])).resolve()
        copied_arrays = case_dir / original_arrays.name
        shutil.copy2(original_arrays, copied_arrays)
        source_value["arrays"] = str(copied_arrays)
    copied_source = case_dir / source_path.name
    atomic_json(copied_source, source_value)
    manifest["rollout"] = str(copied_source)
    return copied_source, source_value, copied_arrays


def bind_source_manifest(manifest: dict[str, Any], path: Path) -> None:
    manifest["rollout_sha256"] = sha256_file(path)


def expect_rejected(manifest_path: Path, root: Path) -> str:
    try:
        load_records(str(manifest_path), root, verify_evidence=True)
    except Exception as error:
        return f"{type(error).__name__}: {error}"
    raise AssertionError(f"tampered artifact was accepted: {manifest_path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    root = Path("<PERSONAL_RESEARCH_ROOT>").resolve()
    source = Path(args.manifest).resolve()
    output = Path(args.output_dir).resolve()
    if output == root or root not in output.parents or output.exists():
        raise ValueError("unsafe or existing tamper audit output")

    valid = load_records(str(source), root, verify_evidence=True)
    if len(valid) != 1:
        raise AssertionError("valid source did not pass formal loader")
    results: dict[str, str] = {}

    cases: dict[str, Callable[[dict[str, np.ndarray]], None]] = {
        "raw_pixel": lambda arrays: arrays["factual_rgb"].reshape(-1).__setitem__(
            0, int(arrays["factual_rgb"].reshape(-1)[0]) ^ 1
        ),
        "contact_activation": lambda arrays: arrays["candidate_active"].__setitem__(
            6, not bool(arrays["candidate_active"][6])
        ),
        "factual_t0_proprio": lambda arrays: arrays["factual_t0_proprio"].__setitem__(
            0, float(arrays["factual_t0_proprio"][0]) + 0.25
        ),
    }
    output.mkdir(parents=False)
    for name, mutation in cases.items():
        case_manifest_path, manifest = copy_case(source, output / name)
        evidence = first_passing_evidence(manifest)
        mutate_npz(evidence, mutation)
        rebind_certificates(manifest, evidence)
        atomic_json(case_manifest_path, manifest)
        results[name] = expect_rejected(case_manifest_path, root)

    case_manifest_path, manifest = copy_case(source, output / "certificate_measurement")
    pair = manifest["blocks"][0]["endpoint_strength_curve"][0]
    pair["measurements"]["candidate_task_effect_max_abs"] += 1.0
    pair["certificate_payload"]["measurements"]["candidate_task_effect_max_abs"] += 1.0
    canonical = json.dumps(
        pair["certificate_payload"], sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    pair["certificate_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    atomic_json(case_manifest_path, manifest)
    results["certificate_measurement"] = expect_rejected(case_manifest_path, root)

    case_manifest_path, manifest = copy_case(source, output / "static_non_target")
    evidence = first_passing_evidence(manifest)
    target_field = manifest["blocks"][0]["static_diff_schema"]["array"]

    def mutate_static(arrays: dict[str, np.ndarray]) -> None:
        names = [str(value) for value in arrays["static_field_names"].tolist()]
        index = next(
            i
            for i, name in enumerate(names)
            if name != target_field
            and arrays[f"static_field_{i:05d}"].dtype.kind in "iufc"
            and arrays[f"static_field_{i:05d}"].size
        )
        key = f"static_field_{index:05d}"
        flat = arrays[key].reshape(-1)
        flat[0] = flat[0] + 1

    mutate_npz(evidence, mutate_static)
    rebind_certificates(manifest, evidence)
    atomic_json(case_manifest_path, manifest)
    results["static_non_target"] = expect_rejected(case_manifest_path, root)

    # Provenance attacks: the verifier must authenticate the natural-success
    # source itself, not merely trust source hashes copied into raw evidence.
    case_manifest_path, manifest = copy_case(source, output / "source_rollout_unhashed")
    copied_source, source_value, _ = copy_source_rollout(
        manifest, case_manifest_path.parent
    )
    source_value["instruction"] = str(source_value["instruction"]) + " tampered"
    atomic_json(copied_source, source_value)
    # Deliberately retain the old rollout_sha256.
    atomic_json(case_manifest_path, manifest)
    results["source_rollout_unhashed"] = expect_rejected(case_manifest_path, root)

    case_manifest_path, manifest = copy_case(source, output / "source_success_flag")
    copied_source, source_value, _ = copy_source_rollout(
        manifest, case_manifest_path.parent
    )
    source_value["done"] = False
    atomic_json(copied_source, source_value)
    bind_source_manifest(manifest, copied_source)
    atomic_json(case_manifest_path, manifest)
    results["source_success_flag"] = expect_rejected(case_manifest_path, root)

    case_manifest_path, manifest = copy_case(source, output / "source_action_chunk")
    copied_source, source_value, copied_arrays = copy_source_rollout(
        manifest, case_manifest_path.parent, copy_arrays=True
    )
    assert copied_arrays is not None
    mutate_npz(
        copied_arrays,
        lambda arrays: arrays["action_chunks"].__setitem__(
            (0, 0, 0), float(arrays["action_chunks"][0, 0, 0]) + 0.125
        ),
    )
    manifest["arrays_sha256"] = sha256_file(copied_arrays)
    atomic_json(copied_source, source_value)
    bind_source_manifest(manifest, copied_source)
    atomic_json(case_manifest_path, manifest)
    results["source_action_chunk"] = expect_rejected(case_manifest_path, root)

    case_manifest_path, manifest = copy_case(source, output / "source_initialization")
    copied_source, source_value, _ = copy_source_rollout(
        manifest, case_manifest_path.parent
    )
    source_value["initialization"]["source"] = "direct_bddl_reset"
    atomic_json(copied_source, source_value)
    bind_source_manifest(manifest, copied_source)
    atomic_json(case_manifest_path, manifest)
    results["source_initialization"] = expect_rejected(case_manifest_path, root)

    case_manifest_path, manifest = copy_case(source, output / "controller_reset_mode")
    manifest["controller_reset_mode"] = "intermediate_state_restore"
    atomic_json(case_manifest_path, manifest)
    results["controller_reset_mode"] = expect_rejected(case_manifest_path, root)

    summary = {
        "kind": "p025_v5_semantic_tamper_audit",
        "source_manifest": str(source),
        "source_manifest_sha256": sha256_file(source),
        "formal_valid_source_passed": True,
        "expected_rejection_count": len(results),
        "all_tampers_rejected": len(results) == 10,
        "rejections": results,
    }
    atomic_json(output / "AUDIT.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
