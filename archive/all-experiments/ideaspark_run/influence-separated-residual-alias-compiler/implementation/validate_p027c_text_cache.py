#!/usr/bin/env python3
"""Validate and lock the P027-C LIBERO text-embedding cache."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path

import torch


PERSONAL_ROOT = Path("<PERSONAL_RESEARCH_ROOT>").resolve()
PROMPT_TEMPLATE = "A video recorded from a robot's point of view executing the following instruction: {task}"
CONTEXT_LEN = 128
CONTEXT_DIM = 4096
ENCODER_ID = "wan22ti2v5b"


def _personal(path: Path, label: str) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(PERSONAL_ROOT)
    except ValueError as exc:
        raise ValueError(f"{label} must stay under {PERSONAL_ROOT}: {resolved}") from exc
    return resolved


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _prompts(dataset_dirs: list[Path]) -> list[str]:
    prompts: set[str] = set()
    for dataset_dir in dataset_dirs:
        tasks_path = dataset_dir / "meta" / "tasks.jsonl"
        if not tasks_path.is_file():
            raise FileNotFoundError(tasks_path)
        for line_number, line in enumerate(tasks_path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            if "task" not in record:
                raise KeyError(f"Missing task at {tasks_path}:{line_number}")
            prompts.add(PROMPT_TEMPLATE.format(task=str(record["task"])))
    return sorted(prompts)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", type=Path, action="append", required=True)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    dataset_dirs = [_personal(path, "dataset_dir") for path in args.dataset_dir]
    cache_dir = _personal(args.cache_dir, "cache_dir")
    manifest_path = _personal(args.manifest, "manifest")
    if manifest_path.exists():
        raise FileExistsError(f"Refusing to overwrite locked manifest: {manifest_path}")
    prompts = _prompts(dataset_dirs)
    if len(prompts) != 40:
        raise ValueError(f"Expected 40 unique LIBERO prompts, found {len(prompts)}")

    expected: dict[str, str] = {}
    records = []
    for prompt in prompts:
        prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        name = f"{prompt_hash}.t5_len{CONTEXT_LEN}.{ENCODER_ID}.pt"
        expected[name] = prompt_hash
        cache_path = cache_dir / name
        if not cache_path.is_file():
            raise FileNotFoundError(cache_path)
        payload = torch.load(cache_path, map_location="cpu", weights_only=True)
        if not isinstance(payload, dict) or set(payload) != {"context", "mask"}:
            raise ValueError(f"Unexpected payload keys in {cache_path}: {sorted(payload) if isinstance(payload, dict) else type(payload)}")
        context, mask = payload["context"], payload["mask"]
        if tuple(context.shape) != (CONTEXT_LEN, CONTEXT_DIM):
            raise ValueError(f"Wrong context shape in {cache_path}: {tuple(context.shape)}")
        if tuple(mask.shape) != (CONTEXT_LEN,):
            raise ValueError(f"Wrong mask shape in {cache_path}: {tuple(mask.shape)}")
        if context.dtype != torch.bfloat16 or mask.dtype != torch.bool:
            raise TypeError(f"Wrong dtypes in {cache_path}: {context.dtype}, {mask.dtype}")
        if not bool(torch.isfinite(context.float()).all().item()):
            raise ValueError(f"Non-finite context in {cache_path}")
        if not bool(mask.any().item()):
            raise ValueError(f"Empty token mask in {cache_path}")
        records.append({"name": name, "sha256": _sha256(cache_path), "bytes": cache_path.stat().st_size})

    actual_names = {item.name for item in cache_dir.glob("*.pt")}
    extra = sorted(actual_names - set(expected))
    missing = sorted(set(expected) - actual_names)
    if extra or missing:
        raise ValueError(f"Cache membership mismatch: missing={missing}, extra={extra}")

    total_bytes = sum(int(item["bytes"]) for item in records)
    if not math.isfinite(float(total_bytes)) or total_bytes <= 0:
        raise ValueError("Invalid total cache size")
    manifest = {
        "protocol": "P027C-LIBERO-TEXT-CACHE-v1",
        "cache_dir": str(cache_dir),
        "dataset_dirs": [str(path) for path in dataset_dirs],
        "prompt_count": len(prompts),
        "context_shape": [CONTEXT_LEN, CONTEXT_DIM],
        "context_dtype": "torch.bfloat16",
        "mask_dtype": "torch.bool",
        "total_bytes": total_bytes,
        "records": records,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = manifest_path.with_name(f".{manifest_path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, manifest_path)
    print(json.dumps({key: value for key, value in manifest.items() if key != "records"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
