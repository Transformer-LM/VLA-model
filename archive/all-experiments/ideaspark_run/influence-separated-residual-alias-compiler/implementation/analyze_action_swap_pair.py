import argparse
import json
import math
import random
import statistics
from pathlib import Path


def mean(values):
    return sum(values) / len(values)


def bootstrap_mean_ci(values, *, samples=50_000, seed=2701, alpha=0.05):
    rng = random.Random(seed)
    n = len(values)
    estimates = sorted(mean([values[rng.randrange(n)] for _ in range(n)]) for _ in range(samples))
    lo = estimates[int((alpha / 2) * samples)]
    hi = estimates[min(int((1 - alpha / 2) * samples), samples - 1)]
    return lo, hi


def exact_two_sided_sign_p(positive, negative):
    n = positive + negative
    if n == 0:
        return 1.0
    tail = min(positive, negative)
    lower = sum(math.comb(n, k) for k in range(tail + 1)) / (2**n)
    return min(1.0, 2.0 * lower)


def pearson(x, y):
    mx, my = mean(x), mean(y)
    dx = [value - mx for value in x]
    dy = [value - my for value in y]
    denom = math.sqrt(sum(value * value for value in dx) * sum(value * value for value in dy))
    if denom == 0:
        return 0.0
    return sum(a * b for a, b in zip(dx, dy)) / denom


def summarize(values):
    lo, hi = bootstrap_mean_ci(values)
    std = statistics.stdev(values) if len(values) > 1 else 0.0
    return {
        "n": len(values),
        "mean": mean(values),
        "std": std,
        "median": statistics.median(values),
        "bootstrap_95_ci": [lo, hi],
        "positive_rate": sum(value > 0 for value in values) / len(values),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("base")
    parser.add_argument("checkpoint")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    base = json.loads(Path(args.base).read_text(encoding="utf-8"))
    checkpoint = json.loads(Path(args.checkpoint).read_text(encoding="utf-8"))
    base_rows = {int(row["eval_index"]): row for row in base["rows"]}
    checkpoint_rows = {int(row["eval_index"]): row for row in checkpoint["rows"]}
    if set(base_rows) != set(checkpoint_rows):
        raise RuntimeError("Base/checkpoint eval indices differ.")

    rows = []
    for eval_index in sorted(base_rows):
        before = base_rows[eval_index]
        after = checkpoint_rows[eval_index]
        if not math.isclose(before["action_mse"], after["action_mse"], rel_tol=0.0, abs_tol=0.0):
            raise RuntimeError(f"Action negative changed at eval_index={eval_index}.")
        rows.append(
            {
                "eval_index": eval_index,
                "action_mse": before["action_mse"],
                "base_factual": before["factual_video_loss"],
                "base_swapped": before["swapped_video_loss"],
                "base_margin": before["margin"],
                "checkpoint_factual": after["factual_video_loss"],
                "checkpoint_swapped": after["swapped_video_loss"],
                "checkpoint_margin": after["margin"],
                "delta_factual_loss": after["factual_video_loss"] - before["factual_video_loss"],
                "delta_swapped_loss": after["swapped_video_loss"] - before["swapped_video_loss"],
                "delta_margin": after["margin"] - before["margin"],
            }
        )

    base_margins = [row["base_margin"] for row in rows]
    checkpoint_margins = [row["checkpoint_margin"] for row in rows]
    delta_margins = [row["delta_margin"] for row in rows]
    factual_deltas = [row["delta_factual_loss"] for row in rows]
    swapped_deltas = [row["delta_swapped_loss"] for row in rows]
    action_mse = [row["action_mse"] for row in rows]
    positive = sum(value > 0 for value in delta_margins)
    negative = sum(value < 0 for value in delta_margins)
    delta_std = statistics.stdev(delta_margins) if len(delta_margins) > 1 else 0.0

    payload = {
        "base_source": base.get("source"),
        "checkpoint_source": checkpoint.get("source"),
        "paired_integrity": {
            "same_eval_indices": True,
            "same_action_mse": True,
            "num_pairs": len(rows),
        },
        "base_margin": summarize(base_margins),
        "checkpoint_margin": summarize(checkpoint_margins),
        "paired_delta_margin": {
            **summarize(delta_margins),
            "cohens_dz": mean(delta_margins) / delta_std if delta_std > 0 else 0.0,
            "positive_count": positive,
            "negative_count": negative,
            "zero_count": len(delta_margins) - positive - negative,
            "exact_two_sided_sign_p": exact_two_sided_sign_p(positive, negative),
        },
        "paired_delta_factual_loss": summarize(factual_deltas),
        "paired_delta_swapped_loss": summarize(swapped_deltas),
        "correlations": {
            "action_mse_vs_base_margin": pearson(action_mse, base_margins),
            "action_mse_vs_checkpoint_margin": pearson(action_mse, checkpoint_margins),
            "action_mse_vs_delta_margin": pearson(action_mse, delta_margins),
        },
        "rows": rows,
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in payload.items() if key != "rows"}, indent=2))


if __name__ == "__main__":
    main()
