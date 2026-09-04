import argparse
import json
from pathlib import Path

import torch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("reference")
    parser.add_argument("candidate")
    parser.add_argument("--output")
    args = parser.parse_args()

    reference = torch.load(args.reference, map_location="cpu", weights_only=True)
    candidate = torch.load(args.candidate, map_location="cpu", weights_only=True)
    reference_state = reference["state_dict"]
    candidate_state = candidate["state_dict"]
    if set(reference_state) != set(candidate_state):
        raise RuntimeError(
            f"Checkpoint tensor names differ: reference={sorted(reference_state)} "
            f"candidate={sorted(candidate_state)}"
        )

    tensors = {}
    for name in sorted(reference_state):
        before = reference_state[name].float()
        after = candidate_state[name].float()
        if before.shape != after.shape:
            raise RuntimeError(f"Shape mismatch for {name}: {before.shape} vs {after.shape}")
        delta = after - before
        base_l2 = float(before.norm().item())
        delta_l2 = float(delta.norm().item())
        tensors[name] = {
            "shape": list(before.shape),
            "numel": int(before.numel()),
            "base_l2": base_l2,
            "candidate_l2": float(after.norm().item()),
            "delta_l2": delta_l2,
            "relative_delta_l2": delta_l2 / max(base_l2, 1e-12),
            "delta_abs_max": float(delta.abs().max().item()),
            "changed_numel": int((delta != 0).sum().item()),
        }

    payload = {
        "reference": {
            "path": str(Path(args.reference).resolve()),
            "format": reference.get("format"),
            "global_step": int(reference.get("global_step", -1)),
            "trainable_numel": int(reference.get("trainable_numel", -1)),
        },
        "candidate": {
            "path": str(Path(args.candidate).resolve()),
            "format": candidate.get("format"),
            "global_step": int(candidate.get("global_step", -1)),
            "trainable_numel": int(candidate.get("trainable_numel", -1)),
        },
        "tensor_count": len(tensors),
        "tensors": tensors,
    }
    rendered = json.dumps(payload, ensure_ascii=True, indent=2)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
