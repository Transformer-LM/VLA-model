"""Print a compact, non-destructive schema summary for a P026 result and rollout."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Any

import numpy as np


def npz_schema(path: Path) -> dict[str, Any]:
    schema: dict[str, Any] = {}
    with zipfile.ZipFile(path) as archive:
        for member in archive.namelist():
            if not member.endswith(".npy"):
                continue
            with archive.open(member) as handle:
                version = np.lib.format.read_magic(handle)
                if version == (1, 0):
                    shape, _, dtype = np.lib.format.read_array_header_1_0(handle)
                else:
                    shape, _, dtype = np.lib.format.read_array_header_2_0(handle)
            schema[member[:-4]] = {"shape": list(shape), "dtype": str(dtype)}
    return schema


def compact(value: Any, depth: int = 0) -> Any:
    if depth >= 3:
        if isinstance(value, dict):
            return {"type": "dict", "keys": sorted(value)[:30], "length": len(value)}
        if isinstance(value, list):
            return {"type": "list", "length": len(value)}
        return value
    if isinstance(value, dict):
        return {key: compact(item, depth + 1) for key, item in value.items()}
    if isinstance(value, list):
        return {
            "type": "list",
            "length": len(value),
            "first": compact(value[0], depth + 1) if value else None,
        }
    if isinstance(value, str) and len(value) > 300:
        return {"type": "str", "length": len(value), "prefix": value[:80]}
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("result")
    args = parser.parse_args()

    result_path = Path(args.result).resolve(strict=True)
    result = json.loads(result_path.read_text(encoding="utf-8"))
    rollout_path = Path(result["rollout"]).resolve(strict=True)
    rollout = json.loads(rollout_path.read_text(encoding="utf-8"))
    arrays_path = Path(rollout["arrays"]).resolve(strict=True)
    with np.load(arrays_path) as arrays:
        array_schema = {
            key: {"shape": list(arrays[key].shape), "dtype": str(arrays[key].dtype)}
            for key in arrays.files
        }

    selected_result = {
        key: value
        for key, value in result.items()
        if key not in {
            "arguments",
            "baseline_static_field_sha256",
            "contact_topology",
        }
    }
    evidence_schema: dict[str, Any] = {}
    for block in result.get("blocks", []):
        for endpoint, record in block.get("endpoint_evidence", {}).items():
            evidence_path = Path(record["path"]).resolve(strict=True)
            evidence_schema[f"{block['parameter_address']}@{endpoint}"] = {
                "path": str(evidence_path),
                "sha256": record["sha256"],
                "arrays": npz_schema(evidence_path),
            }
    payload = {
        "result_path": str(result_path),
        "result": compact(selected_result),
        "rollout_path": str(rollout_path),
        "rollout": compact(rollout),
        "arrays_path": str(arrays_path),
        "arrays": array_schema,
        "endpoint_evidence": evidence_schema,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
